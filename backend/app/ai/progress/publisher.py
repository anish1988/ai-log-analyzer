"""
AI Analysis Progress Publisher.

The publisher converts progress information into
ProgressEvent objects and sends them to an optional
callback.

The publisher is intentionally transport-independent.

Future transport options:

    ProgressPublisher
          |
          +--> In-memory callback
          |
          +--> SSE
          |
          +--> Redis Pub/Sub
          |
          +--> WebSocket
"""

from collections.abc import Awaitable, Callable
from typing import Any

from app.ai.progress.events import (
    ProgressEvent,
    ProgressStatus,
)


# =============================================================================
# CALLBACK TYPE
# =============================================================================

ProgressCallback = Callable[
    [ProgressEvent],
    Any,
]


# =============================================================================
# PROGRESS PUBLISHER
# =============================================================================

class ProgressPublisher:
    """
    Publishes AI analysis progress events.

    Parameters
    ----------
    callback:
        Optional callback that receives every ProgressEvent.

        It may be either:

            sync:
                def callback(event): ...

        or:

            async:
                async def callback(event): ...

    If no callback is provided, the publisher will still
    create and print the event. This is useful during
    development and testing.
    """

    def __init__(
        self,
        callback: ProgressCallback | None = None,
    ) -> None:

        self.callback = callback

    # =========================================================================
    # PUBLISH
    # =========================================================================

    async def publish(
        self,
        *,
        request_id: str,
        task_id: str,
        task_name: str,
        status: ProgressStatus,
        progress: int,
        message: str,
        error_id: str | None = None,
        log_type: str | None = None,
        error_index: int | None = None,
        total_errors: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProgressEvent:
        """
        Create and publish one ProgressEvent.

        Returns
        -------
        ProgressEvent
            The event that was published.
        """

        # ---------------------------------------------------------------------
        # Validate progress
        # ---------------------------------------------------------------------

        if progress < 0 or progress > 100:

            raise ValueError(
                "Progress must be between 0 and 100."
            )

        # ---------------------------------------------------------------------
        # Validate multiple-error information
        # ---------------------------------------------------------------------

        if error_index is not None:

            if error_index < 0:

                raise ValueError(
                    "error_index cannot be negative."
                )

        if total_errors is not None:

            if total_errors < 1:

                raise ValueError(
                    "total_errors must be greater than zero."
                )

        if (
            error_index is not None
            and total_errors is not None
            and error_index >= total_errors
        ):

            raise ValueError(
                "error_index must be less than total_errors."
            )

        # ---------------------------------------------------------------------
        # Create event
        # ---------------------------------------------------------------------

        event = ProgressEvent(

            request_id=request_id,

            error_id=error_id,

            task_id=task_id,

            task_name=task_name,

            status=status,

            progress=progress,

            message=message,

            log_type=log_type,

            error_index=error_index,

            total_errors=total_errors,

            metadata=metadata or {},
        )

        # ---------------------------------------------------------------------
        # Development logging
        # ---------------------------------------------------------------------

        print()
        print("=" * 100)
        print("AI PROGRESS EVENT")
        print("=" * 100)

        print(
            f"Request ID : {event.request_id}"
        )

        print(
            f"Error ID   : {event.error_id}"
        )

        print(
            f"Error      : "
            f"{event.error_index} / "
            f"{event.total_errors}"
        )

        print(
            f"Task ID    : {event.task_id}"
        )

        print(
            f"Task Name  : {event.task_name}"
        )

        print(
            f"Status     : {event.status.value}"
        )

        print(
            f"Progress   : {event.progress}%"
        )

        print(
            f"Message    : {event.message}"
        )

        print(
            f"Log Type   : {event.log_type}"
        )

        # ---------------------------------------------------------------------
        # Publish through callback
        # ---------------------------------------------------------------------

        if self.callback is not None:

            result = self.callback(
                event
            )

            # Support both:

            #     callback(event)

            # and:

            #     await callback(event)

            if isinstance(
                result,
                Awaitable,
            ):

                await result

        return event