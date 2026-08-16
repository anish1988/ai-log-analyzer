"""
Phase 3.3 - Incremental Log Reader.

Responsibilities:
    1. Load the last checkpoint.
    2. Inspect the current log file.
    3. Detect rotation/truncation.
    4. Read only newly appended data.
    5. Return the new lines and the information required
       to create the next checkpoint.

IMPORTANT:
    This class does NOT save the checkpoint.

The checkpoint must only be saved after the complete downstream
processing succeeds.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.automation.persistence.checkpoint_repository import (
    AutomationCheckpointRepository,
)
from app.automation.persistence.models import LogCheckpoint
from app.config.servers import ServerConfig
from app.log_fetchers.web_log_fetcher import (
    read_web_log_incremental,
)


@dataclass
class IncrementalReadResult:
    """
    Result returned by IncrementalLogReader.

    The caller can use this object for:
        - parsing
        - auditing
        - processing
        - checkpoint creation
    """

    server_id: str
    log_type: str
    file_path: str

    lines: list[str]

    start_line: int
    end_line: int

    start_offset: int
    end_offset: int

    previous_line: int
    previous_offset: int

    file_size: int
    file_inode: Optional[int]

    rotated: bool
    truncated: bool

    has_new_data: bool

    @property
    def lines_read(self) -> int:
        return len(self.lines)


class IncrementalLogReader:
    """
    Phase 3.3 incremental reader.

    One checkpoint is maintained for:

        server + log_type + file_path

    Example:

        web-01
        apache_error
        /var/log/apache2/error.log
    """

    def __init__(
        self,
        checkpoint_repository: AutomationCheckpointRepository | None = None,
    ) -> None:

        self.checkpoint_repository = (
            checkpoint_repository
            or AutomationCheckpointRepository()
        )

    async def read(
        self,
        *,
        server: ServerConfig,
        log_type: str,
        file_path: str,
    ) -> IncrementalReadResult:

        # ---------------------------------------------------------
        # STEP 1
        # Load previous checkpoint
        # ---------------------------------------------------------

        checkpoint = await self.checkpoint_repository.get_checkpoint(
            server_id=server.id,
            log_type=log_type,
            file_path=file_path,
        )

        # ---------------------------------------------------------
        # STEP 2
        # Read only the required portion of the file
        #
        # The fetcher also determines:
        #   - current file size
        #   - current inode
        #   - rotation
        #   - truncation
        # ---------------------------------------------------------

        fetch_result = await read_web_log_incremental(
            server=server,
            log_path=file_path,
            checkpoint=checkpoint,
        )

        # ---------------------------------------------------------
        # STEP 3
        # Build normalized result
        # ---------------------------------------------------------

        return IncrementalReadResult(
            server_id=server.id,
            log_type=log_type,
            file_path=file_path,
            lines=fetch_result["lines"],
            start_line=fetch_result["start_line"],
            end_line=fetch_result["end_line"],
            start_offset=fetch_result["start_offset"],
            end_offset=fetch_result["end_offset"],
            previous_line=(
                checkpoint.last_line_number
                if checkpoint
                else 0
            ),
            previous_offset=(
                checkpoint.last_offset
                if checkpoint
                else 0
            ),
            file_size=fetch_result["file_size"],
            file_inode=fetch_result["file_inode"],
            rotated=fetch_result["rotated"],
            truncated=fetch_result["truncated"],
            has_new_data=bool(fetch_result["lines"]),
        )

    @staticmethod
    def build_checkpoint(
        result: IncrementalReadResult,
    ) -> LogCheckpoint:
        """
        Build the checkpoint that should be persisted AFTER
        successful processing.

        This method does not write to PostgreSQL.
        """

        return LogCheckpoint(
            server_id=result.server_id,
            log_type=result.log_type,
            file_path=result.file_path,
            last_offset=result.end_offset,
            last_line_number=result.end_line,
            file_size=result.file_size,
            file_inode=result.file_inode,
            last_read_at=None,
        )