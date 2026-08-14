"""
AI Analysis Progress Publisher.

The publisher converts progress information into
ProgressEvent objects and sends them to:

    1. Existing callback
    2. Real-time subscribers

The publisher remains transport-independent.

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

import asyncio

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

    Supports:

        - Optional callback
        - Real-time request-specific subscribers

    Subscribers are keyed by request_id so that progress from
    one AI analysis request is never sent to another request.
    """

    def __init__(
        self,
        callback: ProgressCallback | None = None,
    ) -> None:

        self.callback = callback

        # ---------------------------------------------------------------------
        # Real-time subscribers
        #
        # request_id -> set of asyncio.Queue
        #
        # Multiple clients may subscribe to the same request.
        # ---------------------------------------------------------------------

        self._subscribers: dict[
            str,
            set[asyncio.Queue[ProgressEvent]],
        ] = {}

        self._subscriber_lock = asyncio.Lock()

    # =========================================================================
    # SUBSCRIBE
    # =========================================================================

    async def subscribe(
        self,
        request_id: str,
    ) -> asyncio.Queue[ProgressEvent]:
        """
        Subscribe to progress events for one request.

        Returns
        -------
        asyncio.Queue
            Queue receiving ProgressEvent objects belonging
            to the supplied request_id.
        """

        queue: asyncio.Queue[
            ProgressEvent
        ] = asyncio.Queue()

        async with self._subscriber_lock:

            subscribers = self._subscribers.setdefault(
                request_id,
                set(),
            )

            subscribers.add(queue)

        return queue

    # =========================================================================
    # UNSUBSCRIBE
    # =========================================================================

    async def unsubscribe(
        self,
        request_id: str,
        queue: asyncio.Queue[ProgressEvent],
    ) -> None:
        """
        Remove one subscriber from a request.
        """

        async with self._subscriber_lock:

            subscribers = self._subscribers.get(
                request_id
            )

            if not subscribers:
                return

            subscribers.discard(queue)

            if not subscribers:

                self._subscribers.pop(
                    request_id,
                    None,
                )

    # =========================================================================
    # PUBLISH TO SUBSCRIBERS
    # =========================================================================

    async def _publish_to_subscribers(
        self,
        event: ProgressEvent,
    ) -> None:
        """
        Send the event to all subscribers listening
        to this event's request_id.
        """

        async with self._subscriber_lock:

            subscribers = list(
                self._subscribers.get(
                    event.request_id,
                    set(),
                )
            )

        for queue in subscribers:

            await queue.put(
                event
            )

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

        The event is delivered to:

            1. Real-time subscribers
            2. Existing callback

        The existing callback behaviour is preserved.
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
        # Real-time subscribers
        # ---------------------------------------------------------------------

        await self._publish_to_subscribers(
            event
        )

        # ---------------------------------------------------------------------
        # Existing callback
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