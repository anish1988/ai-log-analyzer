"""
LangGraph LLM analysis node.

This node is responsible for calling the appropriate
log-type-specific analyzer when the RAG decision says
that LLM processing is required.

RAG itself is NOT performed here.

RAG remains handled by the existing RAG nodes.
"""

from typing import Any

from app.ai.llm.analyzers import AnalyzerFactory
from app.ai.llm.llm_service import LLMService


# =============================================================================
# LLM SERVICE
# =============================================================================

_llm_service = LLMService()


# =============================================================================
# LLM ANALYSIS NODE
# =============================================================================

async def run_llm_analysis(
    state: dict[str, Any],
) -> dict[str, Any]:

    print("=" * 100)
    print("LANGGRAPH - LLM ANALYSIS NODE")
    print("=" * 100)

    current_error = state.get(
        "current_error"
    )

    if not current_error:

        raise ValueError(
            "current_error is missing from "
            "LangGraph state."
        )

    log_type = current_error.get(
        "log_type"
    )

    if not log_type:

        raise ValueError(
            "log_type is missing from current_error."
        )

    print(
        f"Error ID : "
        f"{current_error.get('error_id')}"
    )

    print(
        f"Log Type : "
        f"{log_type}"
    )

    # -------------------------------------------------------------------------
    # RAG decision
    # -------------------------------------------------------------------------

    rag_decision = state.get(
        "rag_decision"
    )

    print(
        f"RAG Decision : "
        f"{rag_decision}"
    )

    # -------------------------------------------------------------------------
    # IMPORTANT
    #
    # REUSE should never reach this node.
    # -------------------------------------------------------------------------

    if rag_decision == "REUSE":

        print(
            "RAG decision is REUSE."
        )

        print(
            "LLM call will NOT be performed."
        )

        return {
            "current_ai_result": state.get(
                "rag_result"
            )
        }

    # -------------------------------------------------------------------------
    # Historical RAG context
    # -------------------------------------------------------------------------

    historical_context = state.get(
        "rag_result"
    )

    print(
        "Historical RAG Context:"
    )

    print(
        historical_context
    )

    # -------------------------------------------------------------------------
    # Select analyzer
    # -------------------------------------------------------------------------

    analyzer = AnalyzerFactory.get_analyzer(
        log_type=log_type,
        llm_service=_llm_service,
    )

    print(
        "Analyzer Selected:"
    )

    print(
        analyzer.__class__.__name__
    )

    # -------------------------------------------------------------------------
    # Call LLM analyzer
    # -------------------------------------------------------------------------

    result = await analyzer.analyze(
        error=current_error,
        historical_context=(
            historical_context
            if rag_decision == "REVIEW"
            else None
        ),
    )

    print("=" * 100)
    print("LLM ANALYSIS COMPLETED")
    print("=" * 100)

    print(
        f"Error ID : "
        f"{current_error.get('error_id')}"
    )

    # -------------------------------------------------------------------------
    # Convert structured Pydantic response to dict
    #
    # WebAIAnalysisResponse and future Telephony/MySQL response
    # models can therefore be stored consistently in final_results.
    # -------------------------------------------------------------------------

    if hasattr(result, "model_dump"):

        ai_result = result.model_dump()

    elif isinstance(result, dict):

        ai_result = result

    else:

        raise TypeError(
            "LLM analyzer returned an unsupported "
            f"result type: {type(result).__name__}"
        )

    # -------------------------------------------------------------------------
    # Add common error metadata
    #
    # The analyzer response contains the AI analysis fields.
    # We enrich it with information coming from the selected error.
    # -------------------------------------------------------------------------

    ai_result = {
        **ai_result,

        "error_id": current_error.get(
            "error_id",
            "",
        ),

        "tier": current_error.get(
            "tier",
            "",
        ),

        "log_type": current_error.get(
            "log_type",
            "",
        ),

        "server": current_error.get(
            "server",
            "",
        ),

        "file_name": current_error.get(
            "file_name",
            "",
        ),

        "title": current_error.get(
            "title",
            "",
        ),

        "severity": ai_result.get(
            "severity",
            "",
        ),

        "timestamp": current_error.get(
            "timestamp",
            "",
        ),

        "start_line": current_error.get(
            "start_line",
            0,
        ),

        "end_line": current_error.get(
            "end_line",
            0,
        ),

        "source": "llm",

        "rag_match": state.get(
            "rag_match_found",
            False,
        ),

        "rag_knowledge_id": (
            (
                state.get(
                    "rag_selected_match"
                )
                or {}
            ).get(
                "knowledge_id"
            )
        ),

        "rag_similarity": state.get(
            "rag_similarity"
        ),

        "confidence": state.get(
            "rag_confidence",
            "none",
        ),

        "status": "completed",

        "error": None,
    }

    # -------------------------------------------------------------------------
    # IMPORTANT:
    #
    # Append this error's result to the existing final_results.
    #
    # This is what was missing.
    # -------------------------------------------------------------------------

    final_results = list(
        state.get(
            "final_results",
            [],
        )
    )

    final_results.append(
        ai_result
    )

    print("=" * 100)
    print("LANGGRAPH - FINAL RESULT APPENDED")
    print("=" * 100)

    print(
        f"Error ID       : "
        f"{current_error.get('error_id')}"
    )

    print(
        f"Final Results  : "
        f"{len(final_results)}"
    )

    return {

        "current_ai_result": ai_result,

        "final_results": final_results,

        "current_task": (
            "LLM analysis completed"
        ),

        "progress": 80,

        "error": None,
    }