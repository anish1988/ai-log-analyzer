"""
Phase 3.5 - Automation Audit Service.

Responsibilities
----------------
1. Record every automation request/response event.
2. Persist the event through the existing
   AutomationAuditRepository.
3. Persist the same event as JSONL on disk.
4. Keep database and file audit concerns behind one service.

IMPORTANT
---------
This service does NOT:
    - execute log fetching
    - execute parsing
    - execute AI analysis
    - create Jira tickets
    - update checkpoints

It only records what happened.

Existing persistence is reused:
    AutomationAuditRepository
    AutomationAuditEvent
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.automation.audit.models import (
    AutomationAuditEvent,
)

from app.automation.persistence.audit_repository import (
    AutomationAuditRepository,
)


class AutomationAuditService:
    """
    Central audit service for Phase 3 automation.

    Every automation step can call:

        await audit_service.record(...)

    The event is then written to:

        1. PostgreSQL
        2. JSONL audit file
    """

    DEFAULT_AUDIT_DIRECTORY = (
        "/app/automation_audit"
    )

    def __init__(
        self,
        repository: AutomationAuditRepository | None = None,
        audit_directory: str | Path | None = None,
    ) -> None:

        self.repository = (
            repository
            or AutomationAuditRepository()
        )

        self.audit_directory = Path(
            audit_directory
            or self.DEFAULT_AUDIT_DIRECTORY
        )

    # =====================================================================
    # PUBLIC API
    # =====================================================================

    async def record(
        self,
        *,
        run_id: str,
        step: str,
        status: str,
        server_id: str | None = None,
        log_type: str | None = None,
        message: str = "",
        request: dict[str, Any] | None = None,
        response: dict[str, Any] | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AutomationAuditEvent:
        """
        Record one automation audit event.

        The same event is persisted to:

            PostgreSQL
            JSONL file
        """

        event = AutomationAuditEvent(
            run_id=run_id,
            server_id=server_id,
            log_type=log_type,
            step=step,
            status=status,
            message=message,
            request=request or {},
            response=response or {},
            error=error,
            metadata=metadata or {},
        )

        # -------------------------------------------------------------
        # File persistence
        #
        # The JSONL audit trail is the local execution record.
        # Write it first so a temporary database failure does not
        # cause the request/response audit information to disappear.
        # -------------------------------------------------------------

        self._write_jsonl(
            event
        )

        # -------------------------------------------------------------
        # Database persistence
        #
        # PostgreSQL provides searchable/queryable audit history.
        # Let database errors propagate so the caller knows that
        # database persistence failed.
        # -------------------------------------------------------------

        await self.repository.record(
            event
        )

        return event

    # =====================================================================
    # JSONL
    # =====================================================================

    def _write_jsonl(
        self,
        event: AutomationAuditEvent,
    ) -> None:
        """
        Append one audit event to the run-specific JSONL file.

        Directory structure:

            /app/automation_audit/
                2026-08-16/
                    RUN-001.jsonl
                    RUN-002.jsonl
        """

        event_date = event.timestamp.astimezone(
            timezone.utc
        ).strftime("%Y-%m-%d")

        date_directory = (
            self.audit_directory
            / event_date
        )

        date_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            date_directory
            / f"{event.run_id}.jsonl"
        )

        payload = asdict(
            event
        )

        payload["timestamp"] = (
            event.timestamp.astimezone(
                timezone.utc
            ).isoformat()
        )

        serialized = json.dumps(
            payload,
            ensure_ascii=False,
            default=str,
        )

        with file_path.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                serialized
            )

            file.write("\n")

    # =====================================================================
    # CONVENIENCE METHODS
    # =====================================================================

    async def record_started(
        self,
        *,
        run_id: str,
        step: str,
        server_id: str | None = None,
        log_type: str | None = None,
        request: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AutomationAuditEvent:
        """
        Record the beginning of a step.
        """

        return await self.record(
            run_id=run_id,
            server_id=server_id,
            log_type=log_type,
            step=step,
            status="started",
            message=(
                f"Step '{step}' started."
            ),
            request=request,
            metadata=metadata,
        )

    async def record_completed(
        self,
        *,
        run_id: str,
        step: str,
        server_id: str | None = None,
        log_type: str | None = None,
        request: dict[str, Any] | None = None,
        response: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AutomationAuditEvent:
        """
        Record successful completion of a step.
        """

        return await self.record(
            run_id=run_id,
            server_id=server_id,
            log_type=log_type,
            step=step,
            status="completed",
            message=(
                f"Step '{step}' completed."
            ),
            request=request,
            response=response,
            metadata=metadata,
        )

    async def record_failed(
        self,
        *,
        run_id: str,
        step: str,
        error: str,
        server_id: str | None = None,
        log_type: str | None = None,
        request: dict[str, Any] | None = None,
        response: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AutomationAuditEvent:
        """
        Record a failed step.
        """

        return await self.record(
            run_id=run_id,
            server_id=server_id,
            log_type=log_type,
            step=step,
            status="failed",
            message=(
                f"Step '{step}' failed."
            ),
            request=request,
            response=response,
            error=error,
            metadata=metadata,
        )