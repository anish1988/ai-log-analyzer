"""
STEP 3.13.8 - RAG REUSE PROGRESS PATH TEST

Purpose
-------
Validate that when a highly similar, verified and resolved
historical RAG knowledge item exists:

    RAG Retrieval
        ↓
    RAG Decision
        ↓
    REUSE
        ↓
    Historical Solution
        ↓
    Finalize

The test MUST NOT call the LLM.

Important
---------
The test uses the SAME build_embedding_text() function used
by the production LangGraph workflow.

This guarantees that the historical test knowledge and the
current LangGraph error use the same embedding representation.
"""

import asyncio
import os
from typing import Any

import psycopg

from app.ai.graph.workflow import (
    build_ai_analysis_graph,
)

from app.ai.rag.embedding_service import (
    EmbeddingService,
)

from app.ai.rag.embedding_text import (
    build_embedding_text,
)

from app.ai.rag.knowledge_store import (
    KnowledgeStore,
)


# =============================================================================
# TEST CONSTANTS
# =============================================================================

TEST_REQUEST_ID = "TEST-3.13.8"

TEST_ERROR_ID = "TEST-3.13.8-001"


# =============================================================================
# TEST ERROR
# =============================================================================

TEST_ERROR: dict[str, Any] = {

    "error_id": TEST_ERROR_ID,

    "tier": "telephony",

    "log_type": "asterisk",

    "server": "test-server",

    "file_name": "full",

    "file_path": "/var/log/asterisk/full",

    "title": "SIP authentication failed",

    "severity": "high",

    "timestamp": "2026-08-13 10:00:00",

    "start_line": 100,

    "end_line": 103,

    "total_lines": 4,

    "error_content": (
        "NOTICE: Request from endpoint 1001 "
        "failed authentication.\n"
        "SIP authentication failed.\n"
        "Endpoint 1001 rejected.\n"
        "Authentication failure."
    ),

    "lines": [

        {
            "line_number": 100,
            "content": (
                "NOTICE: Request from endpoint 1001 "
                "failed authentication."
            ),
        },

        {
            "line_number": 101,
            "content": (
                "SIP authentication failed."
            ),
        },

        {
            "line_number": 102,
            "content": (
                "Endpoint 1001 rejected."
            ),
        },

        {
            "line_number": 103,
            "content": (
                "Authentication failure."
            ),
        },

    ],
}


# =============================================================================
# HISTORICAL ANALYSIS
# =============================================================================

HISTORICAL_ANALYSIS: dict[str, Any] = {

    "error_signature": (
        "asterisk:sip authentication failed"
    ),

    "root_cause": (
        "Historical test root cause: "
        "SIP endpoint authentication credentials "
        "are invalid or do not match the configured "
        "endpoint credentials."
    ),

    "root_cause_evidence": [

        {
            "line_number": 100,
            "content": (
                "NOTICE: Request from endpoint 1001 "
                "failed authentication."
            ),
            "explanation": (
                "The endpoint authentication request "
                "was rejected."
            ),
        },

        {
            "line_number": 101,
            "content": (
                "SIP authentication failed."
            ),
            "explanation": (
                "The log explicitly reports SIP "
                "authentication failure."
            ),
        },

    ],

    "solution": (
        "Verify the SIP endpoint credentials "
        "against the configured Asterisk endpoint "
        "authentication settings."
    ),

    "optimization": (
        "Add monitoring for repeated SIP "
        "authentication failures and validate "
        "endpoint credentials during configuration "
        "changes."
    ),

    "test_result": {

        "status": "PASS",

        "test_steps": [

            "Verify endpoint credentials.",

            "Reload the SIP configuration.",

            "Place a test call.",

            "Confirm successful SIP authentication.",

        ],

        "expected_result": (
            "The endpoint authenticates successfully."
        ),

    },

    "jira_description": (
        "Problem: SIP endpoint authentication failed.\n"
        "Root Cause: Endpoint credentials do not match "
        "the configured authentication credentials.\n"
        "Impact: Endpoint cannot authenticate successfully.\n"
        "Proposed Fix: Correct and validate endpoint "
        "authentication credentials.\n"
        "Validation: Perform a test call and confirm "
        "successful SIP authentication."
    ),

    "status": "resolved",

    "verified": True,

    "verification_notes": (
        "Historical test knowledge is intentionally "
        "marked as verified and resolved for the "
        "RAG REUSE path test."
    ),
}


# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_database_config() -> dict[str, Any]:

    return {

        "host": os.getenv(
            "POSTGRES_HOST",
            "postgres",
        ),

        "port": int(
            os.getenv(
                "POSTGRES_PORT",
                "5432",
            )
        ),

        "dbname": os.getenv(
            "POSTGRES_DB",
            "ai_log_analyzer",
        ),

        "user": os.getenv(
            "POSTGRES_USER",
            "postgres",
        ),

        "password": os.getenv(
            "POSTGRES_PASSWORD",
            "postgres",
        ),

    }


# =============================================================================
# CLEAN TEST KNOWLEDGE
# =============================================================================

async def cleanup_test_knowledge() -> None:

    config = get_database_config()

    connection = await psycopg.AsyncConnection.connect(
        **config
    )

    try:

        async with connection.cursor() as cursor:

            await cursor.execute(
                """
                DELETE FROM ai_knowledge_items
                WHERE error_id = %(error_id)s
                """,
                {
                    "error_id": TEST_ERROR_ID,
                },
            )

        await connection.commit()

    except Exception:

        await connection.rollback()

        raise

    finally:

        await connection.close()


# =============================================================================
# PRINT PROGRESS EVENTS
# =============================================================================

def print_progress_events(
    events: list[Any],
) -> None:

    print()
    print("=" * 100)
    print("PROGRESS EVENT VALIDATION")
    print("=" * 100)

    for event in events:

        print(
            f"{event.task_id:30} "
            f"{event.status.value:12} "
            f"{event.progress:3}% "
            f"{event.message}"
        )

    print("=" * 100)


# =============================================================================
# MAIN TEST
# =============================================================================

