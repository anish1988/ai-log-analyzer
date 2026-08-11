"""
Step 3.8 LLM architecture test.

This verifies:

    LLMService
    AnalyzerFactory
    WebLogAnalyzer
    PromptBuilder
    LLMResponseParser
"""

import asyncio

from app.ai.llm.analyzers import AnalyzerFactory
from app.ai.llm.llm_service import LLMService


async def main():

    print("=" * 100)
    print("STEP 3.8 - LLM ARCHITECTURE TEST")
    print("=" * 100)

    llm_service = LLMService(
        model="gpt-5.6",
        temperature=0.0,
    )

    analyzer = AnalyzerFactory.get_analyzer(
        log_type="laravel",
        llm_service=llm_service,
    )

    error = {

        "error_id": "TEST-LLM-001",

        "tier": "web",

        "log_type": "laravel",

        "server": "test-server",

        "file_name": "laravel.log",

        "title": (
            "Route [dashboard.test] not defined."
        ),

        "severity": "ERROR",

        "timestamp": (
            "2026-08-11 10:00:00"
        ),

        "start_line": 100,

        "end_line": 105,

        "error_content": (
            "Route [dashboard.test] not defined."
        ),

        "lines": [

            {
                "line_number": 100,

                "raw": (
                    "Route [dashboard.test] not defined."
                ),
            },

            {
                "line_number": 101,

                "raw": (
                    "Stack trace example"
                ),
            },
        ],
    }

    result = await analyzer.analyze(
        error=error,

        historical_context=None,
    )

    print()
    print("=" * 100)
    print("LLM ANALYSIS RESULT")
    print("=" * 100)

    print(result)

    print("=" * 100)
    print("STEP 3.8 TEST COMPLETED")
    print("=" * 100)


if __name__ == "__main__":

    asyncio.run(main())