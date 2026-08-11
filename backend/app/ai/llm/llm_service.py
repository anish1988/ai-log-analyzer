"""
Central LLM service.

Responsible only for communicating with the LLM.

The service supports:

    1. Raw text responses
    2. Structured Pydantic responses
"""

import os
from typing import TypeVar

from langchain_openai import ChatOpenAI
from pydantic import BaseModel


T = TypeVar(
    "T",
    bound=BaseModel,
)


class LLMService:

    def __init__(
        self,
        *,
        model: str | None = None,
        temperature: float = 0.0,
    ) -> None:

        self.model = (
            model
            or os.getenv(
                "OPENAI_MODEL",
                "gpt-5.4",
            )
        )

        self.temperature = temperature

        print("=" * 100)
        print("LLM SERVICE INITIALIZATION")
        print("=" * 100)

        print(
            f"LLM Model  : {self.model}"
        )

        print(
            f"Temperature: {temperature}"
        )

        self.llm = ChatOpenAI(
            model=self.model,
            temperature=temperature,
        )

    async def analyze(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Return a raw text response.
        """

        print("=" * 100)
        print("LLM REQUEST")
        print("=" * 100)

        print(
            f"System Prompt Length : "
            f"{len(system_prompt)}"
        )

        print(
            f"User Prompt Length   : "
            f"{len(user_prompt)}"
        )

        response = await self.llm.ainvoke(
            [
                (
                    "system",
                    system_prompt,
                ),
                (
                    "user",
                    user_prompt,
                ),
            ]
        )

        content = response.content

        if not isinstance(
            content,
            str,
        ):

            content = str(content)

        print("=" * 100)
        print("LLM RESPONSE RECEIVED")
        print("=" * 100)

        print(
            f"Response Length : "
            f"{len(content)}"
        )

        return content

    async def analyze_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_schema: type[T],
    ) -> T:
        """
        Return a validated Pydantic response.

        The LLM is constrained to the supplied schema.
        """

        print("=" * 100)
        print("STRUCTURED LLM REQUEST")
        print("=" * 100)

        print(
            f"Schema : "
            f"{response_schema.__name__}"
        )

        print(
            f"System Prompt Length : "
            f"{len(system_prompt)}"
        )

        print(
            f"User Prompt Length   : "
            f"{len(user_prompt)}"
        )

        structured_llm = (
            self.llm.with_structured_output(
                response_schema
            )
        )

        result = await structured_llm.ainvoke(
            [
                (
                    "system",
                    system_prompt,
                ),
                (
                    "user",
                    user_prompt,
                ),
            ]
        )

        if not isinstance(
            result,
            response_schema,
        ):

            raise TypeError(
                "LLM returned an unexpected "
                "structured response type."
            )

        print("=" * 100)
        print("STRUCTURED LLM RESPONSE RECEIVED")
        print("=" * 100)

        print(
            f"Schema : "
            f"{response_schema.__name__}"
        )

        return result