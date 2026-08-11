import asyncio
import json

from app.ai.graph.workflow import build_ai_analysis_graph


async def main():

    print("=" * 100)
    print("STEP 3.10 - LANGGRAPH DIRECT TEST")
    print("=" * 100)

    graph = build_ai_analysis_graph()

    error = {
        "error_id": "TEST-WEB-001",
        "tier": "web",
        "log_type": "laravel",
        "server": "test-server",
        "file_name": "laravel.log",
        "file_path": "/var/log/laravel/laravel.log",
        "title": (
            "[2019-02-04 11:42:00] "
            "local.ERROR: "
            "Route [dashboard.analytical] not defined."
        ),
        "severity": "ERROR",
        "timestamp": "2019-02-04 11:42:00",
        "start_line": 100,
        "end_line": 108,
        "total_lines": 9,
        "error_content": (
            "Route [dashboard.analytical] not defined."
        ),
        "lines": [
            {
                "line_number": 100,
                "raw": (
                    "[2019-02-04 11:42:00] "
                    "local.ERROR: "
                    "Route [dashboard.analytical] "
                    "not defined."
                ),
            },
            {
                "line_number": 101,
                "raw": "Stack trace example",
            },
            {
                "line_number": 102,
                "raw": (
                    "resources/views/layout/"
                    "navbar.blade.php"
                ),
            },
        ],
    }

    initial_state = {
        "request_id": "TEST-3.10",

        "tier": "web",

        "log_type": "laravel",

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
    print("Starting LangGraph...")
    print()

    try:

        result = await graph.ainvoke(
            initial_state
        )

        print()
        print("=" * 100)
        print("LANGGRAPH EXECUTION COMPLETED")
        print("=" * 100)

        print()
        print("FINAL STATE:")
        print(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )

        print()
        print("=" * 100)
        print("FINAL RESULTS")
        print("=" * 100)

        final_results = result.get(
            "final_results",
            [],
        )

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

    except Exception as exc:

        print()
        print("=" * 100)
        print("LANGGRAPH TEST FAILED")
        print("=" * 100)

        print(
            f"{type(exc).__name__}: {exc}"
        )

        raise


if __name__ == "__main__":
    asyncio.run(main())