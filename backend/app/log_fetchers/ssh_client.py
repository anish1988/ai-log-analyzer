"""
asyncssh-based remote grep. One command per (server, path candidate) that
searches for every filter term at once, rather than one SSH round-trip per
field - this is what keeps a multi-field search (lead_id + campaign_id +
agent, etc) fast across several telephony servers.

A missing file is not an error: `test -f ... || true` makes the command
resolve to an empty result so the caller can move on to the next path
candidate (gz -> dated -> undated).
"""
import asyncio
import os
import re
import shlex

import asyncssh

from app.config.servers import ServerConfig
from app.log_fetchers.path_resolver import ResolvedLogPath
import logging
from app.log_fetchers.log_paths import (
    REMOTE_LOG_PATHS,
)

logger = logging.getLogger(__name__)
_connection_pool: dict[str, asyncssh.SSHClientConnection] = {}
_pool_lock = asyncio.Lock()

# TODO: pull from a secret store, not a bare env var pointing at a key on disk.
SSH_KEY_PATH = os.environ.get("LOG_ANALYZER_SSH_KEY_PATH", "/secrets/id_rsa")


async def _get_connection_old(server: ServerConfig) -> asyncssh.SSHClientConnection:
    async with _pool_lock:
        conn = _connection_pool.get(server.id)
        if conn is not None and not conn.is_closed():
            return conn
        print("=" * 80)
        print("Creating SSH Connection")
        print(f"Server Name      : {server.id}")
        print(f"Server IP        : {server.ip}")
        print(f"Server Port      : {server.ssh_port}")
        print(f"Username         : {server.ssh_user}")
       # print(f"SSH Key          : {server.private_key}")
       # print(f"Known Hosts      : {server.known_hosts}")
        print("=" * 80)
        conn = await asyncssh.connect(
            host=server.ip,
            port=server.ssh_port,
            username=server.ssh_user,
            client_keys=[SSH_KEY_PATH],
            known_hosts=None,  # TODO: pin known_hosts in production
        )
        print("=" * 80)
        print("✅ SSH CONNECTION ESTABLISHED SUCCESSFULLY")
        print(f"Connected Server : {server.id}")
        print(f"Server IP        : {server.ip}")
        print(f"SSH User         : {server.ssh_user}")
        print("Authentication   : SUCCESS")
        print("Mode             : Remote Server")
        print("Next Step        : Fetching log data from the remote server...")
        print("=" * 80)
        _connection_pool[server.id] = conn
        return conn


async def _get_connection(server: ServerConfig) -> asyncssh.SSHClientConnection:
    print("=" * 80)
    print("Creating NEW SSH Connection")
    print(f"Server Name : {server.id}")
    print(f"Server IP   : {server.ip}")
    print(f"Server Port : {server.ssh_port}")
    print(f"Username    : {server.ssh_user}")
    print("=" * 80)

    conn = await asyncssh.connect(
        host=server.ip,
        port=server.ssh_port,
        username=server.ssh_user,
        client_keys=[SSH_KEY_PATH],
        known_hosts=None,
    )

    print("=" * 80)
    print("✅ NEW SSH CONNECTION ESTABLISHED")
    print(f"Connection Object : {conn}")
    print("=" * 80)

    return conn

def _escape_for_grep(value: str) -> str:
    return re.sub(r"([.*+?^${}()|\[\]\\])", r"\\\1", value)


