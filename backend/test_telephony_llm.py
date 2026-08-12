"""
STEP 3.11 - TELEPHONY LLM TEST

Tests:

    LangGraph
        ↓
    RAG
        ↓
    RAG Decision
        ↓
    Telephony Analyzer
        ↓
    Structured LLM
        ↓
    Final Results
"""

import asyncio
import json

from app.ai.graph.workflow import (
    build_ai_analysis_graph,
)


async def main():

    print("=" * 100)
    print("STEP 3.11 - TELEPHONY LLM TEST")
    print("=" * 100)

    graph = build_ai_analysis_graph()

    # =========================================================================
    # TEST TELEPHONY ERROR
    # =========================================================================

    error = {
        "error_id": "TEST-TELEPHONY-001",

        "tier": "telephony",

        "log_type": "asterisk",

        "server": "test-server",

        "file_name": "full",

        "file_path": (
            "/var/log/asterisk/full"
        ),

        "title": (
            "SIP authentication failed"
        ),

        "severity": "ERROR",

        "timestamp": (
            "2026-08-11 10:00:00"
        ),

        "start_line": 100,

        "end_line": 106,

        "total_lines": 7,

        "error_content": (
            "Failed to authenticate "
            "SIP peer"
        ),

        "lines": [
            {
                "line_number": 100,
                "raw": (
                    "[2026-08-11 10:00:00] "
                    "NOTICE: "
                    "Received SIP authentication "
                    "failure"
                ),
            },
            {
                "line_number": 101,
                "raw": (
                    "SIP peer authentication failed"
                ),
            },
            {
                "line_number": 102,
                "raw": (
                    "Endpoint rejected authentication"
                ),
            },
            {
                "line_number": 103,
                "raw": (
                    "Request received from "
                    "10.10.10.25"
                ),
            },
            {
                "line_number": 104,
                "raw": (
                    "Authentication failed "
                    "for SIP endpoint 1001"
                ),
            },
            {
                "line_number": 105,
                "raw": (
                    "Call setup aborted"
                ),
            },
            {
                "line_number": 106,
                "raw": (
                    "No outbound channel created"
                ),
            },
        ],
    }

    # =========================================================================
    # INITIAL STATE
    # =========================================================================

    initial_state = {

        "request_id": (
            "TEST-3.11"
        ),

        "tier": "telephony",

        "log_type": "asterisk",

        "selected_errors": [
            error
        ],

        "current_error_index": 0,

        "current_error": error,

        "final_results": [],

        "status": "processing",

        "progress": 0,

        "messages": [],

        "error": None,
    }

    print()
    print(
        "Starting Telephony LangGraph..."
    )
    print()

    try:

        result = await graph.ainvoke(
            initial_state
        )

        print()
        print("=" * 100)
        print(
            "TELEPHONY LANGGRAPH "
            "EXECUTION COMPLETED"
        )
        print("=" * 100)

        # ---------------------------------------------------------------------
        # Final state
        # ---------------------------------------------------------------------

        print()
        print("FINAL STATE:")
        print()

        print(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )

        # ---------------------------------------------------------------------
        # Final results
        # ---------------------------------------------------------------------

        final_results = result.get(
            "final_results",
            [],
        )

        print()
        print("=" * 100)
        print("TELEPHONY FINAL RESULTS")
        print("=" * 100)

        print(
            json.dumps(
                final_results,
                indent=2,
                default=str,
            )
        )

        print()
        print(
            f"Final Result Count : "
            f"{len(final_results)}"
        )

        # ---------------------------------------------------------------------
        # Validation
        # ---------------------------------------------------------------------

        if len(final_results) != 1:

            raise RuntimeError(
                "Expected exactly one "
                "Telephony AI result."
            )

        final_result = final_results[0]

        print()
        print("=" * 100)
        print("STEP 3.11 VALIDATION")
        print("=" * 100)

        print(
            "Error ID       :",
            final_result.get(
                "error_id"
            ),
        )

        print(
            "Log Type       :",
            final_result.get(
                "log_type"
            ),
        )

        print(
            "Source         :",
            final_result.get(
                "source"
            ),
        )

        print(
            "Root Cause     :",
            final_result.get(
                "root_cause"
            ),
        )

        print(
            "Solution       :",
            final_result.get(
                "solution"
            ),
        )

        print(
            "Confidence     :",
            final_result.get(
                "confidence"
            ),
        )

        print()
        print(
            "STEP 3.11 TEST PASSED"
        )

        print("=" * 100)

    except Exception as exc:

        print()
        print("=" * 100)
        print(
            "STEP 3.11 TEST FAILED"
        )
        print("=" * 100)

        print(
            f"{type(exc).__name__}: "
            f"{exc}"
        )

        raise


if __name__ == "__main__":

    asyncio.run(
        main()
    )