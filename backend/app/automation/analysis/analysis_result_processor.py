"""
Phase 3.6 - Analysis Result Processor.

Responsibilities
----------------
1. Receive final_results[] from the existing LangGraph.
2. Process every result independently.
3. Create one Jira ticket per result when enabled.
4. Write one response JSON file per result.
5. Update AutomationRun counters.

This module does NOT:
    - parse logs
    - run LangGraph
    - perform RAG
    - call LLM directly
    - implement Jira API calls

Those responsibilities remain in their existing modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.automation.jira.jira_ticket_processor import (
    JiraTicketProcessor,
)
from app.automation.orchestrator.models import (
    AutomationRun,
)
from app.automation.results.result_writer import (
    AutomationResultWriter,
)


@dataclass
class AnalysisProcessingSummary:
    """
    Summary of processing all final AI results.
    """

    total_results: int = 0

    jira_created: int = 0

    jira_failed: int = 0

    jira_skipped: int = 0

    response_files_written: int = 0

    response_files_failed: int = 0

    response_files: list[str] = field(
        default_factory=list
    )


class AnalysisResultProcessor:
    """
    Processes final_results[] from LangGraph.
    """

    def __init__(
        self,
        *,
        jira_processor: JiraTicketProcessor | None = None,
        result_writer: AutomationResultWriter | None = None,
    ) -> None:

        self.jira_processor = (
            jira_processor
            or JiraTicketProcessor()
        )

        self.result_writer = (
            result_writer
            or AutomationResultWriter()
        )

    async def process(
        self,
        *,
        run: AutomationRun,
        final_results: list[dict[str, Any]],
    ) -> AnalysisProcessingSummary:
        """
        Process every final AI analysis result.

        One result is processed independently from another.

        Therefore:

            30 results
                ->
            30 Jira attempts
                ->
            30 response files
        """

        summary = (
            AnalysisProcessingSummary(
                total_results=len(
                    final_results
                )
            )
        )

        print("=" * 100)
        print("PHASE 3.6 - ANALYSIS RESULT PROCESSING")
        print("=" * 100)

        print(
            f"Run ID       : {run.run_id}"
        )

        print(
            f"Final Results: {len(final_results)}"
        )

        print("=" * 100)

        for index, analysis in enumerate(
            final_results,
            start=1,
        ):

            error_id = (
                str(
                    analysis.get(
                        "error_id",
                        f"UNKNOWN-{index}",
                    )
                )
            )

            print(
                f"[{index}/{len(final_results)}] "
                f"Processing {error_id}"
            )

            # =============================================================
            # STEP 1
            # Jira
            # =============================================================

            try:

                jira_result = (
                    await self.jira_processor.process(
                        analysis
                    )
                )

            except Exception as exc:

                # Jira processor is designed not to raise for normal
                # Jira failures, but keep this protection here so that
                # one unexpected processor error cannot stop all results.

                jira_result = {
                    "auto_create_enabled": True,
                    "created": False,
                    "issue_key": None,
                    "issue_id": None,
                    "issue_url": None,
                    "error": str(exc),
                }

            # =============================================================
            # STEP 2
            # Update Jira counters
            # =============================================================

            if jira_result.get(
                "created"
            ):

                run.jira_tickets_created += 1

                summary.jira_created += 1

            elif jira_result.get(
                "auto_create_enabled"
            ):

                run.jira_tickets_failed += 1

                summary.jira_failed += 1

            else:

                summary.jira_skipped += 1

            # =============================================================
            # STEP 3
            # Write complete response
            # =============================================================

            try:

                response_path = (
                    await self.result_writer.write(
                        run_id=run.run_id,
                        analysis=analysis,
                        jira=jira_result,
                    )
                )

                summary.response_files_written += 1

                summary.response_files.append(
                    str(response_path)
                )

                print(
                    f"Response File : "
                    f"{response_path}"
                )

            except Exception as exc:

                summary.response_files_failed += 1

                print(
                    f"Response File ERROR "
                    f"for {error_id}: {exc}"
                )

            print(
                f"Jira Created  : "
                f"{jira_result.get('created')}"
            )

            print(
                f"Jira Key      : "
                f"{jira_result.get('issue_key')}"
            )

            if jira_result.get("error"):

                print(
                    f"Jira Error    : "
                    f"{jira_result.get('error')}"
                )

            print("-" * 100)

        # =============================================================
        # STEP 4
        # Analysis counter
        # =============================================================

        run.analyses_completed += (
            len(final_results)
        )

        print("=" * 100)
        print("PHASE 3.6 - RESULT PROCESSING COMPLETED")
        print("=" * 100)

        print(
            f"Analyses Completed : "
            f"{run.analyses_completed}"
        )

        print(
            f"Jira Created       : "
            f"{run.jira_tickets_created}"
        )

        print(
            f"Jira Failed        : "
            f"{run.jira_tickets_failed}"
        )

        print(
            f"Jira Skipped       : "
            f"{summary.jira_skipped}"
        )

        print(
            f"Response Files     : "
            f"{summary.response_files_written}"
        )

        print("=" * 100)

        return summary