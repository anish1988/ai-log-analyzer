"""
Local-filesystem equivalent of ssh_client.search_remote_file.
"""

import asyncio
import gzip
import re
from pathlib import Path

from app.config.servers import ServerConfig
from app.log_fetchers.path_resolver import ResolvedLogPath

from app.log_fetchers.log_paths import (
    LOCAL_LOG_PATHS,
)





def _escape_for_regex(value: str) -> str:
    return re.escape(value)


def _search_local_file_sync(
    server: ServerConfig,
    candidate: ResolvedLogPath,
    search_terms: list[tuple[str, str]],
) -> list[dict]:

    print("=" * 100)
    print("LOCAL SEARCH")
    print("=" * 100)
    print(f"Server     : {server.id}")
    print(f"Service    : {candidate.service}")
    print(f"Filename   : {candidate.filename}")
    print(f"Gzipped    : {candidate.is_gzipped}")
    print(f"Dated      : {candidate.is_dated}")
    print("=" * 100)

    pattern = re.compile(
        "|".join(_escape_for_regex(value) for _, value in search_terms)
    )

    opener = gzip.open if candidate.is_gzipped else open

    candidate_paths = []

    for directory in LOCAL_LOG_PATHS.get(candidate.service, []):

        filename = candidate.filename

        #
        # Apache on RHEL uses *_log
        #
        if "httpd" in directory:
            filename = (
                filename
                .replace("access.log", "access_log")
                .replace("error.log", "error_log")
            )

        candidate_paths.append(Path(directory) / filename)

    print("\nCandidate Paths")

    for p in candidate_paths:
        print(" ->", p)

    for path in candidate_paths:

        print(f"\nChecking : {path}")

        if not path.is_file():
            continue

        print(f"Using : {path}")

        lines = []

        with opener(path, mode="rt", errors="replace") as fh:

            for line_number, raw_line in enumerate(fh, start=1):

                raw = raw_line.rstrip("\n")

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
                        "file": str(path),
                        "file_id": str(path),
                        "line_number": line_number,
                        "raw": raw,
                        "matched_filters": matched_filters,
                    }
                )

        print(f"Matched Lines : {len(lines)}")

        return lines

    print("No matching local log file found.")

    return []


async def search_local_file(
    server: ServerConfig,
    candidate: ResolvedLogPath,
    search_terms: list[tuple[str, str]],
) -> list[dict]:
    return await asyncio.to_thread(
        _search_local_file_sync,
        server,
        candidate,
        search_terms,
    )