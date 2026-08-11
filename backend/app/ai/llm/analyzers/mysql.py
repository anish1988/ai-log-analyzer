"""
MySQL AI analyzer.
"""

from typing import Any

from app.ai.llm.analyzers.base import BaseLogAnalyzer
from app.ai.llm.llm_service import LLMService
from app.ai.llm.prompt_builder import PromptBuilder
from app.ai.llm.response_parser import LLMResponseParser


class MySQLLogAnalyzer(BaseLogAnalyzer):

    def __init__(
        self,
        llm_service: LLMService,
    ) -> None:

        self.llm_service = llm_service

    def get_system_prompt(self) -> str:

        return """
You are an expert MySQL database Root Cause Analysis engineer.

Analyze MySQL and database-related log errors.

Pay particular attention to:

- connection failures
- authentication failures
- SQL errors
- deadlocks
- locking
- transaction failures
- replication problems
- table/index problems
- performance-related errors
- resource exhaustion
- configuration issues

Use only evidence provided by the input.

Do not invent SQL statements, schema details,
source-code locations, or configuration values.

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
                        "mysql",
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