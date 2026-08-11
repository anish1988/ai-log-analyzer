"""
RAG Decision Engine.

Responsible for deciding what should happen after RAG retrieval.

Possible decisions:

    REUSE
        A sufficiently similar and verified historical resolution
        can be reused.

    REVIEW
        A potentially similar historical issue exists, but it is
        not safe enough to automatically reuse.

    LLM_REQUIRED
        No sufficiently useful historical solution exists.
        The error should proceed to LLM analysis.

Important:

    RAGRetriever retrieves candidates.

    RAGDecisionEngine decides what to do with those candidates.

These responsibilities are intentionally separate.
"""

from dataclasses import dataclass
from enum import Enum

from app.ai.graph.state import RAGMatch


# =============================================================================
# DECISION
# =============================================================================


class RAGDecision(str, Enum):
    """
    Possible decisions after RAG retrieval.
    """

    REUSE = "reuse"

    REVIEW = "review"

    LLM_REQUIRED = "llm_required"


# =============================================================================
# DECISION RESULT
# =============================================================================


@dataclass
class RAGDecisionResult:
    """
    Result produced by the RAG Decision Engine.
    """

    decision: RAGDecision

    match: RAGMatch | None

    similarity: float | None

    reason: str

    confidence: str


# =============================================================================
# DECISION ENGINE
# =============================================================================


class RAGDecisionEngine:
    """
    Determines whether a retrieved historical solution can be reused.

    Initial policy:

        REUSE
            similarity >= 0.92
            AND verified == True
            AND resolution_status is verified/resolved

        REVIEW
            similarity >= 0.80

        LLM_REQUIRED
            similarity < 0.80
            OR no match

    These thresholds are intentionally configurable.
    """

    DEFAULT_REUSE_THRESHOLD = 0.92

    DEFAULT_REVIEW_THRESHOLD = 0.80

    def __init__(
        self,
        *,
        reuse_threshold: float = DEFAULT_REUSE_THRESHOLD,
        review_threshold: float = DEFAULT_REVIEW_THRESHOLD,
    ) -> None:

        if not 0.0 <= review_threshold <= 1.0:

            raise ValueError(
                "review_threshold must be between 0.0 and 1.0."
            )

        if not 0.0 <= reuse_threshold <= 1.0:

            raise ValueError(
                "reuse_threshold must be between 0.0 and 1.0."
            )

        if review_threshold > reuse_threshold:

            raise ValueError(
                "review_threshold cannot be greater than "
                "reuse_threshold."
            )

        self.reuse_threshold = reuse_threshold

        self.review_threshold = review_threshold

    # =========================================================================
    # PUBLIC METHOD
    # =========================================================================

    def decide(
        self,
        matches: list[RAGMatch],
    ) -> RAGDecisionResult:
        """
        Decide what should happen with the retrieved matches.

        The first result is expected to be the highest-similarity
        candidate because RAGRetriever orders results by similarity.

        Parameters
        ----------
        matches:
            Candidates returned by RAGRetriever.

        Returns
        -------
        RAGDecisionResult
        """

        print("=" * 100)
        print("RAG DECISION ENGINE")
        print("=" * 100)

        print(
            f"Candidates       : {len(matches)}"
        )

        print(
            f"Reuse Threshold  : {self.reuse_threshold}"
        )

        print(
            f"Review Threshold : {self.review_threshold}"
        )

        # =====================================================================
        # NO MATCH
        # =====================================================================

        if not matches:

            print(
                "Decision         : LLM_REQUIRED"
            )

            print(
                "Reason           : No RAG match found."
            )

            print("=" * 100)

            return RAGDecisionResult(
                decision=RAGDecision.LLM_REQUIRED,
                match=None,
                similarity=None,
                reason=(
                    "No sufficiently similar historical "
                    "error was found."
                ),
                confidence="none",
            )

        # =====================================================================
        # BEST MATCH
        # =====================================================================

        best_match = matches[0]

        similarity = float(
            best_match.get(
                "similarity",
                0.0,
            )
        )

        verified = bool(
            best_match.get(
                "verified",
                False,
            )
        )

        resolution_status = (
            best_match.get(
                "resolution_status",
                "",
            )
            or ""
        ).lower()

        print(
            f"Best Match ID    : "
            f"{best_match.get('knowledge_id')}"
        )

        print(
            f"Similarity       : {similarity:.6f}"
        )

        print(
            f"Verified         : {verified}"
        )

        print(
            f"Resolution       : {resolution_status}"
        )

        # =====================================================================
        # REUSE DECISION
        # =====================================================================

        if (
            similarity >= self.reuse_threshold
            and verified
            and resolution_status in {
                "verified",
                "resolved",
            }
        ):

            print(
                "Decision         : REUSE"
            )

            print(
                "Reason           : "
                "High similarity + verified resolution."
            )

            print("=" * 100)

            return RAGDecisionResult(
                decision=RAGDecision.REUSE,
                match=best_match,
                similarity=similarity,
                reason=(
                    "A highly similar historical error was found "
                    "with a verified resolution."
                ),
                confidence="high",
            )

        # =====================================================================
        # REVIEW DECISION
        # =====================================================================

        if similarity >= self.review_threshold:

            print(
                "Decision         : REVIEW"
            )

            print(
                "Reason           : "
                "Potentially similar historical error found."
            )

            print("=" * 100)

            return RAGDecisionResult(
                decision=RAGDecision.REVIEW,
                match=best_match,
                similarity=similarity,
                reason=(
                    "A potentially similar historical error was "
                    "found, but the resolution is not sufficiently "
                    "trusted for automatic reuse."
                ),
                confidence="medium",
            )

        # =====================================================================
        # LLM REQUIRED
        # =====================================================================

        print(
            "Decision         : LLM_REQUIRED"
        )

        print(
            "Reason           : "
            "Similarity is below the review threshold."
        )

        print("=" * 100)

        return RAGDecisionResult(
            decision=RAGDecision.LLM_REQUIRED,
            match=best_match,
            similarity=similarity,
            reason=(
                "No sufficiently similar historical resolution "
                "was found."
            ),
            confidence="low",
        )