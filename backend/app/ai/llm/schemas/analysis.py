from typing import Any

from pydantic import BaseModel, Field


class TelephonyAIAnalysisResponse(BaseModel):
    """
    Structured AI response for Telephony logs.

    Supports:
        - Asterisk
        - VICIdial
        - SIP
        - AGI
        - AMI
        - Dialer
        - Call routing
        - Recording
        - Voicemail
        - Queue / IVR
        - Telephony database issues
    """

    analysis_status: str = Field(
        description=(
            "Analysis status. "
            "Normally completed or failed."
        )
    )

    error_summary: str = Field(
        description=(
            "Concise summary of the telephony error."
        )
    )

    component: str = Field(
        description=(
            "Primary telephony component involved. "
            "Examples: Asterisk, VICIdial, SIP, AGI, "
            "AMI, Dialer, Queue, IVR, Recording, "
            "Voicemail, Database, Carrier/Trunk."
        )
    )

    error_category: str = Field(
        description=(
            "Classification of the error."
        )
    )

    root_cause: str = Field(
        description=(
            "Most likely root cause based strictly "
            "on the supplied evidence."
        )
    )

    root_cause_evidence: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Important log lines supporting the root cause."
        )
    )

    contributing_factors: list[str] = Field(
        default_factory=list,
        description=(
            "Possible contributing factors supported "
            "by the evidence."
        )
    )

    solution: str = Field(
        description=(
            "Recommended corrective solution."
        )
    )

    optimization: str = Field(
        description=(
            "Recommended preventive/optimization actions."
        )
    )

    source_code_analysis: str = Field(
        description=(
            "Source-code analysis if the supplied evidence "
            "supports it. Otherwise explicitly state that "
            "source-code verification is required."
        )
    )

    source_file: str | None = Field(
        default=None,
        description=(
            "Source file implicated by the evidence, "
            "if confidently identifiable."
        )
    )

    source_line_number: int | None = Field(
        default=None,
        description=(
            "Source-code line number only when directly "
            "supported by evidence."
        )
    )

    test_result: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Recommended validation/test procedure and "
            "expected result."
        )
    )

    jira_description: str = Field(
        description=(
            "Production-ready Jira issue description."
        )
    )

    confidence: str = Field(
        description=(
            "Confidence level: high, medium, or low."
        )
    )

    evidence: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            "Important evidence extracted from the "
            "telephony log."
        )
    )