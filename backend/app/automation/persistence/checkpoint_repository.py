"""
Persistence operations for incremental log checkpoints.
"""

from datetime import datetime
from typing import Any

from app.automation.persistence.database import (
    AutomationDatabase,
)

from app.automation.persistence.models import (
    LogCheckpoint,
)


class AutomationCheckpointRepository:
    """
    Repository for automation_checkpoints.
    """

    def __init__(
        self,
        database: AutomationDatabase | None = None,
    ) -> None:

        self.database = (
            database
            or AutomationDatabase()
        )

    async def get_checkpoint(
        self,
        *,
        server_id: str,
        log_type: str,
        file_path: str,
    ) -> LogCheckpoint | None:

        connection = await self.database.connect()

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    SELECT
                        server_id,
                        server_ip,
                        log_type,
                        file_path,
                        last_offset,
                        last_line_number,
                        file_size,
                        file_inode,
                        last_read_at

                    FROM automation_checkpoints

                    WHERE
                        server_id = %(server_id)s
                        AND log_type = %(log_type)s
                        AND file_path = %(file_path)s
                    """,
                    {
                        "server_id": server_id,
                        "log_type": log_type,
                        "file_path": file_path,
                    },
                )

                row = await cursor.fetchone()

                if row is None:
                    return None

                return LogCheckpoint(
                    server_id=row[0],
                    log_type=row[2],
                    file_path=row[3],
                    last_offset=row[4],
                    last_line_number=row[5],
                    file_size=row[6],
                    file_inode=row[7],
                    last_read_at=row[8],
                )

        finally:

            await connection.close()

    async def save_checkpoint(
        self,
        checkpoint: LogCheckpoint,
        *,
        server_ip: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        connection = await self.database.connect()

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    INSERT INTO automation_checkpoints (
                        server_id,
                        server_ip,
                        log_type,
                        file_path,
                        last_offset,
                        last_line_number,
                        file_size,
                        file_inode,
                        last_read_at,
                        metadata,
                        updated_at
                    )

                    VALUES (
                        %(server_id)s,
                        %(server_ip)s,
                        %(log_type)s,
                        %(file_path)s,
                        %(last_offset)s,
                        %(last_line_number)s,
                        %(file_size)s,
                        %(file_inode)s,
                        %(last_read_at)s,
                        %(metadata)s,
                        NOW()
                    )

                    ON CONFLICT (
                        server_id,
                        log_type,
                        file_path
                    )

                    DO UPDATE SET

                        server_ip =
                            EXCLUDED.server_ip,

                        last_offset =
                            EXCLUDED.last_offset,

                        last_line_number =
                            EXCLUDED.last_line_number,

                        file_size =
                            EXCLUDED.file_size,

                        file_inode =
                            EXCLUDED.file_inode,

                        last_read_at =
                            EXCLUDED.last_read_at,

                        metadata =
                            EXCLUDED.metadata,

                        updated_at =
                            NOW()
                    """,
                    {
                        "server_id": checkpoint.server_id,
                        "server_ip": server_ip,
                        "log_type": checkpoint.log_type,
                        "file_path": checkpoint.file_path,
                        "last_offset": checkpoint.last_offset,
                        "last_line_number": checkpoint.last_line_number,
                        "file_size": checkpoint.file_size,
                        "file_inode": checkpoint.file_inode,
                        "last_read_at": checkpoint.last_read_at,
                        "metadata": self.database.jsonb(
                                            metadata or {}
                                        ),
                    },
                )

            await connection.commit()

        finally:

            await connection.close()