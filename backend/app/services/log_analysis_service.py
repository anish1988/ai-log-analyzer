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
from app.config.servers import ServerConfig, get_selectable_servers, get_server_by_id, SERVER_REGISTRY
from app.log_fetchers.local_client import search_local_file
from app.log_fetchers.path_resolver import each_day, resolve_log_file_candidates
from app.log_fetchers.ssh_client import search_remote_file
from app.log_parsers.dedupe import dedupe_log_lines
from app.log_fetchers.web_log_fetcher import read_web_log
from app.schemas.log_analysis import (
    LogFetchResponse,
    LogFileResultSchema,
    LogLineSchema,
    SearchFiltersRequest,
)
from app.schemas.log_analysis import (
    SearchFiltersRequest,
    WebLogFetchResponse,
    WebLogFileSchema,
    WebErrorBlockSchema,
    WebLogLineSchema,
)
import logging
from pathlib import Path
from app.services.web_log_processor import WebLogProcessor
from app.parsers.parser_factory import ParserFactory



logger = logging.getLogger(__name__)
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


async def _fetch_for_file_old(
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

async def _fetch_for_file(
    server: ServerConfig,
    file_config: LogFileConfig,
    from_date,
    to_date,
    search_terms: list[tuple[str, str]],
    meta: dict[str, str],
) -> LogFileResultSchema:

    all_lines: list[dict] = []
    searched_file = ""

    print("=" * 80)
    print(f"Searching File : {file_config.label}")
    print(f"Server         : {server.id}")
    print("=" * 80)

    for day in each_day(from_date, to_date):

        candidates = resolve_log_file_candidates(file_config, day)

        logger.info("=" * 80)
        logger.info("SERVICE RECEIVED CANDIDATES")

        for c in candidates:
            logger.info(
                f"{c.service}/{c.filename}"
            )

        logger.info("=" * 80)

        for candidate in candidates:

            
            searched_file = f"{candidate.service}/{candidate.filename}"
            print(f"Checking : {candidate.service}/{candidate.filename}")

            if server.ip.lower() in LOCAL_HOSTS:

                print(f"[LOCAL] Reading {searched_file}")

                lines = await search_local_file(
                    server,
                    candidate,
                    search_terms,
                )

            else:

                print(f"[SSH] Reading {searched_file}")

                lines = await search_remote_file(
                    server,
                    candidate,
                    search_terms,
                )

            print(f"Matched Lines : {len(lines)}")

            all_lines.extend(lines)

            # Stop searching other candidates once a dated file
            # produced matches OR this is the undated fallback.
            if lines or not candidate.is_dated:
                break

    deduped = dedupe_log_lines(all_lines)

    print(f"Deduped Lines : {len(deduped)}")

    return LogFileResultSchema(
        file_id=file_config.id,
        file_label=file_config.label,
        server=server.id,
        searched_file=searched_file,
        meta=meta,
        matched_count=len(deduped),
        lines=[
            LogLineSchema(**line)
            for line in deduped
        ],
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

    print("\n================== Creating Tasks ==================\n")

    tasks = [
        _fetch_for_file(server, file_config, from_date, to_date, search_terms, meta)
        for server in servers
        for file_config in get_log_files_for_tier(server.tier)
    ]

   # results = await asyncio.gather(*tasks)
   # result_buckets = [r for r in results if r is not None]
   
    print(f"Total Tasks Created : {len(tasks)}")

    print("\n================== Executing Tasks ==================\n")

    results = await asyncio.gather(*tasks)

    print("\n================== Raw Results ==================\n")

    for idx, result in enumerate(results, start=1):
        print(f"\n----- Result {idx} -----")
        print(f"Type : {type(result)}")
        print(result)

    print("\n================== Filtering Results ==================\n")

    #result_buckets = [r for r in results if r is not None]
    result_buckets = results

    print(f"Buckets after filtering : {len(result_buckets)}")

    for idx, bucket in enumerate(result_buckets, start=1):
        print(f"\n===== Bucket {idx} =====")
        print(f"Type          : {type(bucket)}")

        if hasattr(bucket, "server"):
            print(f"Server        : {bucket.server}")

        if hasattr(bucket, "log_file"):
            print(f"Log File      : {bucket.log_file}")

        if hasattr(bucket, "lines"):
            print(f"Matched Lines : {len(bucket.lines)}")

            for line_no, line in enumerate(bucket.lines, start=1):
                print(f"\nLine {line_no}")
                print(line)

        print("\n================== Summary ==================\n")

        #total = sum(len(bucket.lines) for bucket in result_buckets)
        total = sum(bucket.matched_count for bucket in result_buckets)
        print(f"Total Matched Lines : {total}")


   # return LogFetchResponse(
    #    total_lines=sum(len(bucket.lines) for bucket in result_buckets),
     #   results=result_buckets,
    #)
    total_lines = sum(bucket.matched_count for bucket in result_buckets)

    return LogFetchResponse(
        total_lines=total_lines,
        results=result_buckets,
    )


from app.schemas.log_analysis import (
    SearchFiltersRequest,
    LogFetchResponse,
)


async def fetch_web_logs11(
    request: SearchFiltersRequest,
) -> LogFetchResponse:
    """
    Web Log Analyzer

    Flow:
        UI
            ↓
        Validate Request
            ↓
        Resolve Server
            ↓
        Read Log File
            ↓
        Return Response
    """

    print("\n")
    print("=" * 100)
    print("WEB LOG ANALYZER")
    print("=" * 100)

    print(f"Tier              : {request.tier}")
    print(f"Servers           : {request.servers}")
    print(f"Log Type          : {request.log_type}")
    print(f"Default Path      : {request.default_path}")
    print(f"Custom Path       : {request.custom_path}")

    # ------------------------------------------------------------------
    # Decide actual log path
    # ------------------------------------------------------------------

    actual_path = (
        request.custom_path.strip()
        if request.custom_path and request.custom_path.strip()
        else request.default_path
    )

    print(f"Actual Path       : {actual_path}")

    print("=" * 100)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    if not request.servers:
        raise ValueError("Please select at least one server.")

    if not request.log_type:
        raise ValueError("Please select Log Type.")

    if not actual_path:
        raise ValueError("Log path cannot be empty.")

    # ------------------------------------------------------------------
    # Read logs from selected server(s)
    # ------------------------------------------------------------------

    total_lines = 0
    results = []

    for server_id in request.servers:

        print("\n")
        print("=" * 80)
        print(f"Processing Server : {server_id}")
        print("=" * 80)

        #
        # Resolve Server
        #
        server = next(
            (
                s
                for s in SERVER_REGISTRY
                if s.id == server_id
            ),
            None,
        )

        if server is None:
            print(f"Server not found : {server_id}")
            continue

        print(f"Server Name : {server.id}")
        print(f"Server IP   : {server.ip}")
        print(f"SSH User    : {server.ssh_user}")

        #
        # Read log file
        #
        lines = await read_web_log(
            server=server,
            log_path=actual_path,
        )

        print("-" * 80)
        print(f"Lines Read : {len(lines)}")
        print("-" * 80)

        #
        # Preview first few lines
        #
        for index, line in enumerate(lines[:10], start=1):
            print(f"{index:03d}: {line}")

        total_lines += len(lines)

        #
        # Temporary Result
        #
        # Later we'll replace this with
        # parsed error JSON
        #
        results.append(
            {
                "server": server.id,
                "path": actual_path,
                "line_count": len(lines),
            }
        )

    print("\n")
    print("=" * 100)
    print("WEB ANALYZER COMPLETED")
    print("=" * 100)
    print(f"Servers Processed : {len(results)}")
    print(f"Total Lines       : {total_lines}")
    print("=" * 100)

    #
    # Temporary Response
    #
    # We keep LogFetchResponse
    # because frontend already expects it.
    #

    return LogFetchResponse(
        total_lines=total_lines,
        results=[],
    )
    """
    Phase 2

    Web Log Analyzer

    Current Version:
    ----------------
    ✔ Validate request
    ✔ Determine actual log path
    ✔ Print debug information
    ✔ Return empty response

    Next Version:
    -------------
    - SSH connection
    - Read selected log file
    - Parse log
    - Build JSON response
    """

    print("\n")
    print("=" * 100)
    print("WEB LOG ANALYZER")
    print("=" * 100)

    #
    # Tier
    #
    print(f"Tier              : {request.tier}")

    #
    # Cluster(s)
    #
    print(f"Selected Servers  : {request.servers}")

    #
    # Log Type
    #
    print(f"Log Type          : {request.log_type}")

    #
    # Configured Path
    #
    print(f"Default Path      : {request.default_path}")

    #
    # User Override
    #
    print(f"Custom Path       : {request.custom_path}")

    #
    # Decide actual path
    #
    actual_path = (
        request.custom_path.strip()
        if request.custom_path and request.custom_path.strip()
        else request.default_path
    )

    server = next(
    ( s for s in SERVER_REGISTRY if s.id == request.servers[0]),
    None,
    )

    if server is None:
        raise ValueError(
            f"Server not found : {request.servers[0]}"
        )

    print(f"Resolved Server : {server.id}")
    print(f"Server IP       : {server.ip}")

    print(f"Actual Path       : {actual_path}")

    print("=" * 100)

    #
    # Validation
    #
    if not request.servers:
        raise ValueError("Please select at least one server.")

    if not request.log_type:
        raise ValueError("Please select Log Type.")

    if not actual_path:
        raise ValueError("Log path cannot be empty.")

    #
    # Next Step
    #
    print("Next Step : Read log file from SSH server...")
    print("=" * 100)

    #
    # Temporary Response
    #
    return LogFetchResponse(
        total_lines=0,
        results=[]
    )




async def fetch_web_logs(
    request: SearchFiltersRequest,
) -> WebLogFetchResponse:

    print("\n")
    print("=" * 100)
    print("WEB LOG ANALYZER START")
    print("=" * 100)
    print("\n")
    print("=" * 100)
    print("STEP-1 : REQUEST RECEIVED")
    print("=" * 100)

    print(request.model_dump())

    from app.config.web_logs import debug_web_logs

    debug_web_logs()

    #
    # Validation
    #
    if not request.servers:
        raise ValueError("Please select at least one server.")

    if not request.log_type:
        raise ValueError("Please select Log Type.")

    from app.config.web_logs import WEB_LOG_PATHS

    #
    # Resolve actual path from backend config
    #
    config = WEB_LOG_PATHS.get(request.log_type)
    print("\n")
    print("=" * 100)
    print("STEP-3 : BACKEND CONFIG")
    print("=" * 100)

    print(config)

    if config is None:
        raise ValueError(f"Unsupported log type: {request.log_type}")

    #
    # User entered custom path?
    #
    if request.custom_path and request.custom_path.strip():

        actual_path = request.custom_path.strip()

        print("Using Custom Path")

    else:

        actual_path = config["path"]

        print("Using Backend Config Path")

    print(f"Resolved Path : {actual_path}")

    if not actual_path:
        raise ValueError("Log path is empty.")

    print("\nREQUEST DETAILS")
    print("-" * 100)
    print(f"Tier             : {request.tier}")
    print(f"Servers          : {request.servers}")
    print(f"Log Type         : {request.log_type}")
    print(f"Default Path     : {request.default_path}")
    print(f"Custom Path      : {request.custom_path}")
    print(f"Actual Path      : {actual_path}")

   # processor = WebLogProcessor()

    response_files: list[WebLogFileSchema] = []

    #
    # Process every selected server
    #
    for server_id in request.servers:

        print("\n")
        print("=" * 100)
        print(f"PROCESSING SERVER : {server_id}")
        print("=" * 100)

        server = next(
            (s for s in SERVER_REGISTRY if s.id == server_id),
            None,
        )

        if server is None:
            print(f"❌ Server not found : {server_id}")
            continue

        print("✅ Server Found")
        print(f"Server ID    : {server.id}")
        print(f"Server Label : {server.label}")
        print(f"Server IP    : {server.ip}")
        print(f"SSH User     : {server.ssh_user}")

        #
        # Read file
        #
        print("\nREADING LOG FILE...")
        print("-" * 100)

        raw_lines = await read_web_log(
            server=server,
            log_path=actual_path,
        )

        print(f"Returned Object Type : {type(raw_lines)}")
        print(f"Total Lines Read     : {len(raw_lines)}")

        if raw_lines:

            print("\nFIRST LINE")
            print(raw_lines[0])

            print("\nLAST LINE")
            print(raw_lines[-1])

        else:

            print("❌ No lines returned from read_web_log()")
            continue

        #
        # Processor
        #
        print("\n")
        print("=" * 100)
        print("CALLING WEB LOG PROCESSOR")
        print("=" * 100)

      #  response = processor.process(
       #     server=server.id,
        #    log_type=request.log_type,
        #    file_path=actual_path,
        #    raw_lines=raw_lines,
        #)

        #
        # Select Parser
        #
        print("=" * 100)
        print("PARSER DEBUG")
        print("=" * 100)
        print(f"Request Log Type : {request.log_type}")
        print(f"Selected Log Type : {log_type if 'log_type' in locals() else 'N/A'}")
        print("=" * 100)
        parser = ParserFactory.get_parser(
            request.log_type,
        )

        print("=" * 100)
        print("START PARSING")
        print("=" * 100)

        response = parser.parse(

            server=server.id,

            log_type=request.log_type,

            file_name=Path(actual_path).name,

            file_path=actual_path,

            raw_lines=raw_lines,

        )

        print("=" * 100)
        print("PARSING COMPLETED")
        print("=" * 100)
        print(f"Total Errors : {response.total_errors}")

        print("\nPROCESSOR RAW RESPONSE")
        print("-" * 100)
        print(response.model_dump())

        print("\nPROCESSOR SUMMARY")
        print("-" * 100)
        print(f"Server        : {response.server}")
        print(f"Log Type      : {response.log_type}")
        print(f"File Name     : {response.file_name}")
        print(f"Total Lines   : {response.total_lines}")
        print(f"Total Errors  : {response.total_errors}")

        #
        # Merge response
        #
        response_files.append(response)

        print("\nAFTER MERGE")
        print("-" * 100)
        print(f"Current Total Files : {len(response_files)}")

    #
    # Final Summary
    #
    print("\n")
    print("=" * 100)
    print("FINAL RESPONSE")
    print("=" * 100)

    print(f"Total Response Files : {len(response_files)}")

    if response_files:

        for idx, file in enumerate(response_files, start=1):

            print("\n")
            print(f"FILE #{idx}")
            print("-" * 60)

            print(f"Server       : {file.server}")
            print(f"File Name    : {file.file_name}")
            print(f"Total Lines  : {file.total_lines}")
            print(f"Total Errors : {file.total_errors}")

    else:

        print("❌ No response files generated.")

    print("\n")
    print("=" * 100)
    print("WEB LOG ANALYZER END")
    print("=" * 100)

    return WebLogFetchResponse(
        success=True,
        message="Web Log Analysis Completed Successfully.",
        results=response_files,
    )