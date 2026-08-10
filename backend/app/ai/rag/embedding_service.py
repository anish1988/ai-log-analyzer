"""
Embedding Service.

Responsible for converting error/analysis text into vector embeddings
using LangChain's OpenAI integration.

The current embedding model is:

    text-embedding-3-small

which produces 1536-dimensional embeddings.
"""

from langchain_openai import OpenAIEmbeddings


class EmbeddingService:
    """
    Generates embeddings for RAG knowledge and search queries.
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
    ) -> None:

        self.model = model

        self.embeddings = OpenAIEmbeddings(
            model=self.model,
        )

    async def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for one piece of text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        print("=" * 100)
        print("EMBEDDING SERVICE")
        print("=" * 100)
        print(f"Embedding Model : {self.model}")
        print(f"Text Length     : {len(text)}")

        embedding = await self.embeddings.aembed_query(
            text
        )

        print(f"Embedding Size  : {len(embedding)}")
        print("=" * 100)

        return embedding