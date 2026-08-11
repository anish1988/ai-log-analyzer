"""
LangGraph AI Analysis Workflow.

Step 3.7

This workflow connects the components created in previous steps:

    1. Prepare selected errors
    2. Build embedding text
    3. Generate embedding
    4. Retrieve similar historical issues
    5. Run RAG decision engine
    6. Reuse historical resolution OR mark for future LLM processing
    7. Move to the next selected error
    8. Produce final results

The actual LLM analysis is intentionally NOT implemented here yet.

That will be added in the next AI-analysis phase.
"""

from typing import Literal
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from app.ai.graph.state import (
    AIAnalysisResult,
    AIAnalysisState,
    SelectedError,
)
from app.ai.rag.decision_engine import (
    RAGDecision,
    RAGDecisionEngine,
)
from app.ai.rag.embedding_service import EmbeddingService
from app.ai.rag.embedding_text import build_embedding_text
from app.ai.rag.retriever import RAGRetriever


# =============================================================================
# SERVICES
# =============================================================================

embedding_service = EmbeddingService()

rag_retriever = RAGRetriever()

rag_decision_engine = RAGDecisionEngine()


# =============================================================================
# NODE 1
# INITIALIZE
# =============================================================================


def initialize_analysis(
    state: AIAnalysisState,
) -> dict:
    """
    Initialize the AI analysis workflow.
    """

    selected_errors = state.get(
        "selected_errors",
        [],
    )

    print("=" * 100)
    print("LANGGRAPH - INITIALIZE ANALYSIS")
    print("=" * 100)

    print(
        f"Selected Errors : {len(selected_errors)}"
    )

    return {
        "request_id": state.get(
            "request_id",
            str(uuid4()),
        ),

        "current_error_index": 0,

        "current_error": None,

        "final_results": [],

        "status": "processing",

        "current_task": (
            "Preparing selected errors"
        ),

        "progress": 0,

        "messages": [
            "AI analysis workflow started."
        ],

        "error": None,
    }


# =============================================================================
# NODE 2
# PREPARE CURRENT ERROR
# =============================================================================


def prepare_current_error(
    state: AIAnalysisState,
) -> dict:
    """
    Load the current error from selected_errors.
    """

    selected_errors = state.get(
        "selected_errors",
        [],
    )

    current_index = state.get(
        "current_error_index",
        0,
    )

    print("=" * 100)
    print("LANGGRAPH - PREPARE CURRENT ERROR")
    print("=" * 100)

    print(
        f"Current Index : {current_index}"
    )

    if current_index >= len(
        selected_errors
    ):

        return {
            "current_error": None,

            "current_task": (
                "No more errors to process"
            ),

            "progress": 100,
        }

    current_error = selected_errors[
        current_index
    ]

    print(
        f"Error ID      : "
        f"{current_error.get('error_id', '')}"
    )

    print(
        f"Log Type      : "
        f"{current_error.get('log_type', '')}"
    )

    print(
        f"File          : "
        f"{current_error.get('file_name', '')}"
    )

    return {
        "current_error": current_error,

        "tier": current_error.get(
            "tier",
            "",
        ),

        "log_type": current_error.get(
            "log_type",
            "",
        ),

        "current_task": (
            "Evaluating error parameters"
        ),

        "progress": 10,

        "error": None,
    }


# =============================================================================
# NODE 3
# BUILD EMBEDDING TEXT
# =============================================================================


