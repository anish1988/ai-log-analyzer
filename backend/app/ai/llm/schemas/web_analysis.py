"""
Structured response schema for Web/Laravel AI analysis.
"""

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    line_number: int | None = None

    content: str

    explanation: str


class SourceCodeLocation(BaseModel):
    found: bool = False

    file_path: str | None = None

    line_number: int | None = None

    symbol: str | None = None

    explanation: str


class TestResult(BaseModel):
    test_case: str

    expected_result: str

    verification_steps: list[str] = Field(
        default_factory=list
    )


class WebAIAnalysisResponse(BaseModel):
    """
    Final structured response expected from the
    Web/Laravel analysis model.
    """

    analysis_status: str

    error_summary: str

    root_cause: str

    root_cause_evidence: list[EvidenceItem] = Field(
        default_factory=list
    )

    solution: str

    optimization: str

    source_code_analysis: str

    source_code_location: SourceCodeLocation

    test_result: TestResult

    jira_description: str

    confidence: str

    missing_information: list[str] = Field(
        default_factory=list
    )