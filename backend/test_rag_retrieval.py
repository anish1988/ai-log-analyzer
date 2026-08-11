"""
Standalone RAG retrieval test.

Uses the knowledge item created during Step 3.4.
"""

import asyncio

from app.ai.graph.state import SelectedError
from app.ai.rag.embedding_service import EmbeddingService
from app.ai.rag.embedding_text import build_embedding_text
from app.ai.rag.retriever import RAGRetriever


async def main() -> None:

    print("=" * 100)
    print("RAG RETRIEVAL TEST")
    print("=" * 100)

    # -------------------------------------------------------------------------
    # Simulate a NEW error that is very similar to the knowledge item
    # created during Step 3.4.
    # -------------------------------------------------------------------------

    error: SelectedError = {

        "error_id": "TEST-RAG-002",

        "tier": "web",

        "log_type": "laravel",

        "server": "test-server",

        "file_name": "laravel.log",

        "file_path": "/var/log/laravel.log",

        "title": (
            "Route [dashboard.test] not defined."
        ),

        "severity": "ERROR",

        "timestamp": (
            "2026-08-10 19:00:00"
        ),

        "start_line": 200,

        "end_line": 203,

        "total_lines": 4,

        "error_content": (
            "Route [dashboard.test] not defined."
        ),

        "lines": [

            {
                "line_number": 200,
                "raw": (
                    "Route [dashboard.test] not defined."
                ),
            },

            {
                "line_number": 201,
                "raw": (
                    "Stack trace line example"
                ),
            },
        ],
    }

    # -------------------------------------------------------------------------
    # Build search text.
    #
    # Notice that we DON'T include root cause or solution.
    #
    # The new error doesn't have those yet.
    # -------------------------------------------------------------------------

    search_text = build_embedding_text(
        error
    )

    print()
    print("Search Text:")
    print("--------------------------------------------")
    print(search_text)
    print("--------------------------------------------")

    # -------------------------------------------------------------------------
    # Generate query embedding.
    # -------------------------------------------------------------------------

    embedding_service = EmbeddingService()

    embedding = await embedding_service.embed_text(
        search_text
    )

    # -------------------------------------------------------------------------
    # Search RAG.
    # -------------------------------------------------------------------------

    retriever = RAGRetriever()

    matches = await retriever.search(
        embedding=embedding,
        tier="web",
        log_type="laravel",
        limit=5,
        min_similarity=0.0,
    )

    # -------------------------------------------------------------------------
    # Display results.
    # -------------------------------------------------------------------------

    print()
    print("=" * 100)
    print("RAG SEARCH RESULTS")
    print("=" * 100)

    if not matches:

        print("No matches found.")

    else:

        for index, match in enumerate(
            matches,
            start=1,
        ):

            print()
            print(
                f"Match #{index}"
            )

            print(
                f"Knowledge ID : "
                f"{match.get('knowledge_id')}"
            )

            print(
                f"Similarity   : "
                f"{match.get('similarity')}"
            )

            print(
                f"Tier         : "
                f"{match.get('tier')}"
            )

            print(
                f"Log Type     : "
                f"{match.get('log_type')}"
            )

            print(
                f"Error        : "
                f"{match.get('error_signature')}"
            )

            print(
                f"Resolution   : "
                f"{match.get('resolution_status')}"
            )

            print(
                f"Verified     : "
                f"{match.get('verified')}"
            )

            print(
                f"Solution     : "
                f"{match.get('solution')}"
            )

    print()
    print("=" * 100)


if __name__ == "__main__":

    asyncio.run(main())