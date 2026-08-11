"""
Step 3.9 Web/Laravel LLM test.
"""

import asyncio
import json

from app.ai.llm.analyzers import AnalyzerFactory
from app.ai.llm.llm_service import LLMService


async def main():

    print("=" * 100)
    print("STEP 3.9 - WEB/LARAVEL LLM TEST")
    print("=" * 100)

    llm_service = LLMService()

    analyzer = AnalyzerFactory.get_analyzer(
        log_type="laravel",
        llm_service=llm_service,
    )

    error = {

        "error_id": "TEST-WEB-001",

        "tier": "web",

        "log_type": "laravel",

        "server": "test-server",

        "file_name": "laravel.log",

        "file_path": (
            "/var/log/laravel/laravel.log"
        ),

        "title": (
            "[2019-02-04 11:42:00] "
            "local.ERROR: "
            "Route [dashboard.analytical] "
            "not defined."
        ),

        "severity": "ERROR",

        "timestamp": (
            "2019-02-04 11:42:00"
        ),

        "start_line": 100,

        "end_line": 108,

        "total_lines": 9,

        "error_content": (
            "Route [dashboard.analytical] "
            "not defined."
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

                "raw": (
                    "Stack trace example"
                ),
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

    # -------------------------------------------------------------------------
    # Simulated RAG context.
    #
    # This allows us to test the enriched prompt architecture.
    # -------------------------------------------------------------------------

    historical_context = {

        "knowledge_id": 1,

        "similarity": 0.91,

        "tier": "web",

        "log_type": "laravel",

        "title": (
            "Route dashboard.test not defined"
        ),

        "root_cause": (
            "A route reference exists without "
            "a corresponding registered route."
        ),

        "solution": (
            "Register the route or correct "
            "the route reference."
        ),

        "optimization": (
            "Validate named route references "
            "during deployment."
        ),

        "verified": True,

        "resolution_status": "verified",
    }

    result = await analyzer.analyze(

        error=error,

        historical_context=(
            historical_context
        ),
    )

    print()
    print("=" * 100)
    print("STRUCTURED WEB AI RESPONSE")
    print("=" * 100)

    print(
        json.dumps(
            result,
            indent=2,
            default=str,
        )
    )

    print("=" * 100)
    print("STEP 3.9 TEST COMPLETED")
    print("=" * 100)


if __name__ == "__main__":

    asyncio.run(main())