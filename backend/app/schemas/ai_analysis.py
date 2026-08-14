"""
FastAPI schemas for AI log analysis.

These schemas define the public API contract for
starting and receiving AI analysis requests.

The API schemas are intentionally separate from
the internal LangGraph state.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# SELECTED ERROR REQUEST
# =============================================================================


class AISelectedErrorRequest(BaseModel):
    """
    One error selected by the user for AI analysis.
    """

    error_id: str = Field(
        min_length=1,
        description="Unique identifier of the selected error.",
    )

    tier: str = Field(
        min_length=1,
        description="Analysis tier.",
    )

    log_type: str = Field(
        min_length=1,
        description="Log type.",
    )

    server: str = Field(
        default="",
        description="Server associated with the error.",
    )

    file_name: str = Field(
        default="",
        description="Log file name.",
    )

    file_path: str = Field(
        default="",
        description="Full or resolved log file path.",
    )

    title: str = Field(
        default="",
        description="Short error title.",
    )

    severity: str = Field(
        default="",
        description="Error severity.",
    )

    timestamp: str = Field(
        default="",
        description="Error timestamp.",
    )

    start_line: int | None = Field(
        default=None,
        description="First log line belonging to the error.",
    )

    end_line: int | None = Field(
        default=None,
        description="Last log line belonging to the error.",
    )

    total_lines: int | None = Field(
        default=None,
        ge=0,
        description="Total number of error lines.",
    )

    error_content: str = Field(
        default="",
        description="Complete or summarized error content.",
    )

    lines: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Structured log lines.",
    )


# =============================================================================
# AI ANALYSIS REQUEST
# =============================================================================


class AIAnalysisRequest(BaseModel):
    """
    Request to start AI analysis.
    """

    request_id: str | None = Field(
        default=None,
        description="Optional client-generated request ID.",
    )

    selected_errors: list[AISelectedErrorRequest] = Field(
        min_length=1,
        description="Errors selected for AI analysis.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional request metadata.",
    )

    @field_validator("request_id")
    @classmethod
    def validate_request_id(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value


# =============================================================================
# AI ANALYSIS RESULT
# =============================================================================


class AIAnalysisResultResponse(BaseModel):
    """
    Public API representation of one AI analysis result.
    """

    error_id: str = ""

    tier: str = ""

    log_type: str = ""

    server: str = ""

    file_name: str = ""

    title: str = ""

    severity: str = ""

    timestamp: str = ""

    start_line: int | None = None

    end_line: int | None = None

    # -------------------------------------------------------------------------
    # ANALYSIS SOURCE
    # -------------------------------------------------------------------------

    source: Literal[
        "rag",
        "llm",
        "llm_pending",
        "unknown",
    ] = "unknown"

    # -------------------------------------------------------------------------
    # RAG
    # -------------------------------------------------------------------------

    rag_match: bool = False

    rag_knowledge_id: int | None = None

    rag_similarity: float | None = None

    confidence: str = ""

    # -------------------------------------------------------------------------
    # AI ANALYSIS
    # -------------------------------------------------------------------------

    error_summary: str = ""

    root_cause: str = ""

    root_cause_evidence: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    solution: str = ""

    optimization: str = ""

    source_code_analysis: str = ""

    source_file: str | None = None

    source_line_number: int | None = None

    # -------------------------------------------------------------------------
    # TEST RESULT
    # -------------------------------------------------------------------------

    test_result: dict[str, Any] = Field(
        default_factory=dict,
    )

    # -------------------------------------------------------------------------
    # JIRA
    # -------------------------------------------------------------------------

    jira_description: str = ""

    # -------------------------------------------------------------------------
    # EVIDENCE
    # -------------------------------------------------------------------------

    evidence: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    # -------------------------------------------------------------------------
    # STATUS
    # -------------------------------------------------------------------------

    status: str = ""

    error: str | None = None


# =============================================================================
# PROGRESS EVENT
# =============================================================================


class AIProgressEventResponse(BaseModel):
    """
    One progress event generated by the AI workflow.
    """

    task_id: str = ""

    status: str = ""

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    message: str = ""

    timestamp: str | None = None



class AIKnowledgeVerificationRequest(BaseModel):
    verified: bool = True

    resolution_status: Literal[
        "verified",
        "resolved",
        "rejected",
    ]

    verification_notes: str = ""

# =============================================================================
# AI ANALYSIS RESPONSE
# =============================================================================


class AIAnalysisResponse(BaseModel):
    """
    Final response returned by the AI analysis API.
    """

    request_id: str

    status: Literal[
        "processing",
        "completed",
        "error",
    ]

    current_task: str = ""

    progress: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    total_errors: int = 0

    completed_errors: int = 0

    final_results: list[
        AIAnalysisResultResponse
    ] = Field(
        default_factory=list,
    )

    progress_events: list[
        AIProgressEventResponse
    ] = Field(
        default_factory=list,
    )

    messages: list[str] = Field(
        default_factory=list,
    )

    error: str | None = None