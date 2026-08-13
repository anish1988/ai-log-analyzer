"""
LangGraph AI Analysis State.

This state is shared by all nodes in the AI analysis workflow.

The workflow is intentionally designed to support:

    Error Selection
        ↓
    Validation
        ↓
    Normalization
        ↓
    RAG Retrieval
        ↓
    RAG Decision
        ↓
    Existing Solution OR LLM Analysis
        ↓
    Root Cause
        ↓
    Optimization
        ↓
    Source Analysis
        ↓
    Test Result
        ↓
    Jira Description
        ↓
    Final Result
"""

from typing import Any, TypedDict
from app.ai.progress.events import ProgressEvent

# =============================================================================
# SELECTED ERROR
# =============================================================================


class SelectedError(TypedDict, total=False):
    """
    One error selected by the user from Step 2.

    The structure is intentionally generic so it can support:

        - Web
        - Telephony
        - MySQL
        - Future log types
    """

    error_id: str

    tier: str

    log_type: str

    server: str

    file_name: str

    file_path: str

    title: str

    severity: str

    timestamp: str

    start_line: int

    end_line: int

    total_lines: int

    error_content: str

    lines: list[dict[str, Any]]


# =============================================================================
# RAG MATCH
# =============================================================================


class RAGMatch(TypedDict, total=False):
    """
    One candidate returned by the RAG search.
    """

    knowledge_id: int

    similarity: float

    tier: str

    log_type: str

    error_signature: str

    title: str

    root_cause: str

    solution: str

    optimization: str

    test_result: dict[str, Any]

    jira_description: str

    resolution_status: str

    verified: bool

    evidence: list[dict[str, Any]]

    metadata: dict[str, Any]


# =============================================================================
# ANALYSIS RESULT
# =============================================================================


class AIAnalysisResult(TypedDict, total=False):
    """
    Final analysis result for one selected error.
    """

    error_id: str

    tier: str

    log_type: str

    server: str

    file_name: str

    title: str

    severity: str

    timestamp: str

    start_line: int

    end_line: int

    source: str

    rag_match: bool

    rag_knowledge_id: int | None

    rag_similarity: float | None

    confidence: str

    root_cause: str

    root_cause_evidence: list[dict[str, Any]]

    solution: str

    optimization: str

    source_code_analysis: str

    source_file: str

    source_line_number: int | None

    test_result: dict[str, Any]

    jira_description: str

    evidence: list[dict[str, Any]]

    status: str

    error: str | None


# =============================================================================
# LANGGRAPH STATE
# =============================================================================


class AIAnalysisState(TypedDict, total=False):
    """
    Complete state shared by the LangGraph AI analysis workflow.

    This state is designed for multiple selected errors.

    Example:

        selected_errors = [
            error_1,
            error_2,
            error_3,
        ]

    Each error can independently go through:

        RAG → reuse

    or:

        RAG → no match → LLM analysis

    The individual results are eventually aggregated into
    final_results.
    """

    # =========================================================================
    # REQUEST INFORMATION
    # =========================================================================

    request_id: str

    tier: str

    log_type: str

    selected_errors: list[SelectedError]


    # =========================================================================
    # CURRENT ERROR PROCESSING
    # =========================================================================

    current_error_index: int

    current_error: SelectedError | None


    # =========================================================================
    # NORMALIZED ERROR
    # =========================================================================

    normalized_error: dict[str, Any]

    error_signature: str

    embedding_text: str


    # =========================================================================
    # RAG
    # =========================================================================

    rag_query: str

    rag_matches: list[RAGMatch]

    rag_match_found: bool

    rag_selected_match: RAGMatch | None

    rag_similarity: float | None

    rag_confidence: str

    rag_reuse_solution: bool
    rag_decision: str
    rag_result: dict[str, Any] | None


    # =========================================================================
    # AI ANALYSIS
    # =========================================================================

    root_cause: str

    root_cause_evidence: list[dict[str, Any]]

    solution: str

    optimization: str

    current_ai_result: AIAnalysisResult | None


    # =========================================================================
    # SOURCE CODE ANALYSIS
    # =========================================================================

    source_code_analysis: str

    source_file: str

    source_line_number: int | None


    # =========================================================================
    # TEST RESULT
    # =========================================================================

    test_result: dict[str, Any]


    # =========================================================================
    # JIRA
    # =========================================================================

    jira_description: str


    # =========================================================================
    # FINAL RESULTS
    # =========================================================================

    final_results: list[AIAnalysisResult]


    # =========================================================================
    # WORKFLOW STATUS
    # =========================================================================

    status: str

    current_task: str

    progress: int

    messages: list[str]

    error: str | None


    # =========================================================================
    # PROGRESS EVENTS
    # =========================================================================

    progress_event: ProgressEvent | None

    progress_events: list[ProgressEvent]

