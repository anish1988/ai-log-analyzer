"""
Automation run orchestrator.

Coordinates one complete automation execution.

Execution order:

    configured servers
        ↓
    ServerProcessor
        ↓
    Incremental Reader
        ↓
    Existing Parser
        ↓
    Existing LangGraph
        ↓
    AnalysisResultProcessor
        ↓
    Checkpoint
"""

from __future__ import annotations

from app.automation.orchestrator.models import (
    AutomationRun,
)
from app.automation.orchestrator.run_id import (
    generate_run_id,
)
from app.automation.server.server_processor import (
    ServerProcessor,
)
from app.config.servers import (
    SERVER_REGISTRY,
)


class AutomationRunOrchestrator:
    """
    Coordinates one complete automation execution.

    Servers are deliberately processed sequentially.
    """

    def __init__(
        self,
        *,
        server_processor: ServerProcessor | None = None,
    ) -> None:

        self.server_processor = (
            server_processor
            or ServerProcessor()
        )

    async def run(
        self,
        *,
        servers=None,
    ) -> AutomationRun:
        """
        Execute one automation run.

        Parameters
        ----------
        servers:
            Optional list of ServerConfig objects.

            If omitted, SERVER_REGISTRY is used.
        """

        configured_servers = (
            list(
                servers
                if servers is not None
                else SERVER_REGISTRY
            )
        )

        run = AutomationRun(
            run_id=generate_run_id()
        )

        run.servers_total = (
            len(configured_servers)
        )

        run.metadata = {
            "phase": "3.6",
            "automation": True,
            "servers": [
                server.id
                for server in configured_servers
            ],
        }

        print("=" * 100)
        print("AUTOMATION RUN STARTED")
        print("=" * 100)
        print(
            f"Run ID : {run.run_id}"
        )
        print(
            f"Servers: {len(configured_servers)}"
        )
        print("=" * 100)

        try:

            # ==========================================================
            # IMPORTANT:
            # Process one server at a time.
            # ==========================================================

            for server in configured_servers:

                print()
                print("=" * 100)
                print(
                    f"START SERVER: {server.id}"
                )
                print("=" * 100)

                server_result = (
                    await self.server_processor.process(
                        run=run,
                        server=server,
                    )
                )

                run.servers_processed += 1

                run.logs_total += (
                    server_result.logs_total
                )

                run.logs_processed += (
                    server_result.logs_processed
                )

                run.lines_read += (
                    server_result.lines_read
                )

                run.errors_detected += (
                    server_result.errors_detected
                )

                # Analysis/Jira counters are also updated
                # directly by AnalysisResultProcessor, but
                # keeping the server-level totals here makes
                # the orchestration result self-contained.

                print()
                print("=" * 100)
                print(
                    f"FINISHED SERVER: {server.id}"
                )
                print("=" * 100)

            run.complete()

            print("=" * 100)
            print("AUTOMATION RUN COMPLETED")
            print("=" * 100)

            print(
                f"Run ID              : {run.run_id}"
            )

            print(
                f"Status              : {run.status}"
            )

            print(
                f"Servers Processed   : "
                f"{run.servers_processed}/"
                f"{run.servers_total}"
            )

            print(
                f"Logs Processed      : "
                f"{run.logs_processed}/"
                f"{run.logs_total}"
            )

            print(
                f"Lines Read          : "
                f"{run.lines_read}"
            )

            print(
                f"Errors Detected     : "
                f"{run.errors_detected}"
            )

            print(
                f"Analyses Completed  : "
                f"{run.analyses_completed}"
            )

            print(
                f"Jira Created        : "
                f"{run.jira_tickets_created}"
            )

            print(
                f"Jira Failed         : "
                f"{run.jira_tickets_failed}"
            )

            print("=" * 100)

            return run

        except Exception as exc:

            run.fail(
                str(exc)
            )

            print("=" * 100)
            print("AUTOMATION RUN FAILED")
            print("=" * 100)

            print(
                f"Run ID : {run.run_id}"
            )

            print(
                f"Error  : {exc}"
            )

            raise