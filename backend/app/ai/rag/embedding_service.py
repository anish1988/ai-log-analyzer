"""
Embedding Service.

Supports:
    - OpenAI embeddings
    - Gemini embeddings
"""

import os

from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
)


class EmbeddingService:

    def __init__(
        self,
        *,
        model: str | None = None,
    ) -> None:

        self.provider = os.getenv(
            "AI_PROVIDER",
            "openai",
        ).lower()

        if self.provider == "gemini":

            self.model = (
                model
                or os.getenv(
                    "GEMINI_EMBEDDING_MODEL",
                    "gemini-embedding-001",
                )
            )

            api_key = os.getenv(
                "GEMINI_API_KEY"
            )

            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured."
                )

            self.embeddings = (
                GoogleGenerativeAIEmbeddings(
                    model=self.model,
                    google_api_key=api_key,
                    output_dimensionality=int(
                        os.getenv(
                            "GEMINI_EMBEDDING_DIMENSION",
                            "1536",
                        )
                    ),
                )
            )

        elif self.provider == "openai":

            self.model = (
                model
                or os.getenv(
                    "OPENAI_EMBEDDING_MODEL",
                    "text-embedding-3-small",
                )
            )

            api_key = os.getenv(
                "OPENAI_API_KEY"
            )

            if not api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY is not configured."
                )

            self.embeddings = OpenAIEmbeddings(
                model=self.model,
                api_key=api_key,
            )

        else:

            raise ValueError(
                f"Unsupported AI_PROVIDER: "
                f"{self.provider}"
            )

        print("=" * 100)
        print("EMBEDDING SERVICE")
        print("=" * 100)
        print(
            f"Embedding Provider : {self.provider}"
        )
        print(
            f"Embedding Model    : {self.model}"
        )
        print("=" * 100)

    async def embed_text(
        self,
        text: str,
    ) -> list[float]:

        if not text or not text.strip():
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        embedding = (
            await self.embeddings.aembed_query(
                text
            )
        )

        print(
            f"Embedding Size : {len(embedding)}"
        )

        return embedding