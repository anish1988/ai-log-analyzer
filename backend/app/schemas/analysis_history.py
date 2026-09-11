from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnalysisRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: str | None = None
    user_id: UUID
    source_type: Literal["manual", "automation"]
    status: Literal["processing", "completed", "failed", "error"]

    started_at: datetime | None = None
    completed_at: datetime | None = None

    total_errors: int = Field(default=0, ge=0)
    completed_errors: int = Field(default=0, ge=0)
    failed_errors: int = Field(default=0, ge=0)

    log_type: str | None = None
    servers: list[Any] = Field(default_factory=list)
    log_files: list[Any] = Field(default_factory=list)

    custom_prompt: str | None = None
    automation_run_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None

    created_at: datetime
    updated_at: datetime


class AnalysisRunListResponse(BaseModel):
    items: list[AnalysisRunResponse]
    total: int


class AnalysisResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    analysis_run_id: UUID

    error_id: str
    error_signature: str | None = None

    tier: str | None = None
    log_type: str | None = None
    server: str | None = None
    file_name: str | None = None
    file_path: str | None = None
    title: str | None = None
    severity: str | None = None

    timestamp: datetime | None = None
    start_line: int | None = None
    end_line: int | None = None

    source: str | None = None

    rag_match: bool = False
    rag_knowledge_id: int | None = None
    rag_similarity: float | None = None

    confidence: str | None = None
    analysis_status: str | None = None

    error_summary: str | None = None
    root_cause: str | None = None
    solution: str | None = None
    optimization: str | None = None

    source_code_analysis: str | None = None
    source_file: str | None = None
    source_line_number: int | None = None

    jira_description: str | None = None
    jira_issue_key: str | None = None
    jira_issue_id: str | None = None
    jira_issue_url: str | None = None
    jira_status: str | None = None

    root_cause_evidence: list[Any] = Field(default_factory=list)
    test_result: dict[str, Any] = Field(default_factory=dict)
    evidence: list[Any] = Field(default_factory=list)
    source_code_location: dict[str, Any] = Field(default_factory=dict)
    missing_information: list[Any] = Field(default_factory=list)

    request_payload: dict[str, Any] = Field(default_factory=dict)
    response_payload: dict[str, Any] = Field(default_factory=dict)
    jira_payload: dict[str, Any] | None = None

    created_at: datetime
    updated_at: datetime


class AnalysisRunDetailResponse(BaseModel):
    run: AnalysisRunResponse
    results: list[AnalysisResultResponse]