"""
Analysis history repository.

This repository provides the common persistence layer for AI analysis
history used by both manual/browser analysis and automation.

Responsibilities:
    - Create analysis run records.
    - Update analysis run status/counters.
    - Store individual analysis results.
    - Update Jira information after ticket creation.
    - Retrieve analysis runs/results for future history APIs.

IMPORTANT:
    This repository must remain independent of authentication.
    The caller is responsible for providing the appropriate user_id.
"""

import os
from datetime import datetime
from typing import Any
from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb


def _connect() -> psycopg.Connection:
    """
    Create a PostgreSQL connection for analysis-history persistence.
    """

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "ai_log_analyzer"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def create_analysis_run(
    *,
    user_id: UUID,
    request_id: str | None,
    source_type: str,
    status: str = "processing",
    started_at: datetime | None = None,
    total_errors: int = 0,
    log_type: str | None = None,
    servers: list[str] | None = None,
    log_files: list[str] | None = None,
    custom_prompt: str | None = None,
    automation_run_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> UUID:
    """
    Create one analysis-history run.

    Returns:
        UUID of the newly created analysis run.
    """

    if source_type not in {"manual", "automation"}:
        raise ValueError(
            "Analysis run source_type must be 'manual' or 'automation'."
        )

    if total_errors < 0:
        raise ValueError("total_errors cannot be negative.")

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO analysis_runs (
                    request_id,
                    user_id,
                    source_type,
                    status,
                    started_at,
                    total_errors,
                    log_type,
                    servers,
                    log_files,
                    custom_prompt,
                    automation_run_id,
                    metadata
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    COALESCE(%s, NOW()),
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
                    request_id,
                    user_id,
                    source_type,
                    status,
                    started_at,
                    total_errors,
                    log_type,
                    Jsonb(servers or []),
                    Jsonb(log_files or []),
                    custom_prompt,
                    automation_run_id,
                    Jsonb(metadata or {}),
                ),
            )

            row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "Failed to create analysis history run."
        )

    return row[0]


def mark_analysis_run_completed(
    *,
    analysis_run_id: UUID,
    completed_errors: int,
    failed_errors: int = 0,
) -> None:
    """
    Mark an analysis run as completed and store final counters.
    """

    if completed_errors < 0:
        raise ValueError("completed_errors cannot be negative.")

    if failed_errors < 0:
        raise ValueError("failed_errors cannot be negative.")

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE analysis_runs
                SET
                    status = 'completed',
                    completed_at = NOW(),
                    completed_errors = %s,
                    failed_errors = %s,
                    error_message = NULL,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    completed_errors,
                    failed_errors,
                    analysis_run_id,
                ),
            )


