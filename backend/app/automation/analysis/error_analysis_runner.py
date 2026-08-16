"""
Phase 3.4 - Existing Error Analysis Workflow Adapter.

This module connects the standalone Phase 3 automation pipeline
to the existing AI analysis workflow.

IMPORTANT:
    Do NOT duplicate RAG or LLM logic here.

The existing LangGraph workflow remains the single source of truth
for:

    Error preparation
        ↓
    Embedding generation
        ↓
    RAG retrieval
        ↓
    RAG decision
        ↓
    Historical solution reuse
        OR
    Log-type specific LLM analysis
        ↓
    Final AI result
"""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.ai.graph.workflow import (
    build_ai_analysis_graph,
)


class ErrorAnalysisRunner:
    """
    Adapter between Phase 3 automation and the existing
    LangGraph AI analysis workflow.

    This class does NOT implement:
        - embeddings
        - RAG
        - RAG decision
        - LLM calls
        - analyzers

    All of those remain inside the existing AI workflow.
    """

    def __init__(self) -> None:
        self.graph = build_ai_analysis_graph()

    async def analyze(
        self,
        *,
        errors: list[dict[str, Any]],
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Send parsed errors to the existing LangGraph workflow.

        Parameters
        ----------
        errors:
            Parsed errors produced by the existing parser.

        request_id:
            Optional automation request/run identifier.

        Returns
        -------
        dict:
            Final LangGraph state.
        """

        if not errors:
            return {
                "request_id": (
                    request_id
                    or f"AUTO-AI-{uuid4()}"
                ),
                "selected_errors": [],
                "final_results": [],
                "status": "completed",
                "progress": 100,
                "error": None,
            }

        resolved_request_id = (
            request_id
            or f"AUTO-AI-{uuid4()}"
        )

        print("=" * 100)
        print("PHASE 3.4 - ERROR ANALYSIS RUNNER")
        print("=" * 100)

        print(
            f"Request ID    : "
            f"{resolved_request_id}"
        )

        print(
            f"Selected Errors : "
            f"{len(errors)}"
        )

        print("=" * 100)

        # ---------------------------------------------------------
        # Build the exact state expected by the existing LangGraph.
        #
        # This is the same state shape currently constructed by
        # app/api/ai_analysis.py.
        # ---------------------------------------------------------

        initial_state = {
            "request_id": resolved_request_id,

            "selected_errors": errors,

            "current_error_index": 0,

            "current_error": None,

            "final_results": [],

            "progress_events": [],

            "messages": [],

            "status": "processing",

            "progress": 0,

            "error": None,
        }

        # ---------------------------------------------------------
        # EXISTING LANGGRAPH
        #
        # No duplicated RAG / LLM implementation.
        # ---------------------------------------------------------

        print(
            "Starting existing LangGraph..."
        )

        result = await self.graph.ainvoke(
            initial_state
        )

        print("=" * 100)
        print("PHASE 3.4 - LANGGRAPH COMPLETED")
        print("=" * 100)

        print(
            f"Request ID     : "
            f"{resolved_request_id}"
        )

        print(
            f"Final Results  : "
            f"{len(result.get('final_results', []))}"
        )

        print(
            f"Status         : "
            f"{result.get('status')}"
        )

        print("=" * 100)

        return result