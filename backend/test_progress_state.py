"""
STEP 3.13.5 - LangGraph State Integration Test.
"""

from app.ai.graph.state import AIAnalysisState
from app.ai.progress.events import (
    ProgressEvent,
    ProgressStatus,
)


def main():

    print("=" * 100)
    print("STEP 3.13.5 - STATE INTEGRATION TEST")
    print("=" * 100)

    # -------------------------------------------------------------------------
    # Create test event
    # -------------------------------------------------------------------------

    event = ProgressEvent(

        request_id="TEST-3.13.5",

        error_id="ERROR-001",

        error_index=0,

        total_errors=1,

        task_id="initialize_analysis",

        task_name="Initializing AI analysis",

        status=ProgressStatus.STARTED,

        progress=0,

        message="Starting AI analysis.",

        log_type="laravel",
    )

    # -------------------------------------------------------------------------
    # Create state
    # -------------------------------------------------------------------------

    state: AIAnalysisState = {

        "request_id": "TEST-3.13.5",

        "tier": "web",

        "log_type": "laravel",

        "selected_errors": [],

        "current_error_index": 0,

        "current_error": None,

        "final_results": [],

        "status": "started",

        "current_task": "initialize_analysis",

        "progress": 0,

        "messages": [],

        "error": None,

        "progress_event": event,

        "progress_events": [
            event,
        ],
    }

    # -------------------------------------------------------------------------
    # Validate latest event
    # -------------------------------------------------------------------------

    assert state["progress_event"] is not None

    assert (
        state["progress_event"].request_id
        == "TEST-3.13.5"
    )

    assert (
        state["progress_event"].task_id
        == "initialize_analysis"
    )

    # -------------------------------------------------------------------------
    # Validate event history
    # -------------------------------------------------------------------------

    assert (
        len(state["progress_events"])
        == 1
    )

    assert (
        state["progress_events"][0].error_id
        == "ERROR-001"
    )

    assert (
        state["progress_events"][0].progress
        == 0
    )

    # -------------------------------------------------------------------------
    # Validate status/progress consistency
    # -------------------------------------------------------------------------

    assert (
        state["status"]
        == "started"
    )

    assert (
        state["current_task"]
        == "initialize_analysis"
    )

    assert (
        state["progress"]
        == 0
    )

    print()
    print("State progress_event:")
    print(
        state["progress_event"].model_dump()
    )

    print()
    print(
        "Total progress events:",
        len(state["progress_events"]),
    )

    print()
    print("=" * 100)
    print("STEP 3.13.5 TEST PASSED")
    print("=" * 100)


if __name__ == "__main__":
    main()