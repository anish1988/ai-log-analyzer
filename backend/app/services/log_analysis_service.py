"""
Full fetch pipeline:
  servers -> per server, only that server's tier's log files ->
  per file, per day in [from, to] -> resolve path candidates
  (gz vs plain, dated vs undated) -> grep over SSH -> dedupe ->
  group into one LogFileResult per (server, file).

Every (server, file) pair is fetched concurrently via asyncio.gather.
"""
import asyncio
from datetime import datetime

from app.config.log_files import LogFileConfig, get_log_files_for_tier
from app.config.servers import ServerConfig, get_selectable_servers, get_server_by_id
from app.log_fetchers.local_client import search_local_file
from app.log_fetchers.path_resolver import each_day, resolve_log_file_candidates
from app.log_fetchers.ssh_client import search_remote_file
from app.log_parsers.dedupe import dedupe_log_lines
from app.schemas.log_analysis import (
    LogFetchResponse,
    LogFileResultSchema,
    LogLineSchema,
    SearchFiltersRequest,
)

LOCAL_HOSTS = {"local", "localhost", "127.0.0.1"}

def _build_search_terms(filters: SearchFiltersRequest) -> list[tuple[str, str]]:
    fields = [
        ("lead_id", filters.lead_id),
        ("campaign_id", filters.campaign_id),
        ("unique_id", filters.unique_id),
        ("caller_id", filters.caller_id),
        ("caller_number", filters.caller_number),
        ("agent", filters.agent),
        ("inbound_group", filters.inbound_group),
    ]
    return [(key, value.strip()) for key, value in fields if value and value.strip()]


def _build_meta(filters: SearchFiltersRequest) -> dict[str, str]:
    meta: dict[str, str] = {}
    if filters.lead_id:
        meta["leadid"] = filters.lead_id
    if filters.campaign_id:
        meta["outbound"] = filters.campaign_id
    if filters.unique_id:
        meta["uniqueid"] = filters.unique_id
    return meta


async def _fetch_for_file(
    server: ServerConfig,
    file_config: LogFileConfig,
    from_date,
    to_date,
    search_terms: list[tuple[str, str]],
    meta: dict[str, str],
) -> LogFileResultSchema | None:
    all_lines: list[dict] = []

    for day in each_day(from_date, to_date):
        candidates = resolve_log_file_candidates(file_config, day)

        for candidate in candidates:
            if server.ip.lower() in LOCAL_HOSTS:
                print(f"[LOCAL] Reading {candidate.path}")
                lines = await search_local_file(server, candidate, search_terms)
            else:
                print(f"[SSH] Connecting to {server.ip}")
                lines = await search_remote_file(server, candidate, search_terms)
            all_lines.extend(lines)
            # First candidate that produces matches (or is the final, undated
            # fallback) wins for this day - stop trying further candidates.
            if lines or not candidate.is_dated:
                break

    deduped = dedupe_log_lines(all_lines)
    if not deduped:
        return None

    return LogFileResultSchema(
        file_id=file_config.id,
        file_label=file_config.label,
        server=server.id,
        meta=meta,
        lines=[LogLineSchema(**line) for line in deduped],
    )


async def fetch_logs(filters: SearchFiltersRequest) -> LogFetchResponse:
    eligible_ids = {s.id for s in get_selectable_servers(filters.tier)}
    servers = [
        server for sid in filters.servers
        if sid in eligible_ids and (server := get_server_by_id(sid)) is not None
    ]

    if not servers:
        raise ValueError("No matching servers found for the selected tier.")

    print("=" * 80)
    print("Incoming Filters:")
    print("Filter:", filters)
    print(filters.model_dump())   # Use filters.dict() if you're on Pydantic v1
    print("=" * 80)

    search_terms = _build_search_terms(filters)
    print("Search Terms:", search_terms)

    print("Search Terms:")
    print(search_terms)
    print("=" * 80)

    if not search_terms:
        raise ValueError("At least one search field (lead_id, campaign_id, etc.) is required.")

    from_date = datetime.fromisoformat(filters.from_).date()
    to_date = datetime.fromisoformat(filters.to).date()
    meta = _build_meta(filters)

    tasks = [
        _fetch_for_file(server, file_config, from_date, to_date, search_terms, meta)
        for server in servers
        for file_config in get_log_files_for_tier(server.tier)
    ]

    results = await asyncio.gather(*tasks)
    result_buckets = [r for r in results if r is not None]

    return LogFetchResponse(
        total_lines=sum(len(bucket.lines) for bucket in result_buckets),
        results=result_buckets,
    )