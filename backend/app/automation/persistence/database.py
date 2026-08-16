"""
Automation database connection management.
"""

import os

import psycopg
from psycopg.types.json import Jsonb


class AutomationDatabase:
    """
    PostgreSQL connection factory for automation services.
    """

    def __init__(self) -> None:

        self.host = os.getenv(
            "POSTGRES_HOST",
            "postgres",
        )

        self.port = int(
            os.getenv(
                "POSTGRES_PORT",
                "5432",
            )
        )

        self.database = os.getenv(
            "POSTGRES_DB",
            "ai_log_analyzer",
        )

        self.user = os.getenv(
            "POSTGRES_USER",
            "postgres",
        )

        self.password = os.getenv(
            "POSTGRES_PASSWORD",
            "postgres",
        )

    @staticmethod
    def jsonb(
        value: dict | list | None,
    ) -> Jsonb:

        return Jsonb(
            value if value is not None else {}
        )

    async def connect(
        self,
    ) -> psycopg.AsyncConnection:

        return await psycopg.AsyncConnection.connect(
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.user,
            password=self.password,
        )