def prepare_rag_query(
    state: AIAnalysisState,
) -> dict:
    """
    Build the semantic representation used for RAG.

    At this point we only know the original error.

    Root cause and solution are intentionally NOT included
    because they are not known yet for a new error.
    """

    current_error = state.get(
        "current_error"
    )

    if not current_error:

        return {
            "error": (
                "Current error is missing."
            ),

            "status": "error",
        }

    embedding_text = build_embedding_text(
        current_error
    )

    # -------------------------------------------------------------------------
    # Initial normalized representation.
    #
    # This is intentionally simple for Step 3.7.
    #
    # A dedicated normalization/signature stage can be enhanced later without
    # changing the overall workflow architecture.
    # -------------------------------------------------------------------------

    title = (
        current_error.get(
            "title",
            "",
        )
        or ""
    ).strip()

    log_type = (
        current_error.get(
            "log_type",
            "",
        )
        or ""
    ).strip().lower()

    error_signature = (
        f"{log_type}:{title.lower()}"
    )[:500]

    normalized_error = {
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

        "error_id": current_error.get(
            "error_id",
            "",
        ),

        "title": title,

        "severity": current_error.get(
            "severity",
            "",
        ),

        "timestamp": current_error.get(
            "timestamp",
            "",
        ),

        "error_signature": error_signature,
    }

    print("=" * 100)
    print("LANGGRAPH - PREPARE RAG QUERY")
    print("=" * 100)

    print(
        f"Error Signature : {error_signature}"
    )

    print(
        f"Embedding Text Length : "
        f"{len(embedding_text)}"
    )

    return {
        "normalized_error": normalized_error,

        "error_signature": error_signature,

        "embedding_text": embedding_text,

        "rag_query": embedding_text,

        "current_task": (
            "Preparing RAG search"
        ),

        "progress": 20,

        "error": None,
    }


# =============================================================================
# NODE 4
# GENERATE EMBEDDING
# =============================================================================


async def generate_rag_embedding(
    state: AIAnalysisState,
) -> dict:
    """
    Generate the vector representation of the current error.
    """

    embedding_text = state.get(
        "embedding_text",
        "",
    )

    if not embedding_text:

        return {
            "error": (
                "Embedding text is empty."
            ),

            "status": "error",
        }

    print("=" * 100)
    print("LANGGRAPH - GENERATE RAG EMBEDDING")
    print("=" * 100)

    embedding = await embedding_service.embed_text(
        embedding_text
    )

    print(
        f"Embedding Size : {len(embedding)}"
    )

    # -------------------------------------------------------------------------
    # The current state schema doesn't have a dedicated `embedding` field.
    #
    # Therefore we keep the vector in normalized_error for now.
    #
    # This avoids modifying the frozen Step 3.3 state.
    # -------------------------------------------------------------------------

    normalized_error = dict(
        state.get(
            "normalized_error",
            {},
        )
    )

    normalized_error[
        "embedding"
    ] = embedding

    return {
        "normalized_error": normalized_error,

        "current_task": (
            "Searching historical knowledge"
        ),

        "progress": 30,

        "error": None,
    }


# =============================================================================
# NODE 5
# RAG RETRIEVAL
# =============================================================================


async def retrieve_rag_matches(
    state: AIAnalysisState,
) -> dict:
    """
    Search PostgreSQL + pgvector for similar errors.
    """

    normalized_error = state.get(
        "normalized_error",
        {},
    )

    embedding = normalized_error.get(
        "embedding"
    )

    if not embedding:

        return {
            "error": (
                "RAG embedding is missing."
            ),

            "status": "error",
        }

    tier = normalized_error.get(
        "tier"
    )

    log_type = normalized_error.get(
        "log_type"
    )

    print("=" * 100)
    print("LANGGRAPH - RAG RETRIEVAL")
    print("=" * 100)

    matches = await rag_retriever.search(
        embedding=embedding,

        tier=tier,

        log_type=log_type,

        limit=5,

        min_similarity=0.0,
    )

    print(
        f"RAG Matches : {len(matches)}"
    )

    return {
        "rag_matches": matches,

        "current_task": (
            "Evaluating historical solutions"
        ),

        "progress": 45,

        "error": None,
    }


# =============================================================================
# NODE 6
# RAG DECISION
# =============================================================================


