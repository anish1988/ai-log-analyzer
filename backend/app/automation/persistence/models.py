"""
Automation persistence domain models.

Checkpoint state is intentionally separate from run history.

Run history answers:
    What happened during a run?

Checkpoint state answers:
    Where should the next run continue reading?
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class LogCheckpoint:
    """
    Persistent position of one log source.
    """

    server_id: str

    log_type: str

    file_path: str

    last_offset: int = 0

    last_line_number: int = 0

    file_size: int = 0

    file_inode: int | None = None

    last_read_at: datetime | None = None