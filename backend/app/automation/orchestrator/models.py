"""
Automation run domain models.

These models are intentionally independent of FastAPI/frontend code.

They represent one automated execution and can later be used by:

- Cron
- REST API
- Frontend run history
- Manual "Run Now"
- Monitoring
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AutomationRun:
    """
    Represents one complete automation execution.
    """

    run_id: str

    status: str = "running"

    started_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    completed_at: datetime | None = None

    servers_total: int = 0

    servers_processed: int = 0

    logs_total: int = 0

    logs_processed: int = 0

    lines_read: int = 0

    errors_detected: int = 0

    analyses_completed: int = 0

    jira_tickets_created: int = 0

    jira_tickets_failed: int = 0

    error_message: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def complete(self) -> None:
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)

    def fail(
        self,
        message: str,
    ) -> None:
        self.status = "failed"
        self.error_message = message
        self.completed_at = datetime.now(timezone.utc)