def mark_analysis_run_failed(
    *,
    analysis_run_id: UUID,
    error_message: str,
    completed_errors: int = 0,
    failed_errors: int = 0,
) -> None:
    """
    Mark an analysis run as failed.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE analysis_runs
                SET
                    status = 'failed',
                    completed_at = NOW(),
                    completed_errors = %s,
                    failed_errors = %s,
                    error_message = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    completed_errors,
                    failed_errors,
                    error_message,
                    analysis_run_id,
                ),
            )


def update_analysis_run_counters(
    *,
    analysis_run_id: UUID,
    completed_errors: int,
    failed_errors: int,
) -> None:
    """
    Update analysis progress counters without changing run status.
    """

    if completed_errors < 0:
        raise ValueError("completed_errors cannot be negative.")

    if failed_errors < 0:
        raise ValueError("failed_errors cannot be negative.")

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE analysis_runs
                SET
                    completed_errors = %s,
                    failed_errors = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    completed_errors,
                    failed_errors,
                    analysis_run_id,
                ),
            )


def create_analysis_result(
    *,
    analysis_run_id: UUID,
    error_id: str,
    error_signature: str | None = None,
    tier: str | None = None,
    log_type: str | None = None,
    server: str | None = None,
    file_name: str | None = None,
    file_path: str | None = None,
    title: str | None = None,
    severity: str | None = None,
    timestamp: datetime | None = None,
    start_line: int | None = None,
    end_line: int | None = None,
    source: str | None = None,
    rag_match: bool = False,
    rag_knowledge_id: int | None = None,
    rag_similarity: float | None = None,
    confidence: str | None = None,
    analysis_status: str | None = None,
    error_summary: str | None = None,
    root_cause: str | None = None,
    solution: str | None = None,
    optimization: str | None = None,
    source_code_analysis: str | None = None,
    source_file: str | None = None,
    source_line_number: int | None = None,
    jira_description: str | None = None,
    jira_issue_key: str | None = None,
    jira_issue_id: str | None = None,
    jira_issue_url: str | None = None,
    jira_status: str | None = None,
    root_cause_evidence: list[dict[str, Any]] | None = None,
    test_result: dict[str, Any] | None = None,
    evidence: list[dict[str, Any]] | None = None,
    source_code_location: dict[str, Any] | None = None,
    missing_information: list[str] | None = None,
    request_payload: dict[str, Any] | None = None,
    response_payload: dict[str, Any] | None = None,
    jira_payload: dict[str, Any] | None = None,
) -> int:
    """
    Persist one analyzed error/result.

    The normalized columns support reporting and filtering.
    JSONB payloads preserve the complete structured request/response data.

    Returns:
        Database ID of the newly created analysis result.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO analysis_results (
                    analysis_run_id,
                    error_id,
                    error_signature,
                    tier,
                    log_type,
                    server,
                    file_name,
                    file_path,
                    title,
                    severity,
                    timestamp,
                    start_line,
                    end_line,
                    source,
                    rag_match,
                    rag_knowledge_id,
                    rag_similarity,
                    confidence,
                    analysis_status,
                    error_summary,
                    root_cause,
                    solution,
                    optimization,
                    source_code_analysis,
                    source_file,
                    source_line_number,
                    jira_description,
                    jira_issue_key,
                    jira_issue_id,
                    jira_issue_url,
                    jira_status,
                    root_cause_evidence,
                    test_result,
                    evidence,
                    source_code_location,
                    missing_information,
                    request_payload,
                    response_payload,
                    jira_payload
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    analysis_run_id,
                    error_id,
                    error_signature,
                    tier,
                    log_type,
                    server,
                    file_name,
                    file_path,
                    title,
                    severity,
                    timestamp,
                    start_line,
                    end_line,
                    source,
                    rag_match,
                    rag_knowledge_id,
                    rag_similarity,
                    confidence,
                    analysis_status,
                    error_summary,
                    root_cause,
                    solution,
                    optimization,
                    source_code_analysis,
                    source_file,
                    source_line_number,
                    jira_description,
                    jira_issue_key,
                    jira_issue_id,
                    jira_issue_url,
                    jira_status,
                    Jsonb(root_cause_evidence or []),
                    Jsonb(test_result or {}),
                    Jsonb(evidence or []),
                    Jsonb(source_code_location or {}),
                    Jsonb(missing_information or []),
                    Jsonb(request_payload or {}),
                    Jsonb(response_payload or {}),
                    Jsonb(jira_payload)
                    if jira_payload is not None
                    else None,
                ),
            )

            row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "Failed to create analysis history result."
        )

    return row[0]


def update_analysis_result_jira(
    *,
    result_id: int,
    jira_issue_key: str | None,
    jira_issue_id: str | None,
    jira_issue_url: str | None,
    jira_status: str | None,
    jira_payload: dict[str, Any] | None = None,
) -> bool:
    """
    Update Jira information for an existing analysis result.

    Jira creation happens separately from the initial AI analysis,
    therefore Jira fields are intentionally updateable after persistence.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE analysis_results
                SET
                    jira_issue_key = %s,
                    jira_issue_id = %s,
                    jira_issue_url = %s,
                    jira_status = %s,
                    jira_payload = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    jira_issue_key,
                    jira_issue_id,
                    jira_issue_url,
                    jira_status,
                    Jsonb(jira_payload)
                    if jira_payload is not None
                    else None,
                    result_id,
                ),
            )

            return cursor.rowcount > 0


def get_analysis_runs(
    *,
    user_id: UUID,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """
    Return analysis-history runs belonging to one user.

    Results are ordered newest first.
    """

    if limit < 1:
        raise ValueError("limit must be greater than zero.")

    if offset < 0:
        raise ValueError("offset cannot be negative.")

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    request_id,
                    user_id,
                    source_type,
                    status,
                    started_at,
                    completed_at,
                    total_errors,
                    completed_errors,
                    failed_errors,
                    log_type,
                    servers,
                    log_files,
                    custom_prompt,
                    automation_run_id,
                    metadata,
                    error_message,
                    created_at,
                    updated_at
                FROM analysis_runs
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                OFFSET %s
                """,
                (
                    user_id,
                    limit,
                    offset,
                ),
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "request_id": row[1],
            "user_id": row[2],
            "source_type": row[3],
            "status": row[4],
            "started_at": row[5],
            "completed_at": row[6],
            "total_errors": row[7],
            "completed_errors": row[8],
            "failed_errors": row[9],
            "log_type": row[10],
            "servers": row[11],
            "log_files": row[12],
            "custom_prompt": row[13],
            "automation_run_id": row[14],
            "metadata": row[15],
            "error_message": row[16],
            "created_at": row[17],
            "updated_at": row[18],
        }
        for row in rows
    ]

