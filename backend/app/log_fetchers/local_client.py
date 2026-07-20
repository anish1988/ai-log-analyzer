"""
Local-filesystem equivalent of ssh_client.search_remote_file - used when
log_analysis_service resolves a server's IP to LOCAL_HOSTS (dev/testing
without needing a real SSH target).

Mirrors search_remote_file's behavior and output shape exactly (same dict
keys) so dedupe_log_lines / LogLineSchema don't need to know which path was
taken. File I/O is offloaded via asyncio.to_thread so a large local log
doesn't block the event loop while other (server, file) tasks are running
concurrently.
"""
import asyncio
import gzip
import re
from pathlib import Path

from app.config.servers import ServerConfig
from app.log_fetchers.path_resolver import ResolvedLogPath


def _escape_for_regex(value: str) -> str:
    return re.escape(value)


def _search_local_file_sync(
    server: ServerConfig,
    candidate: ResolvedLogPath,
    search_terms: list[tuple[str, str]],
) -> list[dict]:

    print("=" * 100)
    print("[local_reader::_search_local_file_sync] START")
    print(f"Server ID        : {server.id}")
    print(f"Server IP        : {server.ip}")
    print(f"Log File         : {candidate.path}")
    print(f"Gzipped          : {candidate.is_gzipped}")
    print(f"Search Terms     : {search_terms}")
    print("=" * 100)

    path = Path(candidate.path)

    print(f"[local_reader::_search_local_file_sync] Checking file exists: {path}")

    if not path.is_file():
        print(f"[local_reader::_search_local_file_sync] ERROR - File NOT found: {path}")
        return []

    print(f"[local_reader::_search_local_file_sync] File found.")

    pattern_string = "|".join(_escape_for_regex(value) for _, value in search_terms)

    print(f"[local_reader::_search_local_file_sync] Regex Pattern: {pattern_string}")

    pattern = re.compile(pattern_string)

    opener = gzip.open if candidate.is_gzipped else open

    print(f"[local_reader::_search_local_file_sync] Opening file...")

    lines: list[dict] = []
    total_lines = 0
    matched_count = 0

    with opener(path, mode="rt", errors="replace") as fh:

        print(f"[local_reader::_search_local_file_sync] File opened successfully.")

        for line_number, raw_line in enumerate(fh, start=1):

            total_lines += 1
            raw = raw_line.rstrip("\n")

            # Uncomment if you want to see EVERY line
            # print(f"Reading Line {line_number}: {raw}")

            if not pattern.search(raw):
                continue

            matched_count += 1

            print("-" * 80)
            print(f"[MATCH FOUND]")
            print(f"Line Number     : {line_number}")
            print(f"Raw Line        : {raw}")

            matched_filters = [
                key
                for key, value in search_terms
                if value in raw
            ]

            print(f"Matched Filters : {matched_filters}")
            print("-" * 80)

            lines.append({
                "server": server.id,
                "file": candidate.path,
                "file_id": candidate.path,
                "line_number": line_number,
                "raw": raw,
                "matched_filters": matched_filters,
            })

    print("=" * 100)
    print("[local_reader::_search_local_file_sync] COMPLETED")
    print(f"Total Lines Read : {total_lines}")
    print(f"Matched Lines    : {matched_count}")
    print("=" * 100)

    return lines

def _search_local_file_sync_old(
    server: ServerConfig,
    candidate: ResolvedLogPath,
    search_terms: list[tuple[str, str]],
) -> list[dict]:
    path = Path(candidate.path)
    if not path.is_file():
        return []

    pattern = re.compile("|".join(_escape_for_regex(value) for _, value in search_terms))
    opener = gzip.open if candidate.is_gzipped else open

    lines: list[dict] = []
    with opener(path, mode="rt", errors="replace") as fh:
        for line_number, raw_line in enumerate(fh, start=1):
            raw = raw_line.rstrip("\n")
            if not pattern.search(raw):
                continue
            matched_filters = [key for key, value in search_terms if value in raw]
            lines.append({
                "server": server.id,
                "file": candidate.path,
                "file_id": candidate.path,
                "line_number": line_number,
                "raw": raw,
                "matched_filters": matched_filters,
            })
    return lines


async def search_local_file(
    server: ServerConfig,
    candidate: ResolvedLogPath,
    search_terms: list[tuple[str, str]],
) -> list[dict]:
    return await asyncio.to_thread(_search_local_file_sync, server, candidate, search_terms)