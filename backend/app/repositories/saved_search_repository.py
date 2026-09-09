"""
Phase 4 - Saved Search Repository.

This repository handles persistence for user-created saved searches.

Important:
    A record is created ONLY when the user explicitly chooses
    "Save Search".

    Normal searches do NOT use this repository.

    Automation does NOT use this repository.
"""

import os
from datetime import date
from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb


def _connect() -> psycopg.Connection:
    """
    Create a PostgreSQL connection for saved-search persistence.
    """

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ai_log_analyzer"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def create_saved_search(
    *,
    user_id: UUID,
    name: str,
    description: str | None,
    from_date: date,
    to_date: date,
    tier: str,
    servers: list[str],
    search_filters: dict,
) -> int:
    """
    Create a saved search owned by the specified user.

    user_id is supplied by the backend current-user context.
    It must never come from an untrusted frontend user_id field.

    Returns:
        Database ID of the newly created saved search.
    """

    if not name.strip():
        raise ValueError("Saved search name is required.")

    if to_date < from_date:
        raise ValueError(
            "Saved search end date cannot be before start date."
        )

    with _connect() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO saved_searches (
                    user_id,
                    name,
                    description,
                    from_date,
                    to_date,
                    tier,
                    servers,
                    search_filters
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id
                """,
                (
                    user_id,
                    name.strip(),
                    description.strip()
                    if description
                    else None,
                    from_date,
                    to_date,
                    tier,
                    Jsonb(servers),
                    Jsonb(search_filters),
                ),
            )

            row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "Failed to create saved search."
        )

    return row[0]


def get_user_saved_searches(
    *,
    user_id: UUID,
) -> list[dict]:
    """
    Return only saved searches belonging to the current user.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    user_id,
                    name,
                    description,
                    from_date,
                    to_date,
                    tier,
                    servers,
                    search_filters,
                    created_at,
                    updated_at
                FROM saved_searches
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "description": row[3],
            "from_date": row[4],
            "to_date": row[5],
            "tier": row[6],
            "servers": row[7],
            "search_filters": row[8],
            "created_at": row[9],
            "updated_at": row[10],
        }
        for row in rows
    ]


def get_saved_search(
    *,
    user_id: UUID,
    saved_search_id: int,
) -> dict | None:
    """
    Return one saved search only if it belongs to the current user.

    This ownership check is deliberately performed in SQL.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    user_id,
                    name,
                    description,
                    from_date,
                    to_date,
                    tier,
                    servers,
                    search_filters,
                    created_at,
                    updated_at
                FROM saved_searches
                WHERE id = %s
                  AND user_id = %s
                LIMIT 1
                """,
                (
                    saved_search_id,
                    user_id,
                ),
            )

            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "name": row[2],
        "description": row[3],
        "from_date": row[4],
        "to_date": row[5],
        "tier": row[6],
        "servers": row[7],
        "search_filters": row[8],
        "created_at": row[9],
        "updated_at": row[10],
    }


def update_saved_search(
    *,
    user_id: UUID,
    saved_search_id: int,
    name: str,
    description: str | None,
    from_date: date,
    to_date: date,
    tier: str,
    servers: list[str],
    search_filters: dict,
) -> bool:
    """
    Update a saved search belonging to the current user.

    Returns:
        True if a record was updated, otherwise False.
    """

    if not name.strip():
        raise ValueError("Saved search name is required.")

    if to_date < from_date:
        raise ValueError(
            "Saved search end date cannot be before start date."
        )

    with _connect() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE saved_searches
                SET
                    name = %s,
                    description = %s,
                    from_date = %s,
                    to_date = %s,
                    tier = %s,
                    servers = %s,
                    search_filters = %s,
                    updated_at = NOW()
                WHERE id = %s
                  AND user_id = %s
                """,
                (
                    name.strip(),
                    description.strip()
                    if description
                    else None,
                    from_date,
                    to_date,
                    tier,
                    Jsonb(servers),
                    Jsonb(search_filters),
                    saved_search_id,
                    user_id,
                ),
            )

            return cursor.rowcount > 0


def delete_saved_search(
    *,
    user_id: UUID,
    saved_search_id: int,
) -> bool:
    """
    Delete a saved search belonging to the current user.

    Returns:
        True if a record was deleted, otherwise False.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM saved_searches
                WHERE id = %s
                  AND user_id = %s
                """,
                (
                    saved_search_id,
                    user_id,
                ),
            )

            return cursor.rowcount > 0