async def main():

    print("=" * 100)
    print("STEP 3.13.8 - RAG REUSE PROGRESS PATH TEST")
    print("=" * 100)

    knowledge_id = None

    try:

        # =====================================================================
        # CLEAN PREVIOUS TEST DATA
        # =====================================================================

        print()
        print(
            "Cleaning previous 3.13.8 test knowledge..."
        )

        await cleanup_test_knowledge()

        print(
            "Previous test knowledge removed."
        )

        # =====================================================================
        # BUILD EXACT SAME EMBEDDING TEXT AS LANGGRAPH
        # =====================================================================

        print()
        print(
            "Building production RAG embedding text..."
        )

        embedding_text = build_embedding_text(
            TEST_ERROR
        )

        if not embedding_text:

            raise AssertionError(
                "build_embedding_text() returned empty text."
            )

        print(
            f"Embedding Text Length : "
            f"{len(embedding_text)}"
        )

        print()
        print(
            "Embedding text used by test:"
        )

        print(
            embedding_text
        )

        # =====================================================================
        # GENERATE EMBEDDING
        # =====================================================================

        print()
        print(
            "Generating historical knowledge embedding..."
        )

        embedding_service = EmbeddingService()

        embedding = await embedding_service.embed_text(
            embedding_text
        )

        print(
            f"Embedding Size : "
            f"{len(embedding)}"
        )

        if len(embedding) != 1536:

            raise AssertionError(
                "Expected embedding dimension 1536, "
                f"got {len(embedding)}."
            )

        # =====================================================================
        # STORE HISTORICAL KNOWLEDGE
        # =====================================================================

        print()
        print(
            "Storing verified historical RAG knowledge..."
        )

        knowledge_store = KnowledgeStore()

        knowledge_id = (
            await knowledge_store.store_knowledge(

                error=TEST_ERROR,

                embedding=embedding,

                embedding_text=embedding_text,

                analysis=HISTORICAL_ANALYSIS,

            )
        )

        print(
            f"Stored Knowledge ID : "
            f"{knowledge_id}"
        )

        if not knowledge_id:

            raise AssertionError(
                "KnowledgeStore did not return an ID."
            )

        # =====================================================================
        # BUILD GRAPH
        # =====================================================================

        print()
        print(
            "Building LangGraph..."
        )

        graph = build_ai_analysis_graph()

        print(
            "Graph created: OK"
        )

        # =====================================================================
        # INITIAL STATE
        # =====================================================================

        initial_state = {

            "request_id": TEST_REQUEST_ID,

            "tier": "telephony",

            "log_type": "asterisk",

            "selected_errors": [
                TEST_ERROR
            ],

            "current_error_index": 0,

            "current_error": None,

            "normalized_error": {},

            "error_signature": "",

            "embedding_text": "",

            "rag_query": "",

            "rag_matches": [],

            "rag_match_found": False,

            "rag_selected_match": None,

            "rag_similarity": None,

            "rag_confidence": "",

            "rag_reuse_solution": False,

            "rag_decision": "",

            "rag_result": None,

            "root_cause": "",

            "root_cause_evidence": [],

            "solution": "",

            "optimization": "",

            "source_code_analysis": "",

            "source_file": "",

            "source_line_number": None,

            "test_result": {},

            "jira_description": "",

            "final_results": [],

            "status": "pending",

            "current_task": "",

            "progress": 0,

            "messages": [],

            "error": None,

            "progress_event": None,

            "progress_events": [],

        }

        # =====================================================================
        # RUN GRAPH
        # =====================================================================

        print()
        print("=" * 100)
        print("STARTING LANGGRAPH")
        print("=" * 100)

        result = await graph.ainvoke(
            initial_state
        )

        print()
        print("=" * 100)
        print("LANGGRAPH COMPLETED")
        print("=" * 100)

        # =====================================================================
        # BASIC VALIDATION
        # =====================================================================

        if not result:

            raise AssertionError(
                "LangGraph returned an empty result."
            )

        print()
        print(
            f"Final Status : "
            f"{result.get('status')}"
        )

        print(
            f"Final Progress : "
            f"{result.get('progress')}%"
        )

        # =====================================================================
        # RAG DECISION VALIDATION
        # =====================================================================

        print()
        print("=" * 100)
        print("RAG DECISION VALIDATION")
        print("=" * 100)

        rag_decision = result.get(
            "rag_decision"
        )

        rag_similarity = result.get(
            "rag_similarity"
        )

        rag_match_found = result.get(
            "rag_match_found"
        )

        rag_reuse_solution = result.get(
            "rag_reuse_solution"
        )

        print(
            f"RAG Decision       : "
            f"{rag_decision}"
        )

        print(
            f"RAG Match Found    : "
            f"{rag_match_found}"
        )

        print(
            f"RAG Similarity     : "
            f"{rag_similarity}"
        )

        print(
            f"RAG Reuse Solution: "
            f"{rag_reuse_solution}"
        )

        # ---------------------------------------------------------------------
        # ASSERT REUSE
        # ---------------------------------------------------------------------

        if rag_decision != "reuse":

            raise AssertionError(
                "Expected RAG decision "
                f"'reuse', got '{rag_decision}'."
            )

        if not rag_match_found:

            raise AssertionError(
                "Expected RAG match to be found."
            )

        if not rag_reuse_solution:

            raise AssertionError(
                "Expected rag_reuse_solution=True."
            )

        if rag_similarity is None:

            raise AssertionError(
                "RAG similarity is missing."
            )

        if rag_similarity < 0.92:

            raise AssertionError(
                "Expected similarity >= 0.92 "
                f"for REUSE, got {rag_similarity}."
            )

        # =====================================================================
        # SELECTED MATCH VALIDATION
        # =====================================================================

        selected_match = result.get(
            "rag_selected_match"
        )

        print()
        print(
            "Selected RAG Match:"
        )

        print(
            selected_match
        )

        if not selected_match:

            raise AssertionError(
                "Expected a selected RAG match."
            )

        if selected_match.get(
            "knowledge_id"
        ) != knowledge_id:

            raise AssertionError(
                "Expected selected knowledge ID "
                f"{knowledge_id}, got "
                f"{selected_match.get('knowledge_id')}."
            )

        if not selected_match.get(
            "verified",
            False,
        ):

            raise AssertionError(
                "Expected selected RAG knowledge "
                "to be verified."
            )

        if (
            selected_match.get(
                "resolution_status",
                ""
            ).lower()
            not in {
                "resolved",
                "verified",
            }
        ):

            raise AssertionError(
                "Expected RAG resolution status "
                "to be resolved or verified."
            )

        # =====================================================================
        # FINAL RESULT VALIDATION
        # =====================================================================

        final_results = result.get(
            "final_results",
            [],
        )

        print()
        print(
            f"Final Results : "
            f"{len(final_results)}"
        )

        if len(final_results) != 1:

            raise AssertionError(
                "Expected exactly one final result."
            )

        final_result = final_results[0]

        print()
        print(
            "Final Result:"
        )

        print(
            final_result
        )

        # ---------------------------------------------------------------------
        # IMPORTANT: RESULT MUST COME FROM RAG
        # ---------------------------------------------------------------------

        if final_result.get(
            "source"
        ) != "rag":

            raise AssertionError(
                "Expected final result source "
                f"'rag', got "
                f"'{final_result.get('source')}'."
            )

        if not final_result.get(
            "rag_match",
            False,
        ):

            raise AssertionError(
                "Expected final result rag_match=True."
            )

        if (
            final_result.get(
                "rag_knowledge_id"
            )
            != knowledge_id
        ):

            raise AssertionError(
                "Final result contains unexpected "
                "RAG knowledge ID."
            )

        if not final_result.get(
            "solution"
        ):

            raise AssertionError(
                "Expected reused historical solution "
                "in final result."
            )

        # =====================================================================
        # PROGRESS EVENT VALIDATION
        # =====================================================================

        events = result.get(
            "progress_events",
            [],
        )

        print_progress_events(
            events
        )

        if not events:

            raise AssertionError(
                "No progress events were generated."
            )

        # ---------------------------------------------------------------------
        # Required RAG progress tasks
        # ---------------------------------------------------------------------

        task_ids = [
            event.task_id
            for event in events
        ]

        required_tasks = [

            "initialize_analysis",

            "prepare_error",

            "prepare_rag_query",

            "generate_rag_embedding",

            "retrieve_rag",

            "decide_rag",

            "reuse_rag_solution",

            "finalize_analysis",

        ]

        for task_id in required_tasks:

            if task_id not in task_ids:

                raise AssertionError(
                    f"Required progress task "
                    f"'{task_id}' was not generated."
                )

        # =====================================================================
        # REUSE PATH VALIDATION
        # =====================================================================

        if (
            "llm_analysis"
            in task_ids
        ):

            raise AssertionError(
                "LLM analysis progress event was "
                "generated during RAG REUSE."
            )

        if (
            "prepare_llm_analysis"
            in task_ids
        ):

            raise AssertionError(
                "prepare_llm_analysis event was "
                "generated during RAG REUSE."
            )

        # =====================================================================
        # FINAL PROGRESS
        # =====================================================================

        final_event = events[-1]

        if final_event.task_id != (
            "finalize_analysis"
        ):

            raise AssertionError(
                "Last progress event should be "
                "finalize_analysis."
            )

        if final_event.progress != 100:

            raise AssertionError(
                "Final progress should be 100%, "
                f"got {final_event.progress}%."
            )

        # =====================================================================
        # SUCCESS
        # =====================================================================

        print()
        print("=" * 100)
        print(
            "STEP 3.13.8 TEST PASSED"
        )
        print("=" * 100)

        print(
            f"Knowledge ID : {knowledge_id}"
        )

        print(
            f"Similarity   : {rag_similarity}"
        )

        print(
            "RAG Decision : REUSE"
        )

        print(
            "LLM Called   : NO"
        )

        print(
            "Progress Path: REUSE"
        )

        print(
            "Final Source : RAG"
        )

        print(
            "Final Progress: 100%"
        )

        print("=" * 100)

    finally:

        # =====================================================================
        # CLEAN TEST DATA
        # =====================================================================

        print()
        print(
            "Cleaning 3.13.8 test knowledge..."
        )

        try:

            await cleanup_test_knowledge()

            print(
                "Test knowledge cleanup completed."
            )

        except Exception as cleanup_error:

            print(
                "WARNING: Test knowledge cleanup failed:"
            )

            print(
                cleanup_error
            )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )