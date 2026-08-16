"""
Automation server domain models.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AutomationServerResult:
    """
    Result of processing one configured server.
    """

    server_id: str

    status: str = "pending"

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