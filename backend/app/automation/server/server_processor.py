"""
Phase 3.6 - Server Processor.

Processes one configured server.

Flow:

    Server
      ↓
    LogFileConfig
      ↓
    AutomationLogSourceResolver
      ↓
    IncrementalLogReader
      ↓
    Existing Parser
      ↓
    Existing LangGraph
      ↓
    AnalysisResultProcessor
      ↓
    Checkpoint

Checkpoint is persisted only after successful downstream
processing.
"""

from __future__ import annotations

from typing import Any

from app.automation.analysis.analysis_result_processor import (
    AnalysisResultProcessor,
)
from app.automation.analysis.error_analysis_runner import (
    ErrorAnalysisRunner,
)
from app.automation.logs.incremental_reader import (
    IncrementalLogReader,
)
from app.automation.logs.log_source_resolver import (
    AutomationLogSourceResolver,
)
from app.automation.persistence.checkpoint_repository import (
    AutomationCheckpointRepository,
)
from app.automation.server.models import (
    AutomationServerResult,
)
from app.config.log_files import (
    LogFileConfig,
    get_log_files_for_tier,
)
from app.config.servers import (
    ServerConfig,
)
from app.parsers.parser_factory import (
    ParserFactory,
)


class ServerProcessor:
    """
    Processes all currently supported logs for one server.

    Servers themselves are processed sequentially by the
    orchestrator.
    """

    def __init__(
        self,
        *,
        incremental_reader: IncrementalLogReader | None = None,
        analysis_runner: ErrorAnalysisRunner | None = None,
        result_processor: AnalysisResultProcessor | None = None,
        checkpoint_repository: (
            AutomationCheckpointRepository | None
        ) = None,
        source_resolver: (
            AutomationLogSourceResolver | None
        ) = None,
    ) -> None:

        self.checkpoint_repository = (
            checkpoint_repository
            or AutomationCheckpointRepository()
        )

        self.incremental_reader = (
            incremental_reader
            or IncrementalLogReader(
                checkpoint_repository=(
                    self.checkpoint_repository
                )
            )
        )

        self.analysis_runner = (
            analysis_runner
            or ErrorAnalysisRunner()
        )

        self.result_processor = (
            result_processor
            or AnalysisResultProcessor()
        )

        self.source_resolver = (
            source_resolver
            or AutomationLogSourceResolver()
        )

    async def process(
        self,
        *,
        run,
        server: ServerConfig,
    ) -> AutomationServerResult:

        result = AutomationServerResult(
            server_id=server.id,
            status="running",
        )

        log_files = get_log_files_for_tier(
            server.tier
        )

        result.logs_total = len(
            log_files
        )

        print()
        print("=" * 100)
        print("PHASE 3.6 - SERVER PROCESSOR")
        print("=" * 100)
        print(
            f"Run ID    : {run.run_id}"
        )
        print(
            f"Server    : {server.id}"
        )
        print(
            f"Tier      : {server.tier.value}"
        )
        print(
            f"Log Files : {len(log_files)}"
        )
        print("=" * 100)

        for log_config in log_files:

            try:

                await self._process_log(
                    run=run,
                    server=server,
                    log_config=log_config,
                    result=result,
                )

            except Exception as exc:

                print()
                print("=" * 100)
                print("LOG PROCESSING FAILED")
                print("=" * 100)
                print(
                    f"Server : {server.id}"
                )
                print(
                    f"Log    : {log_config.id}"
                )
                print(
                    f"Error  : {exc}"
                )
                print("=" * 100)

                if result.error_message:

                    result.error_message += (
                        f"; {log_config.id}: {exc}"
                    )

                else:

                    result.error_message = (
                        f"{log_config.id}: {exc}"
                    )

                # Continue with the next log.
                continue

        result.status = "completed"

        return result

    async def _process_log(
        self,
        *,
        run,
        server: ServerConfig,
        log_config: LogFileConfig,
        result: AutomationServerResult,
    ) -> None:

        print()
        print("-" * 100)
        print(
            f"LOG: {log_config.id}"
        )
        print(
            f"SERVER: {server.id}"
        )
        print("-" * 100)

        # ============================================================
        # STEP 1
        # Discover the actual physical log file.
        # ============================================================

        source = await self.source_resolver.discover(
            server=server,
            log_config=log_config,
        )

        if source is None:

            print(
                "No physical log file found."
            )

            result.logs_processed += 1

            return

        print()
        print(
            f"Discovered source: {source.file_path}"
        )

        # ============================================================
        # STEP 2
        # Incremental read.
        #
        # IncrementalLogReader:
        #     - loads checkpoint
        #     - checks file
        #     - detects rotation/truncation
        #     - reads only new data
        #
        # It does NOT save the checkpoint.
        # ============================================================

        read_result = (
            await self.incremental_reader.read(
                server=server,
                log_type=source.log_type,
                file_path=source.file_path,
            )
        )

        result.lines_read += (
            read_result.lines_read
        )

        print()
        print(
            f"Previous line  : "
            f"{read_result.previous_line}"
        )

        print(
            f"Current lines  : "
            f"{read_result.start_line}"
            f" -> "
            f"{read_result.end_line}"
        )

        print(
            f"Previous offset: "
            f"{read_result.previous_offset}"
        )

        print(
            f"Current offset : "
            f"{read_result.end_offset}"
        )

        print(
            f"Lines read     : "
            f"{read_result.lines_read}"
        )

        print(
            f"Rotated        : "
            f"{read_result.rotated}"
        )

        print(
            f"Truncated      : "
            f"{read_result.truncated}"
        )

        # ============================================================
        # No new data.
        #
        # Do NOT create a new checkpoint unnecessarily.
        # ============================================================

        if not read_result.has_new_data:

            print(
                "No new data."
            )

            result.logs_processed += 1

            return

        # ============================================================
        # STEP 3
        # Parse only newly-read lines.
        # ============================================================

        errors = (
            self._parse_errors(
                server=server,
                log_type=source.log_type,
                file_path=source.file_path,
                lines=read_result.lines,
            )
        )

        result.errors_detected += (
            len(errors)
        )

        print(
            f"Errors detected: "
            f"{len(errors)}"
        )

        # ============================================================
        # STEP 4
        # Existing LangGraph / AI workflow.
        # ============================================================

        analysis_state = (
            await self.analysis_runner.analyze(
                errors=errors,
                request_id=run.run_id,
            )
        )

        final_results = (
            analysis_state.get(
                "final_results",
                [],
            )
        )

        # ============================================================
        # STEP 5
        # Existing result processor.
        #
        # This includes the Phase 3.6 Jira integration.
        # ============================================================

        processing_summary = (
            await self.result_processor.process(
                run=run,
                final_results=final_results,
            )
        )

        result.analyses_completed += (
            processing_summary.total_results
        )

        result.jira_tickets_created += (
            processing_summary.jira_created
        )

        result.jira_tickets_failed += (
            processing_summary.jira_failed
        )

        # ============================================================
        # STEP 6
        # CHECKPOINT
        #
        # ONLY after:
        #
        #     read
        #     parse
        #     AI
        #     result processing
        #
        # succeeds.
        # ============================================================

        checkpoint = (
            self.incremental_reader.build_checkpoint(
                read_result
            )
        )

        await self.checkpoint_repository.save_checkpoint(
            checkpoint,
            server_ip=server.ip,
            metadata={
                "run_id": run.run_id,
                "phase": "3.6",
                "log_id": log_config.id,
                "log_type": source.log_type,
                "lines_read": read_result.lines_read,
                "errors_detected": len(errors),
                "analyses_completed": (
                    processing_summary.total_results
                ),
                "jira_tickets_created": (
                    processing_summary.jira_created
                ),
                "jira_tickets_failed": (
                    processing_summary.jira_failed
                ),
                "rotated": read_result.rotated,
                "truncated": read_result.truncated,
            },
        )

        print(
            "CHECKPOINT SAVED"
        )

        result.logs_processed += 1

    @staticmethod
    def _parse_errors(
        *,
        server: ServerConfig,
        log_type: str,
        file_path: str,
        lines: list[str],
    ) -> list[dict[str, Any]]:

        parser = ParserFactory.get_parser(
            log_type
        )

        parsed = parser.parse(
            server=server.id,
            log_type=log_type,
            file_name=file_path.rsplit("/", 1)[-1],
            file_path=file_path,
            raw_lines=lines,
        )

        if parsed is None:
            return []

        if isinstance(parsed, list):

            errors = parsed

        elif isinstance(parsed, dict):

            errors = parsed.get(
                "errors",
                [],
            )

        else:

            errors = getattr(
                parsed,
                "errors",
                [],
            )

        normalized: list[
            dict[str, Any]
        ] = []

        for error in errors:

            if hasattr(
                error,
                "model_dump",
            ):

                data = (
                    error.model_dump()
                )

            elif hasattr(
                error,
                "dict",
            ):

                data = (
                    error.dict()
                )

            elif isinstance(
                error,
                dict,
            ):

                data = dict(
                    error
                )

            else:

                data = {
                    "error": str(error)
                }

            data.setdefault(
                "server",
                server.id,
            )

            data.setdefault(
                "tier",
                server.tier.value,
            )

            data.setdefault(
                "log_type",
                log_type,
            )

            data.setdefault(
                "file_path",
                file_path,
            )

            normalized.append(
                data
            )

        return normalized