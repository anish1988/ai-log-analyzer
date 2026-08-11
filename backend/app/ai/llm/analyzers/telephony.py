"""
Telephony AI analyzer.

Handles:

    Asterisk
    VICIdial
    AGI
    telephony-related errors
"""

from typing import Any

from app.ai.llm.analyzers.base import BaseLogAnalyzer
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.llm.response_parser import LLMResponseParser


class TelephonyLogAnalyzer(BaseLogAnalyzer):

    def __init__(
        self,
        llm_service: LLMService,
    ) -> None:

        self.llm_service = llm_service

    def get_system_prompt(self) -> str:

        return """
You are an expert Asterisk and VICIdial
telephony Root Cause Analysis engineer.

Analyze telephony logs with particular attention to:

- Asterisk errors
- SIP/channel problems
- AGI execution
- dialplan behavior
- call routing
- call recording
- voicemail
- VICIdial integration
- database/telephony interaction

Identify the most likely root cause using evidence
from the supplied logs.

Do not invent facts.

Do not invent source-code line numbers.

Clearly distinguish observed evidence from assumptions.

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
                        "telephony",
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