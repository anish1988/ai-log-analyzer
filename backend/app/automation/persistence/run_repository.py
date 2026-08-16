"""
Persistence operations for automation runs.
"""

from datetime import datetime
from typing import Any

from app.automation.persistence.database import (
    AutomationDatabase,
)


class AutomationRunRepository:
    """
    Repository for automation_runs.
    """

    def __init__(
        self,
        database: AutomationDatabase | None = None,
    ) -> None:

        self.database = (
            database
            or AutomationDatabase()
        )

    async def create_run(
        self,
        *,
        run_id: str,
        servers_total: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        connection = await self.database.connect()

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    INSERT INTO automation_runs (
                        run_id,
                        status,
                        servers_total,
                        metadata
                    )
                    VALUES (
                        %(run_id)s,
                        'running',
                        %(servers_total)s,
                        %(metadata)s
                    )
                    """,
                    {
                        "run_id": run_id,
                        "servers_total": servers_total,
                        "metadata": self.database.jsonb(
                                        metadata or {}
                                    ),
                    },
                )

            await connection.commit()

        finally:

            await connection.close()

    async def complete_run(
        self,
        *,
        run_id: str,
        servers_processed: int,
        logs_processed: int,
        lines_read: int,
        errors_detected: int,
        analyses_completed: int,
        jira_tickets_created: int,
        jira_tickets_failed: int,
    ) -> None:

        connection = await self.database.connect()

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    UPDATE automation_runs

                    SET
                        status = 'completed',
                        completed_at = NOW(),
                        servers_processed = %(servers_processed)s,
                        logs_processed = %(logs_processed)s,
                        lines_read = %(lines_read)s,
                        errors_detected = %(errors_detected)s,
                        analyses_completed = %(analyses_completed)s,
                        jira_tickets_created = %(jira_tickets_created)s,
                        jira_tickets_failed = %(jira_tickets_failed)s,
                        updated_at = NOW()

                    WHERE run_id = %(run_id)s
                    """,
                    {
                        "run_id": run_id,
                        "servers_processed": servers_processed,
                        "logs_processed": logs_processed,
                        "lines_read": lines_read,
                        "errors_detected": errors_detected,
                        "analyses_completed": analyses_completed,
                        "jira_tickets_created": jira_tickets_created,
                        "jira_tickets_failed": jira_tickets_failed,
                    },
                )

            await connection.commit()

        finally:

            await connection.close()

    async def fail_run(
        self,
        *,
        run_id: str,
        error_message: str,
    ) -> None:

        connection = await self.database.connect()

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    UPDATE automation_runs

                    SET
                        status = 'failed',
                        completed_at = NOW(),
                        error_message = %(error_message)s,
                        updated_at = NOW()

                    WHERE run_id = %(run_id)s
                    """,
                    {
                        "run_id": run_id,
                        "error_message": error_message,
                    },
                )

            await connection.commit()

        finally:

            await connection.close()

    async def get_run(
        self,
        run_id: str,
    ) -> dict[str, Any] | None:

        connection = await self.database.connect()

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    SELECT
                        run_id,
                        status,
                        started_at,
                        completed_at,
                        servers_total,
                        servers_processed,
                        logs_total,
                        logs_processed,
                        lines_read,
                        errors_detected,
                        analyses_completed,
                        jira_tickets_created,
                        jira_tickets_failed,
                        error_message,
                        metadata,
                        created_at,
                        updated_at

                    FROM automation_runs

                    WHERE run_id = %(run_id)s
                    """,
                    {
                        "run_id": run_id,
                    },
                )

                row = await cursor.fetchone()

                if row is None:
                    return None

                columns = [
                    "run_id",
                    "status",
                    "started_at",
                    "completed_at",
                    "servers_total",
                    "servers_processed",
                    "logs_total",
                    "logs_processed",
                    "lines_read",
                    "errors_detected",
                    "analyses_completed",
                    "jira_tickets_created",
                    "jira_tickets_failed",
                    "error_message",
                    "metadata",
                    "created_at",
                    "updated_at",
                ]

                return dict(
                    zip(
                        columns,
                        row,
                    )
                )

        finally:

            await connection.close()