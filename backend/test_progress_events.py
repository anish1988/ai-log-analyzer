"""
STEP 3.13 - PROGRESS EVENTS TEST

Tests:

3.13.7
    Single selected error progress flow.

3.13.10
    Multiple selected errors progress flow.

This test does NOT modify the LangGraph workflow.

It only invokes the existing graph and observes
the returned state/progress information.
"""

import asyncio
import json
import uuid

from app.ai.graph.workflow import build_ai_analysis_graph


# =============================================================================
# TEST ERROR
# =============================================================================

def build_test_error(
    error_id: str,
    log_type: str = "laravel",
):
    """
    Build a generic test error.

    This structure follows the SelectedError structure
    used by the LangGraph state.
    """

    return {
        "error_id": error_id,

        "tier": "web",

        "log_type": log_type,

        "server": "test-server",

        "file_name": "laravel.log",

        "file_path": "/var/log/laravel/laravel.log",

        "title": "Route [dashboard.test] not defined.",

        "severity": "ERROR",

        "timestamp": "2026-08-13 10:30:00",

        "start_line": 100,

        "end_line": 105,

        "total_lines": 6,

        "error_content": (
            "Route [dashboard.test] not defined."
        ),

        "lines": [
            {
                "line_number": 100,
                "file": "laravel.log",
                "raw": (
                    "Route [dashboard.test] "
                    "not defined."
                ),
            },
            {
                "line_number": 101,
                "file": "laravel.log",
                "raw": (
                    "#0 "
                    "/var/www/app/resources/views/"
                    "dashboard.blade.php(45): "
                    "route('dashboard.test')"
                ),
            },
            {
                "line_number": 102,
                "file": "laravel.log",
                "raw": (
                    "#1 "
                    "/var/www/app/vendor/laravel/"
                    "framework/src/Illuminate/"
                    "View/Engines/PhpEngine.php"
                ),
            },
        ],
    }


# =============================================================================
# PRINT PROGRESS EVENT
# =============================================================================

def print_progress_event(
    event: dict,
):
    """
    Print a progress event in a readable format.
    """

    print()
    print("=" * 100)
    print("PROGRESS EVENT")
    print("=" * 100)

    print(
        f"Request ID : "
        f"{event.get('request_id')}"
    )

    print(
        f"Error ID   : "
        f"{event.get('error_id')}"
    )

    print(
        f"Task ID    : "
        f"{event.get('task_id')}"
    )

    print(
        f"Task Name  : "
        f"{event.get('task_name')}"
    )

    print(
        f"Status     : "
        f"{event.get('status')}"
    )

    print(
        f"Progress   : "
        f"{event.get('progress')}%"
    )

    print(
        f"Message    : "
        f"{event.get('message')}"
    )


# =============================================================================
# EXTRACT PROGRESS EVENTS
# =============================================================================

def extract_progress_events(
    result: dict,
) -> list[dict]:
    """
    Extract progress events from the final LangGraph state.

    Currently supports the progress_event field.

    Later, when SSE / Redis is introduced, this test
    can be changed to collect events from the event stream.
    """

    events = []

    event = result.get(
        "progress_event"
    )

    if event:

        if isinstance(
            event,
            dict,
        ):

            events.append(event)

    return events


# =============================================================================
# VALIDATE EVENT
# =============================================================================

def validate_progress_event(
    event: dict,
):
    """
    Validate basic ProgressEvent structure.
    """

    required_fields = [

        "task_id",

        "task_name",

        "status",

        "progress",

        "message",
    ]

    for field in required_fields:

        assert field in event, (
            f"Missing progress event field: "
            f"{field}"
        )

    progress = event.get(
        "progress"
    )

    assert isinstance(
        progress,
        int,
    ), (
        "Progress must be an integer."
    )

    assert 0 <= progress <= 100, (
        f"Invalid progress value: "
        f"{progress}"
    )


# =============================================================================
# 3.13.7
# SINGLE ERROR TEST
# =============================================================================

