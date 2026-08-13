"""
LangGraph Progress Helper.

Provides a small integration layer between LangGraph state
and the ProgressPublisher.

LangGraph nodes should use this helper instead of directly
constructing ProgressEvent objects.
"""

from typing import Any

from app.ai.progress.events import ProgressEvent, ProgressStatus
from app.ai.progress.publisher import ProgressPublisher
from app.ai.progress.tasks import get_task_label


# =============================================================================
# DEFAULT PUBLISHER
# =============================================================================

_progress_publisher = ProgressPublisher()


# =============================================================================
# GET PUBLISHER
# =============================================================================

def get_progress_publisher() -> ProgressPublisher:
    """
    Return the application-level progress publisher.

    Keeping publisher creation here prevents every LangGraph
    node from creating its own publisher instance.
    """

    return _progress_publisher


# =============================================================================
# REPORT PROGRESS
# =============================================================================

async def report_progress(
    state: dict[str, Any],
    *,
    task_id: str,
    status: ProgressStatus,
    progress: int,
    message: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> ProgressEvent:
    """
    Publish one progress event using information from
    the current LangGraph state.

    Parameters
    ----------
    state:
        Current AIAnalysisState.

    task_id:
        Stable task identifier from ProgressTasks.

    status:
        ProgressStatus value.

    progress:
        Overall request progress from 0 to 100.

    message:
        Optional human-readable message.
        If omitted, TASK_LABELS is used.

    metadata:
        Optional additional information.
    """

    # -------------------------------------------------------------------------
    # Request information
    # -------------------------------------------------------------------------

    request_id = state.get(
        "request_id",
        "unknown-request",
    )

    # -------------------------------------------------------------------------
    # Current error
    # -------------------------------------------------------------------------

    current_error = state.get(
        "current_error"
    ) or {}

    error_id = current_error.get(
        "error_id"
    )

    log_type = current_error.get(
        "log_type"
    )

    # -------------------------------------------------------------------------
    # Multiple-error information
    # -------------------------------------------------------------------------

    selected_errors = state.get(
        "selected_errors"
    ) or []

    total_errors = len(
        selected_errors
    )

    current_error_index = state.get(
        "current_error_index",
        0,
    )

    # -------------------------------------------------------------------------
    # Task name
    # -------------------------------------------------------------------------

    task_name = get_task_label(
        task_id
    )

    # -------------------------------------------------------------------------
    # Message
    # -------------------------------------------------------------------------

    if message is None:

        message = task_name

    # -------------------------------------------------------------------------
    # Publish
    # -------------------------------------------------------------------------

    publisher = get_progress_publisher()

    event = await publisher.publish(

        request_id=request_id,

        error_id=error_id,

        task_id=task_id,

        task_name=task_name,

        status=status,

        progress=progress,

        message=message,

        log_type=log_type,

        error_index=(
            current_error_index
            if (
                total_errors > 0
                and error_id is not None
            )
            else None
        ),

        total_errors=(
            total_errors
            if total_errors > 0
            else None
        ),

        metadata=metadata,
    )

    return event

def append_progress_event(
    state: dict[str, Any],
    event: ProgressEvent,
) -> list[ProgressEvent]:
    """
    Return the existing progress event history with
    the new event appended.

    The original state is never mutated.
    """

    return [
        *state.get(
            "progress_events",
            [],
        ),
        event,
    ]    