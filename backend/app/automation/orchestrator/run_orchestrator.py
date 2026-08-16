"""
Automation run orchestrator.

This is the central reusable automation service.

Cron, future REST APIs, and future frontend-triggered
runs should all call this service rather than implementing
their own automation logic.
"""

from app.automation.orchestrator.models import AutomationRun
from app.automation.orchestrator.run_id import generate_run_id


class AutomationRunOrchestrator:
    """
    Coordinates one complete automation execution.
    """

    async def run(self) -> AutomationRun:
        """
        Execute one automation run.

        The actual server/log/analysis processors will be
        added in the following Phase 3 steps.
        """

        run = AutomationRun(
            run_id=generate_run_id()
        )

        print("=" * 100)
        print("AUTOMATION RUN STARTED")
        print("=" * 100)
        print(
            f"Run ID : {run.run_id}"
        )

        try:
            # -------------------------------------------------------------
            # Server processing will be added next.
            # -------------------------------------------------------------

            run.complete()

            print("=" * 100)
            print("AUTOMATION RUN COMPLETED")
            print("=" * 100)

            print(
                f"Run ID : {run.run_id}"
            )

            print(
                f"Status : {run.status}"
            )

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