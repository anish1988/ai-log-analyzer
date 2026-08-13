"""
STEP 3.13.4 - LangGraph Progress Helper test.
"""

import asyncio

from app.ai.graph.progress import report_progress
from app.ai.progress.events import ProgressStatus
from app.ai.progress.tasks import ProgressTasks


# =============================================================================
# TEST
# =============================================================================

async def main():

    print("=" * 100)
    print("STEP 3.13.4 - LANGGRAPH PROGRESS HELPER TEST")
    print("=" * 100)

    state = {

        "request_id": "TEST-3.13.4",

        "current_error_index": 1,

        "selected_errors": [

            {
                "error_id": "ERROR-001",
                "log_type": "laravel",
            },

            {
                "error_id": "ERROR-002",
                "log_type": "laravel",
            },

            {
                "error_id": "ERROR-003",
                "log_type": "laravel",
            },

        ],

        "current_error": {

            "error_id": "ERROR-002",

            "log_type": "laravel",

        },

    }

    # -------------------------------------------------------------------------
    # Publish event
    # -------------------------------------------------------------------------

    event = await report_progress(

        state,

        task_id=ProgressTasks.RETRIEVE_RAG,

        status=ProgressStatus.RUNNING,

        progress=35,

        message="Searching historical knowledge.",

    )

    # -------------------------------------------------------------------------
    # Print
    # -------------------------------------------------------------------------

    print()
    print("=" * 100)
    print("EVENT RECEIVED")
    print("=" * 100)

    print(
        event.model_dump()
    )

    # -------------------------------------------------------------------------
    # Assertions
    # -------------------------------------------------------------------------

    assert event.request_id == (
        "TEST-3.13.4"
    )

    assert event.error_id == (
        "ERROR-002"
    )

    assert event.error_index == 1

    assert event.total_errors == 3

    assert event.task_id == (
        ProgressTasks.RETRIEVE_RAG
    )

    assert event.task_name == (
        "Searching historical knowledge"
    )

    assert event.status == (
        ProgressStatus.RUNNING
    )

    assert event.progress == 35

    assert event.log_type == (
        "laravel"
    )

    print()
    print("=" * 100)
    print("STEP 3.13.4 TEST PASSED")
    print("=" * 100)


if __name__ == "__main__":

    asyncio.run(
        main()
    )