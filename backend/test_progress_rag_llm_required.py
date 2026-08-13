"""
STEP 3.13.9 - RAG LLM_REQUIRED PROGRESS PATH TEST

Purpose
-------
Validate the LangGraph path when historical RAG knowledge exists
but is not sufficiently similar to the current error.

Expected path:

    RAG Retrieval
        |
        v
    Historical Match
        |
        v
    Similarity < 0.80
        |
        v
    LLM_REQUIRED
        |
        v
    LLM Analysis
        |
        v
    Finalize
        |
        v
    100%

This test is the opposite branch of 3.13.8.

3.13.8:
    High similarity + verified
        -> REUSE
        -> LLM skipped

3.13.9:
    Low similarity
        -> LLM_REQUIRED
        -> LLM executed
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

TEST_REQUEST_ID = (
    "TEST-3.13.9"
)

TEST_ERROR_ID = (
    "TEST-3.13.9-001"
)


# =============================================================================
# CURRENT ERROR
# =============================================================================
#
# This is the error LangGraph will actually analyze.
#
# The historical RAG record below intentionally describes a
# substantially different Asterisk problem.
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
# HISTORICAL ERROR
# =============================================================================
#
# IMPORTANT:
#
# This is intentionally DIFFERENT from TEST_ERROR.
#
# We still use:
#
#     tier      = telephony
#     log_type  = asterisk
#
# so RAGRetriever is allowed to return the record.
#
# But the actual error is substantially different so that
# similarity should remain below the REVIEW threshold.
# =============================================================================

HISTORICAL_ERROR: dict[str, Any] = {

    "error_id": TEST_ERROR_ID,

    "tier": "telephony",

    "log_type": "asterisk",

    "server": "historical-server",

    "file_name": "messages",

    "file_path": "/var/log/asterisk/messages",

    "title": (
        "Voicemail mailbox storage quota exceeded"
    ),

    "severity": "medium",

    "timestamp": "2026-08-01 10:00:00",

    "start_line": 500,

    "end_line": 503,

    "total_lines": 4,

    "error_content": (
        "Voicemail storage limit reached.\n"
        "Mailbox 7001 cannot save new message.\n"
        "Disk quota exceeded for voicemail storage.\n"
        "Voicemail message rejected."
    ),

    "lines": [

        {
            "line_number": 500,
            "content": (
                "Voicemail storage limit reached."
            ),
        },

        {
            "line_number": 501,
            "content": (
                "Mailbox 7001 cannot save new message."
            ),
        },

        {
            "line_number": 502,
            "content": (
                "Disk quota exceeded for voicemail storage."
            ),
        },

        {
            "line_number": 503,
            "content": (
                "Voicemail message rejected."
            ),
        },

    ],
}


# =============================================================================
# HISTORICAL ANALYSIS
# =============================================================================

HISTORICAL_ANALYSIS: dict[str, Any] = {

    "error_signature": (
        "asterisk:voicemail storage quota exceeded"
    ),

    "root_cause": (
        "Historical test root cause: "
        "the voicemail mailbox storage quota was exceeded."
    ),

    "root_cause_evidence": [

        {
            "line_number": 500,
            "content": (
                "Voicemail storage limit reached."
            ),
            "explanation": (
                "The voicemail storage limit is explicitly "
                "reported as reached."
            ),
        },

        {
            "line_number": 502,
            "content": (
                "Disk quota exceeded for voicemail storage."
            ),
            "explanation": (
                "The log explicitly reports a storage "
                "quota problem."
            ),
        },

    ],

    "solution": (
        "Increase the voicemail storage capacity or "
        "remove unnecessary voicemail files after "
        "confirming the retention requirements."
    ),

    "optimization": (
        "Monitor voicemail storage utilization and "
        "configure alerts before the storage quota "
        "is exhausted."
    ),

    "test_result": {

        "status": "PASS",

        "test_steps": [

            "Check voicemail storage utilization.",

            "Free or increase the required storage.",

            "Create a test voicemail message.",

            "Confirm that the voicemail is stored successfully.",

        ],

        "expected_result": (
            "A new voicemail message is stored successfully."
        ),

    },

    "jira_description": (
        "Problem: Voicemail message could not be stored.\n"
        "Root Cause: Voicemail storage quota was exceeded.\n"
        "Impact: New voicemail messages cannot be stored.\n"
        "Proposed Fix: Increase available voicemail storage "
        "or remove unnecessary files according to retention policy.\n"
        "Validation: Create a test voicemail and confirm "
        "successful storage."
    ),

    "status": "resolved",

    "verified": True,

    "verification_notes": (
        "Historical test knowledge is resolved and verified, "
        "but intentionally describes a different error from "
        "the current SIP authentication failure."
    ),
}


# =============================================================================
# DATABASE CONFIGURATION
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
# CREATE INITIAL STATE
# =============================================================================

def create_initial_state() -> dict[str, Any]:

    return {

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
    print("STEP 3.13.9 - RAG LLM_REQUIRED PROGRESS PATH TEST")
    print("=" * 100)

    knowledge_id = None

    try:

        # =====================================================================
        # CLEAN OLD TEST DATA
        # =====================================================================

        print()
        print(
            "Cleaning previous 3.13.9 test knowledge..."
        )

        await cleanup_test_knowledge()

        print(
            "Previous test knowledge removed."
        )

        # =====================================================================
        # BUILD HISTORICAL EMBEDDING
        # =====================================================================

        print()
        print(
            "Building historical RAG embedding text..."
        )

        historical_embedding_text = (
            build_embedding_text(
                HISTORICAL_ERROR
            )
        )

        print(
            f"Historical Embedding Text Length : "
            f"{len(historical_embedding_text)}"
        )

        # =====================================================================
        # GENERATE HISTORICAL EMBEDDING
        # =====================================================================

        print()
        print(
            "Generating historical knowledge embedding..."
        )

        embedding_service = EmbeddingService()

        historical_embedding = (
            await embedding_service.embed_text(
                historical_embedding_text
            )
        )

        print(
            f"Historical Embedding Size : "
            f"{len(historical_embedding)}"
        )

        if len(historical_embedding) != 1536:

            raise AssertionError(
                "Expected historical embedding dimension "
                "1536, got "
                f"{len(historical_embedding)}."
            )

        # =====================================================================
        # STORE HISTORICAL KNOWLEDGE
        # =====================================================================

        print()
        print(
            "Storing historical RAG knowledge..."
        )

        knowledge_store = KnowledgeStore()

        knowledge_id = (
            await knowledge_store.store_knowledge(

                error=HISTORICAL_ERROR,

                embedding=historical_embedding,

                embedding_text=(
                    historical_embedding_text
                ),

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

        initial_state = (
            create_initial_state()
        )

        # =====================================================================
        # RUN LANGGRAPH
        # =====================================================================

        print()
        print("=" * 100)
        print(
            "STARTING LANGGRAPH"
        )
        print("=" * 100)

        result = await graph.ainvoke(
            initial_state
        )

        print()
        print("=" * 100)
        print(
            "LANGGRAPH COMPLETED"
        )
        print("=" * 100)

        if not result:

            raise AssertionError(
                "LangGraph returned an empty result."
            )

        # =====================================================================
        # BASIC RESULT
        # =====================================================================

        print()
        print(
            f"Final Status   : "
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
        print(
            "RAG DECISION VALIDATION"
        )
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
            f"RAG Decision        : "
            f"{rag_decision}"
        )

        print(
            f"RAG Match Found     : "
            f"{rag_match_found}"
        )

        print(
            f"RAG Similarity      : "
            f"{rag_similarity}"
        )

        print(
            f"RAG Reuse Solution  : "
            f"{rag_reuse_solution}"
        )

        # =====================================================================
        # ASSERT LLM_REQUIRED
        # =====================================================================

        if rag_decision != "llm_required":

            raise AssertionError(
                "Expected RAG decision "
                f"'llm_required', got "
                f"'{rag_decision}'."
            )

        if not rag_match_found:

            raise AssertionError(
                "Expected RAG to find the historical "
                "candidate."
            )

        if rag_reuse_solution:

            raise AssertionError(
                "Expected rag_reuse_solution=False "
                "for LLM_REQUIRED path."
            )

        if rag_similarity is None:

            raise AssertionError(
                "RAG similarity is missing."
            )

        if rag_similarity >= 0.80:

            raise AssertionError(
                "Expected similarity below the "
                "review threshold of 0.80, got "
                f"{rag_similarity}."
            )

        # =====================================================================
        # SELECTED MATCH
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
                "Expected a historical RAG candidate."
            )

        if selected_match.get(
            "knowledge_id"
        ) != knowledge_id:

            raise AssertionError(
                "Expected selected knowledge ID "
                f"{knowledge_id}, got "
                f"{selected_match.get('knowledge_id')}."
            )

        # =====================================================================
        # PROGRESS EVENTS
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

        task_ids = [
            event.task_id
            for event in events
        ]

        # =====================================================================
        # REQUIRED RAG EVENTS
        # =====================================================================

        required_rag_tasks = [

            "initialize_analysis",

            "prepare_error",

            "prepare_rag_query",

            "generate_rag_embedding",

            "retrieve_rag",

            "decide_rag",

        ]

        for task_id in required_rag_tasks:

            if task_id not in task_ids:

                raise AssertionError(
                    f"Required progress task "
                    f"'{task_id}' was not generated."
                )

        # =====================================================================
        # LLM PATH MUST EXIST
        # =====================================================================

        llm_events = [
            event
            for event in events
            if event.task_id == "prepare_llm_analysis"
        ]

        if not llm_events:

            raise AssertionError(
                "Expected prepare_llm_analysis progress events "
                "for LLM_REQUIRED path."
            )

        llm_statuses = {
            event.status.value
            for event in llm_events
        }

        if "running" not in llm_statuses:

            raise AssertionError(
                "Expected prepare_llm_analysis running event."
            )

        if "completed" not in llm_statuses:

            raise AssertionError(
                "Expected prepare_llm_analysis completed event."
            )

        # =====================================================================
        # REUSE PATH MUST NOT EXIST
        # =====================================================================

        if (
            "reuse_rag_solution"
            in task_ids
        ):

            raise AssertionError(
                "reuse_rag_solution event was generated "
                "during LLM_REQUIRED path."
            )

        # =====================================================================
        # FINALIZE MUST EXIST
        # =====================================================================

        if (
            "finalize_analysis"
            not in task_ids
        ):

            raise AssertionError(
                "finalize_analysis progress event "
                "was not generated."
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

        # =====================================================================
        # FINAL RESULT MUST COME FROM LLM
        # =====================================================================

        source = final_result.get(
            "source"
        )

        if source != "llm":

            raise AssertionError(
                "Expected final result source "
                f"'llm', got '{source}'."
            )

        # =====================================================================
        # FINAL RESULT MUST NOT REUSE RAG SOLUTION
        # =====================================================================

        if rag_decision != "llm_required":

            raise AssertionError(
                "Expected final RAG decision to be "
                "'llm_required'."
            )

        if final_result.get(
            "source"
        ) != "llm":

            raise AssertionError(
                "Expected final result source to be "
                "'llm'."
            )

        # A RAG candidate may still have been retrieved.
        # rag_match=True means a candidate existed.
        # It does NOT mean that the solution was reused.

        if not final_result.get(
            "rag_match",
            False,
        ):

            raise AssertionError(
                "Expected final result rag_match=True "
                "because a RAG candidate was retrieved."
            )

        if final_result.get(
            "rag_knowledge_id"
        ) != selected_match.get(
            "knowledge_id"
        ):

            raise AssertionError(
                "Final result RAG knowledge ID does not "
                "match the selected RAG candidate."
            )

        if final_result.get(
            "rag_similarity"
        ) != rag_similarity:

            raise AssertionError(
                "Final result RAG similarity does not "
                "match the RAG decision similarity."
            )

        # =====================================================================
        # FINAL RESULT MUST HAVE ANALYSIS
        # =====================================================================

        if not final_result.get(
            "root_cause"
        ):

            raise AssertionError(
                "Expected LLM analysis to produce "
                "a root cause."
            )

        if not final_result.get(
            "solution"
        ):

            raise AssertionError(
                "Expected LLM analysis to produce "
                "a solution."
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
            "STEP 3.13.9 TEST PASSED"
        )
        print("=" * 100)

        print(
            f"Knowledge ID : "
            f"{knowledge_id}"
        )

        print(
            f"Similarity   : "
            f"{rag_similarity}"
        )

        print(
            "RAG Decision : LLM_REQUIRED"
        )

        print(
            "LLM Called   : YES"
        )

        print(
            "Progress Path: LLM"
        )

        print(
            "Final Source : LLM"
        )

        print(
            "Final Progress: 100%"
        )

        print("=" * 100)

    finally:

        # =====================================================================
        # CLEAN TEST KNOWLEDGE
        # =====================================================================

        print()
        print(
            "Cleaning 3.13.9 test knowledge..."
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