import asyncio

from app.ai.rag.embedding_service import EmbeddingService
from app.ai.rag.retriever import RAGRetriever


async def main():

    text = (
        "Asterisk SIP authentication failed "
        "for endpoint 1001. "
        "Request from endpoint 1001 failed authentication. "
        "SIP authentication failed. "
        "Endpoint 1001 rejected."
    )

    embedding_service = EmbeddingService()

    embedding = await embedding_service.embed_text(
        text
    )

    print("=" * 100)
    print("RAG SIMILARITY TEST")
    print("=" * 100)

    print(
        f"Embedding Size : {len(embedding)}"
    )

    retriever = RAGRetriever()

    matches = await retriever.search(
        embedding=embedding,
        tier="telephony",
        log_type="asterisk",
        limit=5,
        min_similarity=0.0,
    )

    print(
        f"Matches : {len(matches)}"
    )

    print()

    for match in matches:

        print("=" * 100)
        print("MATCH FOUND")
        print("=" * 100)

        print(
            "Knowledge ID :",
            match.get("knowledge_id"),
        )

        print(
            "Similarity   :",
            match.get("similarity"),
        )

        print(
            "Signature    :",
            match.get("error_signature"),
        )

        print(
            "Title        :",
            match.get("title"),
        )

        print(
            "Tier         :",
            match.get("tier"),
        )

        print(
            "Log Type     :",
            match.get("log_type"),
        )

        print(
            "Full Match   :",
            match,
        )


if __name__ == "__main__":

    asyncio.run(main())