"""
Automation run ID generation.
"""

from datetime import datetime, timezone


def generate_run_id() -> str:
    """
    Generate a unique, human-readable automation run ID.
    """

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d-%H%M%S"
    )

    return f"RUN-{timestamp}"