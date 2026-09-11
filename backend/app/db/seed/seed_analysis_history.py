"""Seed development analysis history data.

This seeder is intentionally independent from authentication and automation.
It loads deterministic development/demo data from analysis_history_data.json
and can safely be executed multiple times without creating duplicates.

Usage
-----

From the project root:

    python3 backend/app/db/seed/seed_analysis_history.py

Or, when running inside the backend Docker container:

    docker compose exec backend \
        python -m app.db.seed.seed_analysis_history

The seed is idempotent and can be executed multiple times safely.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import psycopg
from psycopg.types.json import Jsonb


SEED_DIRECTORY = Path(__file__).resolve().parent
DATA_FILE = SEED_DIRECTORY / "analysis_history_data.json"


def get_database_connection() -> psycopg.Connection[Any]:
    """Create a PostgreSQL connection using the application's environment."""
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv(
            "POSTGRES_DB",
            "ai_log_analyzer",
        ),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def load_seed_data() -> dict[str, Any]:
    """Load and validate the seed JSON file."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Seed data file was not found: {DATA_FILE}"
        )

    with DATA_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    required_keys = {
        "users",
        "analysis_runs",
        "analysis_results",
    }

    missing_keys = required_keys - set(data)

    if missing_keys:
        raise ValueError(
            "Seed data is missing required sections: "
            + ", ".join(sorted(missing_keys))
        )

    return data


def jsonb_value(value: Any) -> Jsonb:
    """Wrap a Python value for insertion into a PostgreSQL JSONB column."""
    return Jsonb(value)


def seed_users(
    cursor: psycopg.Cursor[Any],
    users: list[dict[str, Any]],
) -> None:
    """Insert or update development seed users."""
    for user in users:
        cursor.execute(
            """
            INSERT INTO users (
                id,
                email,
                display_name,
                role,
                auth_provider,
                provider_subject,
                password_hash,
                is_active,
                last_login_at,
                created_at,
                updated_at
            )
            VALUES (
                %(id)s,
                %(email)s,
                %(display_name)s,
                %(role)s,
                %(auth_provider)s,
                %(provider_subject)s,
                %(password_hash)s,
                %(is_active)s,
                %(last_login_at)s,
                %(created_at)s,
                %(updated_at)s
            )
            ON CONFLICT (id)
            DO UPDATE SET
                email = EXCLUDED.email,
                display_name = EXCLUDED.display_name,
                role = EXCLUDED.role,
                auth_provider = EXCLUDED.auth_provider,
                provider_subject = EXCLUDED.provider_subject,
                password_hash = EXCLUDED.password_hash,
                is_active = EXCLUDED.is_active,
                last_login_at = EXCLUDED.last_login_at,
                updated_at = EXCLUDED.updated_at
            """,
            user,
        )


def seed_analysis_runs(
    cursor: psycopg.Cursor[Any],
    runs: list[dict[str, Any]],
) -> None:
    """Insert or update analysis run seed records."""
    for run in runs:
        cursor.execute(
            """
            INSERT INTO analysis_runs (
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
            )
            VALUES (
                %(id)s,
                %(request_id)s,
                %(user_id)s,
                %(source_type)s,
                %(status)s,
                %(started_at)s,
                %(completed_at)s,
                %(total_errors)s,
                %(completed_errors)s,
                %(failed_errors)s,
                %(log_type)s,
                %(servers)s,
                %(log_files)s,
                %(custom_prompt)s,
                %(automation_run_id)s,
                %(metadata)s,
                %(error_message)s,
                %(created_at)s,
                %(updated_at)s
            )
            ON CONFLICT (id)
            DO UPDATE SET
                request_id = EXCLUDED.request_id,
                user_id = EXCLUDED.user_id,
                source_type = EXCLUDED.source_type,
                status = EXCLUDED.status,
                started_at = EXCLUDED.started_at,
                completed_at = EXCLUDED.completed_at,
                total_errors = EXCLUDED.total_errors,
                completed_errors = EXCLUDED.completed_errors,
                failed_errors = EXCLUDED.failed_errors,
                log_type = EXCLUDED.log_type,
                servers = EXCLUDED.servers,
                log_files = EXCLUDED.log_files,
                custom_prompt = EXCLUDED.custom_prompt,
                automation_run_id = EXCLUDED.automation_run_id,
                metadata = EXCLUDED.metadata,
                error_message = EXCLUDED.error_message,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at
            """,
            {
                **run,
                "servers": jsonb_value(
                    run.get("servers", [])
                ),
                "log_files": jsonb_value(
                    run.get("log_files", [])
                ),
                "metadata": jsonb_value(
                    run.get("metadata", {})
                ),
            },
        )


def seed_analysis_results(
    cursor: psycopg.Cursor[Any],
    results: list[dict[str, Any]],
) -> None:
    """Insert or update analysis result seed records."""
    for result in results:
        cursor.execute(
            """
            INSERT INTO analysis_results (
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
            )
            VALUES (
                %(id)s,
                %(analysis_run_id)s,
                %(error_id)s,
                %(error_signature)s,
                %(tier)s,
                %(log_type)s,
                %(server)s,
                %(file_name)s,
                %(file_path)s,
                %(title)s,
                %(severity)s,
                %(timestamp)s,
                %(start_line)s,
                %(end_line)s,
                %(source)s,
                %(rag_match)s,
                %(rag_knowledge_id)s,
                %(rag_similarity)s,
                %(confidence)s,
                %(analysis_status)s,
                %(error_summary)s,
                %(root_cause)s,
                %(solution)s,
                %(optimization)s,
                %(source_code_analysis)s,
                %(source_file)s,
                %(source_line_number)s,
                %(jira_description)s,
                %(jira_issue_key)s,
                %(jira_issue_id)s,
                %(jira_issue_url)s,
                %(jira_status)s,
                %(root_cause_evidence)s,
                %(test_result)s,
                %(evidence)s,
                %(source_code_location)s,
                %(missing_information)s,
                %(request_payload)s,
                %(response_payload)s,
                %(jira_payload)s,
                %(created_at)s,
                %(updated_at)s
            )
            ON CONFLICT (id)
            DO UPDATE SET
                analysis_run_id = EXCLUDED.analysis_run_id,
                error_id = EXCLUDED.error_id,
                error_signature = EXCLUDED.error_signature,
                tier = EXCLUDED.tier,
                log_type = EXCLUDED.log_type,
                server = EXCLUDED.server,
                file_name = EXCLUDED.file_name,
                file_path = EXCLUDED.file_path,
                title = EXCLUDED.title,
                severity = EXCLUDED.severity,
                timestamp = EXCLUDED.timestamp,
                start_line = EXCLUDED.start_line,
                end_line = EXCLUDED.end_line,
                source = EXCLUDED.source,
                rag_match = EXCLUDED.rag_match,
                rag_knowledge_id = EXCLUDED.rag_knowledge_id,
                rag_similarity = EXCLUDED.rag_similarity,
                confidence = EXCLUDED.confidence,
                analysis_status = EXCLUDED.analysis_status,
                error_summary = EXCLUDED.error_summary,
                root_cause = EXCLUDED.root_cause,
                solution = EXCLUDED.solution,
                optimization = EXCLUDED.optimization,
                source_code_analysis = EXCLUDED.source_code_analysis,
                source_file = EXCLUDED.source_file,
                source_line_number = EXCLUDED.source_line_number,
                jira_description = EXCLUDED.jira_description,
                jira_issue_key = EXCLUDED.jira_issue_key,
                jira_issue_id = EXCLUDED.jira_issue_id,
                jira_issue_url = EXCLUDED.jira_issue_url,
                jira_status = EXCLUDED.jira_status,
                root_cause_evidence = EXCLUDED.root_cause_evidence,
                test_result = EXCLUDED.test_result,
                evidence = EXCLUDED.evidence,
                source_code_location = EXCLUDED.source_code_location,
                missing_information = EXCLUDED.missing_information,
                request_payload = EXCLUDED.request_payload,
                response_payload = EXCLUDED.response_payload,
                jira_payload = EXCLUDED.jira_payload,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at
            """,
            {
                **result,
                "root_cause_evidence": jsonb_value(
                    result.get(
                        "root_cause_evidence",
                        [],
                    )
                ),
                "test_result": jsonb_value(
                    result.get(
                        "test_result",
                        {},
                    )
                ),
                "evidence": jsonb_value(
                    result.get(
                        "evidence",
                        [],
                    )
                ),
                "source_code_location": jsonb_value(
                    result.get(
                        "source_code_location",
                        {},
                    )
                ),
                "missing_information": jsonb_value(
                    result.get(
                        "missing_information",
                        [],
                    )
                ),
                "request_payload": jsonb_value(
                    result.get(
                        "request_payload",
                        {},
                    )
                ),
                "response_payload": jsonb_value(
                    result.get(
                        "response_payload",
                        {},
                    )
                ),
                "jira_payload": (
                    jsonb_value(
                        result["jira_payload"]
                    )
                    if result.get("jira_payload") is not None
                    else None
                ),
            },
        )


def sync_analysis_results_sequence(
    cursor: psycopg.Cursor[Any],
) -> None:
    """Synchronize the BIGSERIAL sequence with seeded result IDs."""
    cursor.execute(
        """
        SELECT setval(
            pg_get_serial_sequence(
                'analysis_results',
                'id'
            ),
            GREATEST(
                COALESCE(
                    (
                        SELECT MAX(id)
                        FROM analysis_results
                    ),
                    1
                ),
                1
            ),
            true
        )
        """
    )


def main() -> None:
    """Run the analysis history seed."""
    data = load_seed_data()

    users = data["users"]
    runs = data["analysis_runs"]
    results = data["analysis_results"]

    print("==============================================")
    print("Analysis History Seeder")
    print("==============================================")
    print(f"Users:            {len(users)}")
    print(f"Analysis runs:    {len(runs)}")
    print(f"Analysis results: {len(results)}")
    print()

    with get_database_connection() as connection:
        with connection.cursor() as cursor:
            seed_users(cursor, users)
            print("✓ Users seeded")

            seed_analysis_runs(cursor, runs)
            print("✓ Analysis runs seeded")

            seed_analysis_results(cursor, results)
            print("✓ Analysis results seeded")

            sync_analysis_results_sequence(cursor)
            print("✓ Analysis results sequence synchronized")

        connection.commit()

    print()
    print("Analysis history seed completed successfully.")


if __name__ == "__main__":
    main()