import asyncio

from app.ai.graph.state import SelectedError
from app.ai.rag.embedding_service import EmbeddingService
from app.ai.rag.embedding_text import build_embedding_text
from app.ai.rag.knowledge_store import KnowledgeStore


async def main() -> None:

    print("=" * 100)
    print("RAG STORAGE TEST")
    print("=" * 100)

    error: SelectedError = {
        "error_id": "TEST-RAG-001",
        "tier": "web",
        "log_type": "laravel",
        "server": "test-server",
        "file_name": "laravel.log",
        "file_path": "/var/log/laravel.log",
        "title": "Route [dashboard.test] not defined.",
        "severity": "ERROR",
        "timestamp": "2026-08-10 18:00:00",
        "start_line": 100,
        "end_line": 103,
        "total_lines": 4,
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
                    "Stack trace line example"
                ),
            },
        ],
    }

    # -------------------------------------------------------------------------
    # 1. Build semantic text
    # -------------------------------------------------------------------------

    embedding_text = build_embedding_text(
        error,
        root_cause=(
            "The application references a Laravel route "
            "that is not registered."
        ),
        solution=(
            "Register the route or correct the route reference."
        ),
        optimization=(
            "Validate route references during deployment."
        ),
    )

    print()
    print("Embedding Text:")
    print("--------------------------------------------")
    print(embedding_text)
    print("--------------------------------------------")

    # -------------------------------------------------------------------------
    # 2. Generate embedding
    # -------------------------------------------------------------------------

    embedding_service = EmbeddingService()

    embedding = await embedding_service.embed_text(
        embedding_text
    )

    # -------------------------------------------------------------------------
    # 3. Store in PostgreSQL
    # -------------------------------------------------------------------------

    knowledge_store = KnowledgeStore()

    knowledge_id = await knowledge_store.store_knowledge(
        error=error,
        embedding=embedding,
        embedding_text=embedding_text,
        analysis={
            "error_signature": (
                "laravel.route_not_defined"
            ),
            "root_cause": (
                "The application references a Laravel route "
                "that is not registered."
            ),
            "solution": (
                "Register the route or correct the route reference."
            ),
            "optimization": (
                "Validate route references during deployment."
            ),
            "status": "resolved",
            "verified": False,
            "test_result": {
                "status": "not_run",
            },
            "jira_description": (
                "Fix missing Laravel route reference."
            ),
        },
    )

    print()
    print("=" * 100)
    print(
        f"RAG KNOWLEDGE STORED SUCCESSFULLY: {knowledge_id}"
    )
    print("=" * 100)


if __name__ == "__main__":
    asyncio.run(main())