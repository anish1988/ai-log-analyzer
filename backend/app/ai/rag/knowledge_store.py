"""
RAG Knowledge Store.

Stores analyzed errors and their embeddings in:

    PostgreSQL
        +
    pgvector

Table:

    ai_knowledge_items
"""

import os
from typing import Any

import psycopg
from pgvector.psycopg import register_vector_async
from psycopg.types.json import Jsonb

from app.ai.graph.state import AIAnalysisResult, SelectedError


class KnowledgeStore:
    """
    PostgreSQL repository for RAG knowledge.

    LangGraph decides WHEN knowledge should be stored.

    KnowledgeStore decides HOW it is stored.
    """

    def __init__(self) -> None:

        self.host = os.getenv(
            "POSTGRES_HOST",
            "postgres",
        )

        self.port = int(
            os.getenv(
                "POSTGRES_PORT",
                "5432",
            )
        )

        self.database = os.getenv(
            "POSTGRES_DB",
            "ai_log_analyzer",
        )

        self.user = os.getenv(
            "POSTGRES_USER",
            "postgres",
        )

        self.password = os.getenv(
            "POSTGRES_PASSWORD",
            "postgres",
        )

    async def _connect(self):

        connection = await psycopg.AsyncConnection.connect(
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.user,
            password=self.password,
        )

        await register_vector_async(connection)

        return connection

    async def store_knowledge(
        self,
        *,
        error: SelectedError,
        embedding: list[float],
        embedding_text: str,
        analysis: AIAnalysisResult | None = None,
    ) -> int:
        """
        Store one analyzed error in the RAG knowledge base.

        Returns:
            Database ID of the inserted knowledge item.
        """

        analysis = analysis or {}

        evidence = error.get(
            "lines",
            [],
        )

        root_cause_evidence = analysis.get(
            "root_cause_evidence",
            [],
        )

        test_result = analysis.get(
            "test_result",
            {},
        )

        metadata = {
            "source": "ai_analysis",
            "embedding_provider": os.getenv(
                "AI_PROVIDER",
                "openai",
            ),
            "embedding_model": os.getenv(
                "GEMINI_EMBEDDING_MODEL"
                if os.getenv("AI_PROVIDER") == "gemini"
                else "OPENAI_EMBEDDING_MODEL",
                "gemini-embedding-001"
                if os.getenv("AI_PROVIDER") == "gemini"
                else "text-embedding-3-small",
            ),
        }

        print("=" * 100)
        print("RAG KNOWLEDGE STORE")
        print("=" * 100)

        print(
            f"Log Type        : {error.get('log_type', '')}"
        )

        print(
            f"File            : {error.get('file_name', '')}"
        )

        print( f"Error ID        : {error.get('error_id', '')}" )

        print( f"Embedding Size  : {len(embedding)}" )

        connection = await self._connect()

        try:

            async with connection.cursor() as cursor:

                await cursor.execute(
                    """
                    INSERT INTO ai_knowledge_items (
                        tier,
                        log_type,
                        server,
                        file_name,
                        file_path,
                        error_id,
                        error_signature,
                        title,
                        severity,
                        timestamp,
                        error_content,
                        evidence,
                        root_cause,
                        root_cause_evidence,
                        solution,
                        optimization,
                        test_result,
                        jira_description,
                        resolution_status,
                        verified,
                        verification_notes,
                        embedding_text,
                        embedding,
                        metadata
                    )
                    VALUES (
                        %(tier)s,
                        %(log_type)s,
                        %(server)s,
                        %(file_name)s,
                        %(file_path)s,
                        %(error_id)s,
                        %(error_signature)s,
                        %(title)s,
                        %(severity)s,
                        %(timestamp)s,
                        %(error_content)s,
                        %(evidence)s,
                        %(root_cause)s,
                        %(root_cause_evidence)s,
                        %(solution)s,
                        %(optimization)s,
                        %(test_result)s,
                        %(jira_description)s,
                        %(resolution_status)s,
                        %(verified)s,
                        %(verification_notes)s,
                        %(embedding_text)s,
                        %(embedding)s,
                        %(metadata)s
                    )
                    RETURNING id
                    """,
                    {
                        "tier": error.get(
                            "tier",
                            "",
                        ),

                        "log_type": error.get(
                            "log_type",
                            "",
                        ),

                        "server": error.get(
                            "server",
                            "",
                        ),

                        "file_name": error.get(
                            "file_name",
                            "",
                        ),

                        "file_path": error.get(
                            "file_path",
                            "",
                        ),

                        "error_id": error.get(
                            "error_id",
                            "",
                        ),

                        "error_signature": analysis.get(
                            "error_signature",
                            "",
                        ),

                        "title": error.get(
                            "title",
                            "",
                        ),

                        "severity": error.get(
                            "severity",
                            "",
                        ),

                        "timestamp": error.get(
                            "timestamp",
                            "",
                        ),

                        "error_content": error.get(
                            "error_content",
                            "",
                        ),

                        "evidence": Jsonb(
                            evidence
                        ),

                        "root_cause": analysis.get(
                            "root_cause",
                            "",
                        ),

                        "root_cause_evidence": Jsonb(
                            root_cause_evidence
                        ),

                        "solution": analysis.get(
                            "solution",
                            "",
                        ),

                        "optimization": analysis.get(
                            "optimization",
                            "",
                        ),

                        "test_result": Jsonb(
                            test_result
                        ),

                        "jira_description": analysis.get(
                            "jira_description",
                            "",
                        ),

                        "resolution_status": analysis.get(
                            "status",
                            "unknown",
                        ),

                        "verified": analysis.get(
                            "verified",
                            False,
                        ),

                        "verification_notes": analysis.get(
                            "verification_notes",
                            "",
                        ),

                        "embedding_text": embedding_text,

                        # pgvector + Psycopg 3 handles the list
                        # after register_vector_async().
                        "embedding": embedding,

                        "metadata": Jsonb(
                            metadata
                        ),
                    },
                )

                row = await cursor.fetchone()

                if row is None:

                    raise RuntimeError(
                        "Failed to insert AI knowledge item."
                    )

                knowledge_id = int(
                    row[0]
                )

            await connection.commit()

            print(
                f"Knowledge ID    : {knowledge_id}"
            )

            print("=" * 100)

            return knowledge_id

        except Exception:

            await connection.rollback()

            raise

        finally:

            await connection.close()