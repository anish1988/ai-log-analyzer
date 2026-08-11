"""
Standalone tests for the RAG Decision Engine.
"""

from app.ai.rag.decision_engine import (
    RAGDecision,
    RAGDecisionEngine,
)


def create_match(
    *,
    similarity: float,
    verified: bool,
    resolution_status: str,
):
    return {
        "knowledge_id": 1,
        "similarity": similarity,
        "tier": "web",
        "log_type": "laravel",
        "error_signature": "laravel.route_not_defined",
        "title": "Route not defined",
        "root_cause": "Route is not registered.",
        "solution": "Register the route.",
        "optimization": "Validate routes.",
        "test_result": {},
        "jira_description": "",
        "resolution_status": resolution_status,
        "verified": verified,
        "evidence": [],
        "metadata": {},
    }


def main():

    engine = RAGDecisionEngine()

    # =========================================================================
    # TEST 1
    # High similarity + verified + resolved
    # =========================================================================

    result = engine.decide(
        [
            create_match(
                similarity=0.97,
                verified=True,
                resolution_status="verified",
            )
        ]
    )

    print(
        "TEST 1:",
        result.decision,
    )

    assert result.decision == RAGDecision.REUSE

    # =========================================================================
    # TEST 2
    # High similarity but NOT verified
    # =========================================================================

    result = engine.decide(
        [
            create_match(
                similarity=0.97,
                verified=False,
                resolution_status="resolved",
            )
        ]
    )

    print(
        "TEST 2:",
        result.decision,
    )

    assert result.decision == RAGDecision.REVIEW

    # =========================================================================
    # TEST 3
    # Medium similarity
    # =========================================================================

    result = engine.decide(
        [
            create_match(
                similarity=0.85,
                verified=True,
                resolution_status="verified",
            )
        ]
    )

    print(
        "TEST 3:",
        result.decision,
    )

    assert result.decision == RAGDecision.REVIEW

    # =========================================================================
    # TEST 4
    # Low similarity
    # =========================================================================

    result = engine.decide(
        [
            create_match(
                similarity=0.50,
                verified=True,
                resolution_status="verified",
            )
        ]
    )

    print(
        "TEST 4:",
        result.decision,
    )

    assert result.decision == RAGDecision.LLM_REQUIRED

    # =========================================================================
    # TEST 5
    # No matches
    # =========================================================================

    result = engine.decide([])

    print(
        "TEST 5:",
        result.decision,
    )

    assert result.decision == RAGDecision.LLM_REQUIRED

    print()
    print("=" * 100)
    print("ALL RAG DECISION TESTS PASSED")
    print("=" * 100)


if __name__ == "__main__":
    main()