def decide_rag(
    state: AIAnalysisState,
) -> dict:
    """
    Decide whether the historical knowledge can be reused.
    """

    matches = state.get(
        "rag_matches",
        [],
    )

    print("=" * 100)
    print("LANGGRAPH - RAG DECISION")
    print("=" * 100)

    decision = rag_decision_engine.decide(
        matches
    )

    # -------------------------------------------------------------------------
    # We don't modify the frozen Step 3.3 state to add a `rag_decision`
    # field.
    #
    # Instead:
    #
    #     high confidence → rag_reuse_solution=True
    #     medium confidence → rag_reuse_solution=False
    #     low/none → rag_reuse_solution=False
    #
    # Routing will use `rag_confidence`.
    # -------------------------------------------------------------------------

    rag_selected_match = (
        decision.match
    )

    return {
        "rag_match_found": (
            decision.match is not None
        ),

        "rag_selected_match": (
            rag_selected_match
        ),

        "rag_similarity": (
            decision.similarity
        ),

        "rag_confidence": (
            decision.confidence
        ),

        "rag_reuse_solution": (
            decision.decision
            == RAGDecision.REUSE
        ),

        "current_task": (
            "RAG decision completed"
        ),

        "progress": 55,

        "error": None,
    }


# =============================================================================
# ROUTER
# =============================================================================


def route_after_rag(
    state: AIAnalysisState,
) -> Literal[
    "reuse_rag",
    "llm_required",
]:
    """
    Route the workflow after RAG decision.

    For now both REVIEW and LLM_REQUIRED go to the future
    LLM branch.

    The actual LLM branch will be implemented later.
    """

    if state.get(
        "rag_reuse_solution",
        False,
    ):

        return "reuse_rag"

    return "llm_required"


# =============================================================================
# NODE 7
# REUSE RAG SOLUTION
# =============================================================================


