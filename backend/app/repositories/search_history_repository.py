"""
Phase 4 - Search history persistence.

This repository belongs to the interactive/manual portal flow.

IMPORTANT:
    The Phase 3 automation pipeline must not use this repository.
"""

import os
from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb

from app.schemas.log_analysis import SearchFiltersRequest


def _connect() -> psycopg.Connection:
    """
    Create a PostgreSQL connection for Phase 4 portal persistence.
    """

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ai_log_analyzer"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def _build_search_filters(
    request: SearchFiltersRequest,
) -> dict:
    """
    Store only the actual search parameters.

    user_id is intentionally NOT taken from the request.
    """

    return {
        "leadId": request.lead_id,
        "campaignId": request.campaign_id,
        "uniqueId": request.unique_id,
        "callerId": request.caller_id,
        "callerNumber": request.caller_number,
        "agent": request.agent,
        "inboundGroup": request.inbound_group,
        "logType": request.log_type,
        "defaultLogPath": request.default_path,
        "customLogPath": request.custom_path,
    }


def create_search_history(
    *,
    user_id: UUID,
    request: SearchFiltersRequest,
) -> UUID:
    """
    Create one manual search-history record.

    The initial status is 'started'.

    Returns:
        search_id
    """

    search_filters = _build_search_filters(request)

    with _connect() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO search_history (
                    user_id,
                    from_date,
                    to_date,
                    tier,
                    servers,
                    search_filters,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    'started'
                )
                RETURNING search_id
                """,
                (
                    user_id,
                    request.from_,
                    request.to,
                    request.tier,
                    Jsonb(request.servers),
                    Jsonb(search_filters),
                ),
            )

            row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "Failed to create search history record."
        )

    return row[0]


def mark_search_completed(
    *,
    search_id: UUID,
    total_results: int,
) -> None:
    """
    Mark a manual search as successfully completed.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE search_history
                SET
                    status = 'completed',
                    total_results = %s,
                    error_message = NULL,
                    updated_at = NOW()
                WHERE search_id = %s
                """,
                (
                    total_results,
                    search_id,
                ),
            )


def mark_search_failed(
    *,
    search_id: UUID,
    error_message: str,
) -> None:
    """
    Mark a manual search as failed.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE search_history
                SET
                    status = 'failed',
                    error_message = %s,
                    updated_at = NOW()
                WHERE search_id = %s
                """,
                (
                    error_message,
                    search_id,
                ),
            )