async def search_remote_file(
    server: ServerConfig,
    candidate: ResolvedLogPath,
    search_terms: list[tuple[str, str]],  # (field_key, value)
) -> list[dict]:
    print("\n" + "=" * 100)
    print("REMOTE LOG SEARCH STARTED")
    print("=" * 100)
    print(f"Server           : {server.id}")
    print(f"Server IP        : {server.ip}")
    print(f"SSH User         : {server.ssh_user}")
    print(f"Log File         : {candidate.service}/{candidate.filename}")
    print(f"Gzipped File     : {candidate.is_gzipped}")
    print("=" * 100)

    print("Step 1 : Establishing SSH connection...")
    conn = await _get_connection(server)

    print("✅ SSH connection established successfully.")
    print("Now reading logs from the REMOTE SERVER.")
    print()
    print("=" * 100)
    print("REMOTE SEARCH")
    print("=" * 100)
    print(f"Server     : {server.id}")
    print(f"Service    : {candidate.service}")
    print(f"Filename   : {candidate.filename}")
    print(f"Gzipped    : {candidate.is_gzipped}")
    print(f"Dated      : {candidate.is_dated}")
    print("=" * 100)

    pattern = "|".join(_escape_for_grep(value) for _, value in search_terms)

    print("Step 2 : Preparing search pattern...")
    print(f"Search Pattern : {pattern}")

    reader = "zcat" if candidate.is_gzipped else "cat"

    print(f"Reader Command : {reader}")

   

   
    candidate_paths = []

    for directory in REMOTE_LOG_PATHS.get(candidate.service, []):

        filename = candidate.filename

        #
        # httpd uses underscore
        #
        if "httpd" in directory:

            filename = (
                filename
                .replace("access.log", "access_log")
                .replace("error.log", "error_log")
            )

        candidate_paths.append(f"{directory}/{filename}")

    print("\nCandidate Paths")

    for p in candidate_paths:
        print(" ->", p)
   
    quoted_pattern = shlex.quote(pattern)

    
    # -n keeps line numbers (needed for the dedupe key), -E for a plain OR of terms.
    stdout = ""
    selected_path = None

    for path in candidate_paths:

        logger.info("=" * 80)
        logger.info("SSH CLIENT")
        logger.info(f"Candidate filename : {candidate.filename}")
        logger.info(f"Candidate service  : {candidate.service}")
        logger.info(f"Dated             : {candidate.is_dated}")
        logger.info(f"Gzipped           : {candidate.is_gzipped}")
        logger.info("=" * 80)
        quoted_path = shlex.quote(path)

        command = f"""
        echo "PATH={quoted_path}"
        if test -f {quoted_path}; then
            echo "FILE EXISTS"
            {reader} {quoted_path} | grep -nE {quoted_pattern}
        else
            echo "FILE NOT FOUND"
        fi
        """
        print("\nTrying:", path)
        print(command)

        print("Connection object:", conn)
        print("Connection is None:", conn is None)

        #result = await conn.run(command, check=False)

        try:
            result = await conn.run(command, check=False)
            print("HOSTNAME:", result.stdout)
        except Exception as e:
            print("HOSTNAME TEST FAILED:", repr(e))
            print("=" * 80)
            print("COMMAND TO EXECUTE")
            print(command)
            print("=" * 80)

            print("COMMAND LENGTH:", len(command))
            print("EXCEPTION TYPE:", type(e).__name__)
            print("EXCEPTION:", repr(e))

            raise

        if result.stdout.strip():
            print("\nNo output returned.")

            print("Possible reasons:")
            print(f"• File not found            : {path}")
            print("• File exists but no matching lines")
            print("• File is empty")
            print("• Permission denied")
            print("• Search pattern not present")

            print("=" * 100)
            stdout = result.stdout
            selected_path = path

            logger.info(f"[SSH] Service={candidate.service}, File={candidate.filename}, Path={selected_path}")
            print(f"✅ Using {selected_path}")

            break

    if not selected_path:

        print("❌ No matching log file found.")

        return []

    lines: list[dict] = []
    print("=" * 100)
    print("Matched File :", selected_path)
    print("Matched Lines:", len(stdout.splitlines()))
    print("=" * 100)
    for entry in stdout.splitlines():
        if not entry:
            continue
        line_number_raw, _, raw = entry.partition(":")
        matched_filters = [key for key, value in search_terms if value in raw]
        lines.append({
            "server": server.id,
            "file": selected_path,
            "file_id": selected_path,
            "line_number": int(line_number_raw) if line_number_raw.isdigit() else 0,
            "raw": raw,
            "matched_filters": matched_filters,
        })

        print()
        print("=" * 100)
        print("REMOTE FILE PROCESSING COMPLETED")
        print("=" * 100)
        print(f"Server           : {server.id}")
        print(f"File             : {path}")
        print(f"Matched Lines    : {len(lines)}")
        print("Returning results to log_analysis_service()")
        print("=" * 100)
    return lines


async def close_all_connections() -> None:
    """Call on app shutdown to close pooled SSH connections cleanly."""
    async with _pool_lock:
        for conn in _connection_pool.values():
            conn.close()
        _connection_pool.clear()