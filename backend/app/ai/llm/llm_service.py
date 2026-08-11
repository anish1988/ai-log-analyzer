"""
Central LLM service.

This class is responsible only for communicating with the LLM.

It does NOT:
    - decide which prompt to use
    - perform RAG
    - analyze log types
    - build Jira descriptions
    - decide whether a RAG result should be reused

Those responsibilities belong to higher-level components.
"""

from typing import Any

from langchain_openai import ChatOpenAI


class LLMService:

    def __init__(
        self,
        *,
        model: str = "gpt-5.6",
        temperature: float = 0.0,
    ) -> None:

        print("=" * 100)
        print("LLM SERVICE INITIALIZATION")
        print("=" * 100)

        print(
            f"LLM Model  : {model}"
        )

        print(
            f"Temperature: {temperature}"
        )

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
        )

    async def analyze(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Send a prompt to the LLM and return the raw response.

        Structured parsing is intentionally handled separately.
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