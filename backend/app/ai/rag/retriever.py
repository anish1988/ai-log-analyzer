"""
RAG Retriever.

Responsible for finding historically similar errors
from the PostgreSQL + pgvector knowledge store.

This class does NOT decide whether a RAG result should
be trusted.

It only retrieves candidates.

The confidence / reuse decision will be implemented
in Step 3.6.
"""

import os
from typing import Any

import psycopg
#from pgvector.psycopg import register_vector_async
#from pgvector import Vector
from pgvector.psycopg import Vector, register_vector_async

from app.ai.graph.state import RAGMatch


class RAGRetriever:
    """
    Retrieves similar historical errors from pgvector.
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

        await register_vector_async(
            connection
        )

        return connection

    async def search(
        self,
        *,
        embedding: list[float],
        tier: str | None = None,
        log_type: str | None = None,
        limit: int = 5,
        error_signature: str | None = None,
        min_similarity: float = 0.0,
    ) -> list[RAGMatch]:
        """
        Find similar historical knowledge items.

        Parameters
        ----------
        embedding:
            Query embedding.

        tier:
            Optional tier filter.

        log_type:
            Optional log type filter.

        limit:
            Maximum number of results.

        min_similarity:
            Minimum cosine similarity.

        Returns
        -------
        list[RAGMatch]
            Similar historical errors.

        Important:
            This method only retrieves candidates.

            It does NOT decide whether the result is safe
            enough to reuse.
        """

        if not embedding:

            raise ValueError(
                "Embedding cannot be empty."
            )

        if limit <= 0:

            raise ValueError(
                "limit must be greater than zero."
            )

        print("=" * 100)
        print("RAG RETRIEVER")
        print("=" * 100)

        print(
            f"Embedding Size  : {len(embedding)}"
        )

        print(
            f"Tier Filter      : {tier}"
        )

        print(
            f"Log Type Filter  : {log_type}"
        )

        print(
            f"Limit            : {limit}"
        )

        print(
            f"Min Similarity   : {min_similarity}"
        )

        connection = await self._connect()

        try:

            async with connection.cursor() as cursor:

                # ----------------------------------------------------------------
                # Build filtering conditions.
                #
                # We deliberately filter by tier/log_type BEFORE the final
                # RAG decision.
                #
                # Example:
                #
                # web + laravel
                #
                # should not automatically compete with:
                #
                # telephony + asterisk
                # ----------------------------------------------------------------

                conditions: list[str] = []

                query_embedding = Vector(embedding)

                print(
                    f"Query Vector Type : {type(query_embedding).__name__}"
                )

                parameters: dict[str, Any] = {
                    "embedding": query_embedding,
                    "error_signature": error_signature,
                    "limit": limit,
                    "min_similarity": min_similarity,
                }

                if tier:

                    conditions.append(
                        "tier = %(tier)s"
                    )

                    parameters["tier"] = tier

                if log_type:

                    conditions.append(
                        "log_type = %(log_type)s"
                    )

                    parameters["log_type"] = log_type

                where_clause = ""

                if conditions:

                    where_clause = (
                        "WHERE "
                        + " AND ".join(
                            conditions
                        )
                    )

                # ----------------------------------------------------------------
                # Cosine similarity:
                #
                # pgvector:
                #
                #     embedding <=> query_embedding
                #
                # returns cosine DISTANCE.
                #
                # Therefore:
                #
                #     similarity = 1 - distance
                # ----------------------------------------------------------------

                query = f"""
                    SELECT
                        id,
                        tier,
                        log_type,
                        server,
                        file_name,
                        error_id,
                        error_signature,
                        title,
                        root_cause,
                        solution,
                        optimization,
                        test_result,
                        jira_description,
                        resolution_status,
                        verified,
                        evidence,
                        metadata,

                        1 - (
                            embedding <=> %(embedding)s
                        ) AS similarity

                    FROM ai_knowledge_items

                    {where_clause}

                    AND embedding IS NOT NULL

                    AND (
                        1 - (
                            embedding <=> %(embedding)s
                        )
                    ) >= %(min_similarity)s

                    ORDER BY
                        embedding <=> %(embedding)s

                    LIMIT %(limit)s
                """

                # ---------------------------------------------------------------
                # If no WHERE clause exists, the generated query currently
                # starts with:
                #
                #     FROM ai_knowledge_items
                #
                # and then:
                #
                #     AND embedding IS NOT NULL
                #
                # which is invalid SQL.
                #
                # We therefore build the embedding condition correctly here.
                # ---------------------------------------------------------------

                base_conditions = conditions.copy()

                base_conditions.append(
                    "embedding IS NOT NULL"
                )

                base_conditions.append(
                    """
                    (
                        1 - (
                            embedding <=> %(embedding)s
                        )
                    ) >= %(min_similarity)s
                    """
                )

                where_clause = (
                    "WHERE "
                    + " AND ".join(
                        base_conditions
                    )
                )

                query = f"""
                    SELECT
                        id,
                        tier,
                        log_type,
                        server,
                        file_name,
                        error_id,
                        error_signature,
                        title,
                        root_cause,
                        solution,
                        optimization,
                        test_result,
                        jira_description,
                        resolution_status,
                        verified,
                        evidence,
                        metadata,

                        1 - (
                            embedding <=> %(embedding)s
                        ) AS similarity

                    FROM ai_knowledge_items

                    {where_clause}

                    ORDER BY
                        CASE
                            WHEN  error_signature = %(error_signature)s
                            THEN 0
                            ELSE 1
                        END,
                        embedding <=> %(embedding)s

                    LIMIT %(limit)s
                """

                await cursor.execute(
                    query,
                    parameters,
                )

                rows = await cursor.fetchall()

            results: list[RAGMatch] = []

            for row in rows:

                (
                    knowledge_id,
                    result_tier,
                    result_log_type,
                    server,
                    file_name,
                    error_id,
                    error_signature,
                    title,
                    root_cause,
                    solution,
                    optimization,
                    test_result,
                    jira_description,
                    resolution_status,
                    verified,
                    evidence,
                    metadata,
                    similarity,
                ) = row

                result: RAGMatch = {

                    "knowledge_id": int(
                        knowledge_id
                    ),

                    "similarity": float(
                        similarity
                    ),

                    "tier": result_tier,

                    "log_type": result_log_type,

                    "error_signature": (
                        error_signature or ""
                    ),

                    "title": (
                        title or ""
                    ),

                    "root_cause": (
                        root_cause or ""
                    ),

                    "solution": (
                        solution or ""
                    ),

                    "optimization": (
                        optimization or ""
                    ),

                    "test_result": (
                        test_result or {}
                    ),

                    "jira_description": (
                        jira_description or ""
                    ),

                    "resolution_status": (
                        resolution_status or ""
                    ),

                    "verified": bool(
                        verified
                    ),

                    "evidence": (
                        evidence or []
                    ),

                    "metadata": (
                        metadata or {}
                    ),
                }

                results.append(
                    result
                )

                print(
                    "----------------------------------------"
                )

                print(
                    f"Knowledge ID : {knowledge_id}"
                )

                print(
                    f"Similarity   : {similarity:.6f}"
                )

                print(
                    f"Tier         : {result_tier}"
                )

                print(
                    f"Log Type     : {result_log_type}"
                )

                print(
                    f"Error ID     : {error_id}"
                )

                print(
                    f"Title        : {title}"
                )

                print(
                    f"Verified     : {verified}"
                )

            print("=" * 100)
            print(
                f"Total Matches : {len(results)}"
            )
            print("=" * 100)

            return results

        finally:

            await connection.close()