def reuse_rag_solution(
    state: AIAnalysisState,
) -> dict:
    """
    Build a final result using a trusted historical solution.

    This node does NOT call the LLM.
    """

    current_error = state.get(
        "current_error"
    )

    match = state.get(
        "rag_selected_match"
    )

    if not current_error:

        return {
            "error": (
                "Current error missing "
                "during RAG reuse."
            ),

            "status": "error",
        }

    if not match:

        return {
            "error": (
                "RAG reuse requested but "
                "no selected match exists."
            ),

            "status": "error",
        }

    result: AIAnalysisResult = {

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

        "severity": current_error.get(
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

        "source": "rag",

        "rag_match": True,

        "rag_knowledge_id": match.get(
            "knowledge_id"
        ),

        "rag_similarity": match.get(
            "similarity"
        ),

        "confidence": state.get(
            "rag_confidence",
            "high",
        ),

        "root_cause": match.get(
            "root_cause",
            "",
        ),

        "root_cause_evidence": [],

        "solution": match.get(
            "solution",
            "",
        ),

        "optimization": match.get(
            "optimization",
            "",
        ),

        "source_code_analysis": "",

        "source_file": "",

        "source_line_number": None,

        "test_result": match.get(
            "test_result",
            {},
        ),

        "jira_description": match.get(
            "jira_description",
            "",
        ),

        "evidence": match.get(
            "evidence",
            [],
        ),

        "status": "completed",

        "error": None,
    }

    final_results = list(
        state.get(
            "final_results",
            [],
        )
    )

    final_results.append(
        result
    )

    print("=" * 100)
    print("LANGGRAPH - RAG SOLUTION REUSED")
    print("=" * 100)

    print(
        f"Error ID     : "
        f"{result['error_id']}"
    )

    print(
        f"Knowledge ID : "
        f"{result['rag_knowledge_id']}"
    )

    print(
        f"Similarity   : "
        f"{result['rag_similarity']}"
    )

    return {
        "final_results": final_results,

        "current_task": (
            "Historical solution reused"
        ),

        "progress": 80,

        "error": None,
    }


# =============================================================================
# NODE 8
# LLM PLACEHOLDER
# =============================================================================


def llm_analysis_placeholder(
    state: AIAnalysisState,
) -> dict:
    """
    Temporary placeholder for the future LLM analysis branch.

    This node intentionally DOES NOT call an LLM.

    It allows us to test the complete RAG-aware workflow
    before implementing:

        - Web prompts
        - Telephony prompts
        - MySQL prompts
        - structured LLM output
        - source-code analysis
        - testing
        - Jira generation
    """

    current_error = state.get(
        "current_error"
    )

    if not current_error:

        return {
            "error": (
                "Current error missing "
                "during LLM placeholder."
            ),

            "status": "error",
        }

    rag_confidence = state.get(
        "rag_confidence",
        "none",
    )

    if rag_confidence == "medium":

        status = (
            "waiting_for_llm_validation"
        )

        task = (
            "Historical match found - "
            "LLM validation required"
        )

    else:

        status = (
            "waiting_for_llm_analysis"
        )

        task = (
            "No trusted historical solution - "
            "LLM analysis required"
        )

    result: AIAnalysisResult = {

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

        "severity": current_error.get(
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

        "source": "llm_pending",

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

        "confidence": rag_confidence,

        "root_cause": "",

        "root_cause_evidence": [],

        "solution": "",

        "optimization": "",

        "source_code_analysis": "",

        "source_file": "",

        "source_line_number": None,

        "test_result": {},

        "jira_description": "",

        "evidence": current_error.get(
            "lines",
            [],
        ),

        "status": status,

        "error": None,
    }

    final_results = list(
        state.get(
            "final_results",
            [],
        )
    )

    final_results.append(
        result
    )

    print("=" * 100)
    print("LANGGRAPH - LLM PLACEHOLDER")
    print("=" * 100)

    print(
        f"Error ID : "
        f"{current_error.get('error_id', '')}"
    )

    print(
        f"Status   : {status}"
    )

    return {
        "final_results": final_results,

        "current_task": task,

        "progress": 80,

        "error": None,
    }


# =============================================================================
# NODE 9
# NEXT ERROR
# =============================================================================


def move_to_next_error(
    state: AIAnalysisState,
) -> dict:
    """
    Move to the next selected error.
    """

    current_index = state.get(
        "current_error_index",
        0,
    )

    next_index = current_index + 1

    total_errors = len(
        state.get(
            "selected_errors",
            [],
        )
    )

    if total_errors > 0:

        progress = min(
            90,
            int(
                (
                    next_index
                    / total_errors
                )
                * 90
            ),
        )

    else:

        progress = 90

    print("=" * 100)
    print("LANGGRAPH - NEXT ERROR")
    print("=" * 100)

    print(
        f"Current Index : {current_index}"
    )

    print(
        f"Next Index    : {next_index}"
    )

    print(
        f"Total Errors  : {total_errors}"
    )

    return {
        "current_error_index": next_index,

        "current_error": None,

        "normalized_error": {},

        "error_signature": "",

        "embedding_text": "",

        "rag_query": "",

        "rag_matches": [],

        "rag_match_found": False,

        "rag_selected_match": None,

        "rag_similarity": None,

        "rag_confidence": "",

        "rag_reuse_solution": False,

        "current_task": (
            "Moving to next selected error"
        ),

        "progress": progress,

        "error": None,
    }


# =============================================================================
# FINALIZE
# =============================================================================


def finalize_analysis(
    state: AIAnalysisState,
) -> dict:
    """
    Finalize the workflow.
    """

    final_results = state.get(
        "final_results",
        [],
    )

    print("=" * 100)
    print("LANGGRAPH - FINALIZE ANALYSIS")
    print("=" * 100)

    print(
        f"Final Results : "
        f"{len(final_results)}"
    )

    return {
        "status": "completed",

        "current_task": (
            "AI analysis workflow completed"
        ),

        "progress": 100,

        "messages": [
            *state.get(
                "messages",
                [],
            ),
            "AI analysis workflow completed.",
        ],

        "error": None,
    }


# =============================================================================
# ROUTER - MORE ERRORS?
# =============================================================================


def route_after_result(
    state: AIAnalysisState,
) -> Literal[
    "next_error",
    "finalize",
]:
    """
    Determine whether another selected error needs processing.
    """

    current_index = state.get(
        "current_error_index",
        0,
    )

    selected_errors = state.get(
        "selected_errors",
        [],
    )

    if (
        current_index + 1
        < len(selected_errors)
    ):

        return "next_error"

    return "finalize"


# =============================================================================
# BUILD GRAPH
# =============================================================================


def build_ai_analysis_graph():

    graph = StateGraph(
        AIAnalysisState
    )

    # -------------------------------------------------------------------------
    # Nodes
    # -------------------------------------------------------------------------

    graph.add_node(
        "initialize_analysis",
        initialize_analysis,
    )

    graph.add_node(
        "prepare_current_error",
        prepare_current_error,
    )

    graph.add_node(
        "prepare_rag_query",
        prepare_rag_query,
    )

    graph.add_node(
        "generate_rag_embedding",
        generate_rag_embedding,
    )

    graph.add_node(
        "retrieve_rag_matches",
        retrieve_rag_matches,
    )

    graph.add_node(
        "decide_rag",
        decide_rag,
    )

    graph.add_node(
        "reuse_rag_solution",
        reuse_rag_solution,
    )

    graph.add_node(
        "llm_analysis_placeholder",
        llm_analysis_placeholder,
    )

    graph.add_node(
        "move_to_next_error",
        move_to_next_error,
    )

    graph.add_node(
        "finalize_analysis",
        finalize_analysis,
    )

    # -------------------------------------------------------------------------
    # START
    # -------------------------------------------------------------------------

    graph.add_edge(
        START,
        "initialize_analysis",
    )

    # -------------------------------------------------------------------------
    # Main pipeline
    # -------------------------------------------------------------------------

    graph.add_edge(
        "initialize_analysis",
        "prepare_current_error",
    )

    graph.add_edge(
        "prepare_current_error",
        "prepare_rag_query",
    )

    graph.add_edge(
        "prepare_rag_query",
        "generate_rag_embedding",
    )

    graph.add_edge(
        "generate_rag_embedding",
        "retrieve_rag_matches",
    )

    graph.add_edge(
        "retrieve_rag_matches",
        "decide_rag",
    )

    # -------------------------------------------------------------------------
    # RAG Decision
    # -------------------------------------------------------------------------

    graph.add_conditional_edges(
        "decide_rag",
        route_after_rag,
        {
            "reuse_rag": (
                "reuse_rag_solution"
            ),

            "llm_required": (
                "llm_analysis_placeholder"
            ),
        },
    )

    # -------------------------------------------------------------------------
    # Both branches eventually process the next error.
    # -------------------------------------------------------------------------

    graph.add_conditional_edges(
        "reuse_rag_solution",
        route_after_result,
        {
            "next_error": (
                "move_to_next_error"
            ),

            "finalize": (
                "finalize_analysis"
            ),
        },
    )

    graph.add_conditional_edges(
        "llm_analysis_placeholder",
        route_after_result,
        {
            "next_error": (
                "move_to_next_error"
            ),

            "finalize": (
                "finalize_analysis"
            ),
        },
    )

    # -------------------------------------------------------------------------
    # Loop
    # -------------------------------------------------------------------------

    graph.add_edge(
        "move_to_next_error",
        "prepare_current_error",
    )

    # -------------------------------------------------------------------------
    # END
    # -------------------------------------------------------------------------

    graph.add_edge(
        "finalize_analysis",
        END,
    )

    return graph.compile()


# =============================================================================
# COMPILED GRAPH
# =============================================================================


ai_analysis_graph = build_ai_analysis_graph()