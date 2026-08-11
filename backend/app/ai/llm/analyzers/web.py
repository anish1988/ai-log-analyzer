"""
Web log AI analyzer.

Handles web-related log types such as:

    Laravel
    Apache
    future web log parsers
"""

from typing import Any

from app.ai.llm.analyzers.base import BaseLogAnalyzer
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.llm.response_parser import LLMResponseParser


class WebLogAnalyzer(BaseLogAnalyzer):

    def __init__(
        self,
        llm_service: LLMService,
    ) -> None:

        self.llm_service = llm_service

    def get_system_prompt(self) -> str:

        return """
You are an expert Web Application Root Cause Analysis engineer.

You analyze web application and web server logs.

Your analysis must be evidence-driven.

You must distinguish between:

1. Facts directly visible in the logs.
2. Strongly supported conclusions.
3. Hypotheses that require verification.

Analyze:

- error meaning
- likely root cause
- important evidence
- relevant log lines
- likely source-code area
- recommended solution
- optimization/prevention
- test/verification approach
- Jira-ready description

Do not invent source-code line numbers.

If the supplied logs do not provide enough information,
explicitly state what information is missing.

Return ONLY valid JSON.
"""

    async def analyze(
        self,
        *,
        error: dict[str, Any],
        historical_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        user_prompt = (
            PromptBuilder.build_user_prompt(
                error=error,

                log_type=(
                    error.get(
                        "log_type",
                        "web",
                    )
                ),

                historical_context=(
                    historical_context
                ),
            )
        )

        response = await self.llm_service.analyze(
            system_prompt=self.get_system_prompt(),

            user_prompt=user_prompt,
        )

        return LLMResponseParser.parse(
            response
        )