"""
Phase 4 - Current user development context.

Authentication is NOT implemented here.

This module provides a development-only current-user context so that
Phase 4 user-owned data can start storing user_id without coupling
the application to a real authentication provider.

Real authentication will be implemented in Phase 4.13:
    - Local Sign-In
    - Google
    - Enterprise SSO
"""

import os
from dataclasses import dataclass
from uuid import UUID

import psycopg
from fastapi import Depends, HTTPException, Request


@dataclass(frozen=True)
class CurrentUser:
    """
    Represents the authenticated/development user used by the
    application layer.
    """

    id: UUID
    email: str
    display_name: str | None
    role: str


def _get_database_connection() -> psycopg.Connection:
    """
    Create a synchronous PostgreSQL connection for the lightweight
    current-user lookup.

    This is intentionally separate from the Phase 3 automation
    persistence layer.
    """

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ai_log_analyzer"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def _get_development_user() -> CurrentUser:
    """
    Resolve the development user.

    The default development identity is dev-user@local.

    This function is only valid when APP_ENV=development.
    """

    email = os.getenv(
        "DEV_USER_EMAIL",
        "dev-user@local",
    )

    with _get_database_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    email,
                    display_name,
                    role
                FROM users
                WHERE email = %s
                  AND is_active = TRUE
                LIMIT 1
                """,
                (email,),
            )

            row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Development user was not found. "
                "Run the Phase 4 user migration first."
            ),
        )

    return CurrentUser(
        id=row[0],
        email=row[1],
        display_name=row[2],
        role=row[3],
    )


async def get_current_user(
    request: Request,
) -> CurrentUser:
    """
    Resolve the current application user.

    Phase 4.1 / development behaviour:
        APP_ENV=development
            -> use DEV_USER_EMAIL

    Production behaviour:
        Authentication is required.

    Real authentication will replace this development path in
    Phase 4.13.
    """

    app_env = os.getenv(
        "APP_ENV",
        "development",
    ).lower()

    if app_env == "development":
        return _get_development_user()

    raise HTTPException(
        status_code=401,
        detail="Authentication is required.",
    )


CurrentUserDependency = Depends(get_current_user)