def get_analysis_run(
    *,
    analysis_run_id: UUID,
    user_id: UUID,
) -> dict[str, Any] | None:
    """
    Return one analysis run by ID.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    request_id,
                    user_id,
                    source_type,
                    status,
                    started_at,
                    completed_at,
                    total_errors,
                    completed_errors,
                    failed_errors,
                    log_type,
                    servers,
                    log_files,
                    custom_prompt,
                    automation_run_id,
                    metadata,
                    error_message,
                    created_at,
                    updated_at
                FROM analysis_runs
                WHERE id = %s
                    AND user_id = %s
                LIMIT 1
                """,
                (
                    analysis_run_id,
                    user_id,
                ),
            )

            row = cursor.fetchone()

    if row is None:
        return None

    return {
        "id": row[0],
        "request_id": row[1],
        "user_id": row[2],
        "source_type": row[3],
        "status": row[4],
        "started_at": row[5],
        "completed_at": row[6],
        "total_errors": row[7],
        "completed_errors": row[8],
        "failed_errors": row[9],
        "log_type": row[10],
        "servers": row[11],
        "log_files": row[12],
        "custom_prompt": row[13],
        "automation_run_id": row[14],
        "metadata": row[15],
        "error_message": row[16],
        "created_at": row[17],
        "updated_at": row[18],
    }


def get_analysis_results(
    *,
    analysis_run_id: UUID,
) -> list[dict[str, Any]]:
    """
    Return all analyzed results belonging to one analysis run.
    """

    with _connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    analysis_run_id,
                    error_id,
                    error_signature,
                    tier,
                    log_type,
                    server,
                    file_name,
                    file_path,
                    title,
                    severity,
                    timestamp,
                    start_line,
                    end_line,
                    source,
                    rag_match,
                    rag_knowledge_id,
                    rag_similarity,
                    confidence,
                    analysis_status,
                    error_summary,
                    root_cause,
                    solution,
                    optimization,
                    source_code_analysis,
                    source_file,
                    source_line_number,
                    jira_description,
                    jira_issue_key,
                    jira_issue_id,
                    jira_issue_url,
                    jira_status,
                    root_cause_evidence,
                    test_result,
                    evidence,
                    source_code_location,
                    missing_information,
                    request_payload,
                    response_payload,
                    jira_payload,
                    created_at,
                    updated_at
                FROM analysis_results
                WHERE analysis_run_id = %s
                ORDER BY id ASC
                """,
                (analysis_run_id,),
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "analysis_run_id": row[1],
            "error_id": row[2],
            "error_signature": row[3],
            "tier": row[4],
            "log_type": row[5],
            "server": row[6],
            "file_name": row[7],
            "file_path": row[8],
            "title": row[9],
            "severity": row[10],
            "timestamp": row[11],
            "start_line": row[12],
            "end_line": row[13],
            "source": row[14],
            "rag_match": row[15],
            "rag_knowledge_id": row[16],
            "rag_similarity": row[17],
            "confidence": row[18],
            "analysis_status": row[19],
            "error_summary": row[20],
            "root_cause": row[21],
            "solution": row[22],
            "optimization": row[23],
            "source_code_analysis": row[24],
            "source_file": row[25],
            "source_line_number": row[26],
            "jira_description": row[27],
            "jira_issue_key": row[28],
            "jira_issue_id": row[29],
            "jira_issue_url": row[30],
            "jira_status": row[31],
            "root_cause_evidence": row[32],
            "test_result": row[33],
            "evidence": row[34],
            "source_code_location": row[35],
            "missing_information": row[36],
            "request_payload": row[37],
            "response_payload": row[38],
            "jira_payload": row[39],
            "created_at": row[40],
            "updated_at": row[41],
        }
        for row in rows
    ]