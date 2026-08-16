"""
Automation audit models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class AutomationAuditEvent:
    """
    One auditable event during an automation run.
    """

    run_id: str

    step: str

    status: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    server_id: str | None = None

    log_type: str | None = None

    message: str = ""

    request: dict[str, Any] = field(
        default_factory=dict
    )

    response: dict[str, Any] = field(
        default_factory=dict
    )

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )