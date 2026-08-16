"""
Persistence operations for automation audit events.
"""

from app.automation.audit.models import (
    AutomationAuditEvent,
)

from app.automation.persistence.database import (
    AutomationDatabase,
)


class AutomationAuditRepository:
    """
    Repository for automation_audit_events.
    """

    def __init__(
        self,
        database: AutomationDatabase | None = None,
    ) -> None:

        self.database = (
            database
            or AutomationDatabase()
        )

    async def record(
        self,
        event: AutomationAuditEvent,
    ) -> None:

        connection = await self.database.connect()

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    INSERT INTO automation_audit_events (
                        run_id,
                        server_id,
                        log_type,
                        step,
                        status,
                        timestamp,
                        message,
                        request,
                        response,
                        error,
                        metadata
                    )

                    VALUES (
                        %(run_id)s,
                        %(server_id)s,
                        %(log_type)s,
                        %(step)s,
                        %(status)s,
                        %(timestamp)s,
                        %(message)s,
                        %(request)s,
                        %(response)s,
                        %(error)s,
                        %(metadata)s
                    )
                    """,
                    {
                        "run_id": event.run_id,
                        "server_id": event.server_id,
                        "log_type": event.log_type,
                        "step": event.step,
                        "status": event.status,
                        "timestamp": event.timestamp,
                        "message": event.message,
                        "request": self.database.jsonb(
                            event.request
                        ),
                        "response": self.database.jsonb(
                            event.response
                        ),
                        "error": event.error,
                        "metadata": self.database.jsonb(
                            event.metadata
                        ),
                    },
                )

            await connection.commit()

        finally:

            await connection.close()


await audit_repository.record(
    AutomationAuditEvent(
        run_id=run_id,
        server_id=result.server_id,
        log_type=result.log_type,
        step="log_fetch",
        status="completed",
        message="Incremental log fetch completed.",
        request={
            "file": result.file_path,
            "previous_line": result.previous_line,
            "previous_offset": result.previous_offset,
        },
        response={
            "start_line": result.start_line,
            "end_line": result.end_line,
            "start_offset": result.start_offset,
            "end_offset": result.end_offset,
            "lines_read": result.lines_read,
            "has_new_data": result.has_new_data,
            "rotated": result.rotated,
            "truncated": result.truncated,
        },
        metadata={
            "phase": "3.3",
            "reader": "IncrementalLogReader",
        },
    )
)        