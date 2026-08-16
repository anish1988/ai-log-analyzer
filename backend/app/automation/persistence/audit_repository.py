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