async def test_single_error_progress():
    """
    STEP 3.13.7

    Test progress processing for one selected error.
    """

    print()
    print("=" * 100)
    print("STEP 3.13.7 - SINGLE ERROR PROGRESS TEST")
    print("=" * 100)

    request_id = (
        f"TEST-SINGLE-{uuid.uuid4().hex[:8]}"
    )

    selected_errors = [

        build_test_error(
            error_id="TEST-PROGRESS-001",
        )

    ]

    print(
        f"Request ID      : {request_id}"
    )

    print(
        f"Selected Errors : "
        f"{len(selected_errors)}"
    )

    # -------------------------------------------------------------------------
    # Build graph
    # -------------------------------------------------------------------------

    graph = build_ai_analysis_graph()

    # -------------------------------------------------------------------------
    # Initial state
    # -------------------------------------------------------------------------

    initial_state = {

        "request_id": request_id,

        "tier": "web",

        "log_type": "laravel",

        "selected_errors": selected_errors,

        "current_error_index": 0,

        "current_error": None,

        "final_results": [],

        "status": "started",

        "current_task": "initialize_analysis",

        "progress": 0,

        "messages": [],

        "error": None,
    }

    print()
    print("Starting LangGraph...")
    print()

    # -------------------------------------------------------------------------
    # Execute
    # -------------------------------------------------------------------------

    result = await graph.ainvoke(
        initial_state
    )

    # -------------------------------------------------------------------------
    # Print final state
    # -------------------------------------------------------------------------

    print()
    print("=" * 100)
    print("SINGLE ERROR GRAPH COMPLETED")
    print("=" * 100)

    print(
        f"Final Status : "
        f"{result.get('status')}"
    )

    print(
        f"Final Progress : "
        f"{result.get('progress')}%"
    )

    print(
        f"Final Task : "
        f"{result.get('current_task')}"
    )

    # -------------------------------------------------------------------------
    # Extract events
    # -------------------------------------------------------------------------

    events = extract_progress_events(
        result
    )

    print(
        f"Progress Events Found : "
        f"{len(events)}"
    )

    for event in events:

        print_progress_event(
            event
        )

        validate_progress_event(
            event
        )

    print()
    print("=" * 100)
    print("3.13.7 SINGLE ERROR TEST PASSED")
    print("=" * 100)


# =============================================================================
# 3.13.10
# MULTIPLE ERROR TEST
# =============================================================================

async def test_multiple_error_progress():
    """
    STEP 3.13.10

    Test progress processing for multiple selected errors.
    """

    print()
    print("=" * 100)
    print("STEP 3.13.10 - MULTIPLE ERROR PROGRESS TEST")
    print("=" * 100)

    request_id = (
        f"TEST-MULTI-{uuid.uuid4().hex[:8]}"
    )

    selected_errors = [

        build_test_error(
            error_id="TEST-PROGRESS-001",
        ),

        build_test_error(
            error_id="TEST-PROGRESS-002",
        ),

        build_test_error(
            error_id="TEST-PROGRESS-003",
        ),

    ]

    print(
        f"Request ID      : {request_id}"
    )

    print(
        f"Selected Errors : "
        f"{len(selected_errors)}"
    )

    # -------------------------------------------------------------------------
    # Build graph
    # -------------------------------------------------------------------------

    graph = build_ai_analysis_graph()

    # -------------------------------------------------------------------------
    # Initial state
    # -------------------------------------------------------------------------

    initial_state = {

        "request_id": request_id,

        "tier": "web",

        "log_type": "laravel",

        "selected_errors": selected_errors,

        "current_error_index": 0,

        "current_error": None,

        "final_results": [],

        "status": "started",

        "current_task": "initialize_analysis",

        "progress": 0,

        "messages": [],

        "error": None,
    }

    print()
    print("Starting LangGraph...")
    print()

    # -------------------------------------------------------------------------
    # Execute
    # -------------------------------------------------------------------------

    result = await graph.ainvoke(
        initial_state
    )

    # -------------------------------------------------------------------------
    # Print result
    # -------------------------------------------------------------------------

    print()
    print("=" * 100)
    print("MULTIPLE ERROR GRAPH COMPLETED")
    print("=" * 100)

    print(
        f"Final Status : "
        f"{result.get('status')}"
    )

    print(
        f"Final Progress : "
        f"{result.get('progress')}%"
    )

    print(
        f"Final Task : "
        f"{result.get('current_task')}"
    )

    final_results = result.get(
        "final_results",
        [],
    )

    print(
        f"Final Results : "
        f"{len(final_results)}"
    )

    # -------------------------------------------------------------------------
    # Validate result count
    # -------------------------------------------------------------------------

    assert len(final_results) == len(
        selected_errors
    ), (
        "Final result count does not match "
        "selected error count."
    )

    # -------------------------------------------------------------------------
    # Progress events
    # -------------------------------------------------------------------------

    events = extract_progress_events(
        result
    )

    print(
        f"Progress Events Found : "
        f"{len(events)}"
    )

    for event in events:

        print_progress_event(
            event
        )

        validate_progress_event(
            event
        )

    print()
    print("=" * 100)
    print("3.13.10 MULTIPLE ERROR TEST PASSED")
    print("=" * 100)


# =============================================================================
# MAIN
# =============================================================================

async def main():

    print()
    print("=" * 100)
    print("STEP 3.13 - PROGRESS EVENTS TEST")
    print("=" * 100)

    try:

        # ---------------------------------------------------------------------
        # Single error
        # ---------------------------------------------------------------------

        await test_single_error_progress()

        # ---------------------------------------------------------------------
        # Multiple errors
        # ---------------------------------------------------------------------

        await test_multiple_error_progress()

        print()
        print("=" * 100)
        print("ALL PROGRESS EVENT TESTS PASSED")
        print("=" * 100)

    except Exception as exc:

        print()
        print("=" * 100)
        print("PROGRESS EVENT TEST FAILED")
        print("=" * 100)

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        raise


if __name__ == "__main__":

    asyncio.run(
        main()
    )