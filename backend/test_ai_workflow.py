"""
Standalone LangGraph workflow test.

This test does not call the frontend.

It directly exercises:

    Selected Errors
        ↓
    LangGraph
        ↓
    RAG
        ↓
    Decision
        ↓
    Final Results
"""

import asyncio

from app.ai.graph.state import AIAnalysisState
from app.ai.graph.workflow import ai_analysis_graph


async def main() -> None:

    print("=" * 100)
    print("AI ANALYSIS LANGGRAPH TEST")
    print("=" * 100)

    # -------------------------------------------------------------------------
    # We intentionally use an error similar to the test knowledge item
    # created during Step 3.4.
    # -------------------------------------------------------------------------

    selected_errors = [
        {
            "error_id": "TEST-GRAPH-001",

            "tier": "web",

            "log_type": "laravel",

            "server": "test-server",

            "file_name": "laravel.log",

            "file_path": "/var/log/laravel.log",

            "title": (
                "Route [dashboard.test] not defined."
            ),

            "severity": "ERROR",

            "timestamp": (
                "2026-08-11 10:00:00"
            ),

            "start_line": 300,

            "end_line": 303,

            "total_lines": 4,

            "error_content": (
                "Route [dashboard.test] not defined."
            ),

            "lines": [
                {
                    "line_number": 300,
                    "raw": (
                        "Route [dashboard.test] not defined."
                    ),
                },
                {
                    "line_number": 301,
                    "raw": (
                        "Stack trace line example"
                    ),
                },
            ],
        }
    ]

    initial_state: AIAnalysisState = {

        "request_id": (
            "TEST-GRAPH-001"
        ),

        "tier": "web",

        "log_type": "laravel",

        "selected_errors": selected_errors,

        "current_error_index": 0,

        "current_error": None,

        "final_results": [],

        "status": "idle",

        "current_task": "",

        "progress": 0,

        "messages": [],

        "error": None,
    }

    # -------------------------------------------------------------------------
    # Run graph
    # -------------------------------------------------------------------------

    result = await ai_analysis_graph.ainvoke(
        initial_state
    )

    # -------------------------------------------------------------------------
    # Display result
    # -------------------------------------------------------------------------

    print()
    print("=" * 100)
    print("LANGGRAPH FINAL STATE")
    print("=" * 100)

    print(
        "Status:",
        result.get("status"),
    )

    print(
        "Progress:",
        result.get("progress"),
    )

    print(
        "Current Task:",
        result.get("current_task"),
    )

    print(
        "Final Results:",
        len(
            result.get(
                "final_results",
                [],
            )
        ),
    )

    for index, analysis in enumerate(
        result.get(
            "final_results",
            [],
        ),
        start=1,
    ):

        print()
        print(
            f"Result #{index}"
        )

        print(
            "Error ID:",
            analysis.get(
                "error_id"
            ),
        )

        print(
            "Source:",
            analysis.get(
                "source"
            ),
        )

        print(
            "RAG Match:",
            analysis.get(
                "rag_match"
            ),
        )

        print(
            "Similarity:",
            analysis.get(
                "rag_similarity"
            ),
        )

        print(
            "Status:",
            analysis.get(
                "status"
            ),
        )

    print()
    print("=" * 100)
    print("LANGGRAPH TEST COMPLETED")
    print("=" * 100)


if __name__ == "__main__":

    asyncio.run(main())