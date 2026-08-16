"""
Standalone automation entry point.

Cron should invoke this module.

Business logic must remain inside reusable services.
"""

import asyncio

from app.automation.orchestrator.run_orchestrator import (
    AutomationRunOrchestrator,
)


async def main() -> None:

    orchestrator = AutomationRunOrchestrator()

    await orchestrator.run()


if __name__ == "__main__":
    asyncio.run(
        main()
    )