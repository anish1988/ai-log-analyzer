"""
STEP 3.13.3 - ProgressPublisher test.
"""

import asyncio

from app.ai.progress.events import ProgressStatus
from app.ai.progress.publisher import ProgressPublisher


# =============================================================================
# TEST CALLBACK
# =============================================================================

received_events = []


def test_callback(event):

    print()
    print("CALLBACK RECEIVED EVENT")

    received_events.append(
        event
    )


# =============================================================================
# TEST
# =============================================================================

async def main():

    print("=" * 100)
    print("STEP 3.13.3 - PROGRESS PUBLISHER TEST")
    print("=" * 100)

    publisher = ProgressPublisher(
        callback=test_callback
    )

    # -------------------------------------------------------------------------
    # STARTED
    # -------------------------------------------------------------------------

    event_1 = await publisher.publish(

        request_id="TEST-3.13.3",

        error_id="TEST-ERROR-001",

        task_id="initialize_analysis",

        task_name="Initializing AI analysis",

        status=ProgressStatus.STARTED,

        progress=0,

        message="Starting AI analysis.",

        log_type="laravel",

        error_index=0,

        total_errors=1,
    )

    # -------------------------------------------------------------------------
    # RUNNING
    # -------------------------------------------------------------------------

    event_2 = await publisher.publish(

        request_id="TEST-3.13.3",

        error_id="TEST-ERROR-001",

        task_id="retrieve_rag",

        task_name="Searching historical knowledge",

        status=ProgressStatus.RUNNING,

        progress=35,

        message="Searching historical knowledge.",

        log_type="laravel",

        error_index=0,

        total_errors=1,
    )

    # -------------------------------------------------------------------------
    # COMPLETED
    # -------------------------------------------------------------------------

    event_3 = await publisher.publish(

        request_id="TEST-3.13.3",

        error_id="TEST-ERROR-001",

        task_id="finalize_analysis",

        task_name="Finalizing analysis",

        status=ProgressStatus.COMPLETED,

        progress=100,

        message="AI analysis completed.",

        log_type="laravel",

        error_index=0,

        total_errors=1,
    )

    # =========================================================================
    # VALIDATION
    # =========================================================================

    assert event_1.status == ProgressStatus.STARTED

    assert event_2.status == ProgressStatus.RUNNING

    assert event_3.status == ProgressStatus.COMPLETED

    assert event_1.progress == 0

    assert event_2.progress == 35

    assert event_3.progress == 100

    assert event_1.error_index == 0

    assert event_1.total_errors == 1

    assert len(received_events) == 3

    print()
    print("=" * 100)
    print(
        "Events received:",
        len(received_events),
    )

    print(
        "First event:",
        received_events[0].model_dump(),
    )

    print(
        "Last event:",
        received_events[-1].model_dump(),
    )

    print("=" * 100)
    print("STEP 3.13.3 TEST PASSED")
    print("=" * 100)


if __name__ == "__main__":

    asyncio.run(main())