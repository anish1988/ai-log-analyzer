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

_connection_pool: dict[str, asyncssh.SSHClientConnection] = {}
_pool_lock = asyncio.Lock()

# TODO: pull from a secret store, not a bare env var pointing at a key on disk.
SSH_KEY_PATH = os.environ.get("LOG_ANALYZER_SSH_KEY_PATH", "/etc/log-analyzer/ssh/deploy_key")


async def _get_connection(server: ServerConfig) -> asyncssh.SSHClientConnection:
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
        _connection_pool[server.id] = conn
        return conn


def _escape_for_grep(value: str) -> str:
    return re.sub(r"([.*+?^${}()|\[\]\\])", r"\\\1", value)

import gzip
import re
from pathlib import Path

async def search_local_file(
    server: ServerConfig,
    candidate: ResolvedLogPath,
    search_terms: list[tuple[str, str]],
) -> list[dict]:

    path = Path(candidate.path)

    if not path.exists():
        return []

    pattern = re.compile("|".join(re.escape(value) for _, value in search_terms))

    opener = gzip.open if candidate.is_gzipped else open

    lines: list[dict] = []

    with opener(path, "rt", encoding="utf-8", errors="ignore") as f:
        for line_number, raw in enumerate(f, start=1):

            if not pattern.search(raw):
                continue

            matched_filters = [
                key
                for key, value in search_terms
                if value in raw
            ]

            lines.append(
                {
                    "server": server.id,
                    "file": candidate.path,
                    "file_id": candidate.path,
                    "line_number": line_number,
                    "raw": raw.rstrip("\n"),
                    "matched_filters": matched_filters,
                }
            )

    return lines
async def search_remote_file(
    server: ServerConfig,
    candidate: ResolvedLogPath,
    search_terms: list[tuple[str, str]],  # (field_key, value)
) -> list[dict]:
    conn = await _get_connection(server)

    pattern = "|".join(_escape_for_grep(value) for _, value in search_terms)
    reader = "zcat" if candidate.is_gzipped else "cat"
    quoted_path = shlex.quote(candidate.path)
    quoted_pattern = shlex.quote(pattern)

    # -n keeps line numbers (needed for the dedupe key), -E for a plain OR of terms.
    command = f"test -f {quoted_path} && {reader} {quoted_path} | grep -nE {quoted_pattern} || true"

    result = await conn.run(command, check=False)
    stdout = result.stdout or ""
    if not stdout.strip():
        return []

    lines: list[dict] = []
    for entry in stdout.splitlines():
        if not entry:
            continue
        line_number_raw, _, raw = entry.partition(":")
        matched_filters = [key for key, value in search_terms if value in raw]
        lines.append({
            "server": server.id,
            "file": candidate.path,
            "file_id": candidate.path,
            "line_number": int(line_number_raw) if line_number_raw.isdigit() else 0,
            "raw": raw,
            "matched_filters": matched_filters,
        })
    return lines


async def close_all_connections() -> None:
    """Call on app shutdown to close pooled SSH connections cleanly."""
    async with _pool_lock:
        for conn in _connection_pool.values():
            conn.close()
        _connection_pool.clear()