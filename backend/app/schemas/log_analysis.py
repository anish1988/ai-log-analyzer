"""Pydantic request/response contracts for the /api/logs/* endpoints."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

TierSelection = Literal["all", "web", "db", "telephony"]


class SearchFiltersRequest(BaseModel):
    from_: str = Field(alias="from")
    to: str
    tier: TierSelection
    servers: list[str]
    lead_id: str = Field(default="", alias="leadId")
    campaign_id: str = Field(default="", alias="campaignId")
    unique_id: str = Field(default="", alias="uniqueId")
    caller_id: str = Field(default="", alias="callerId")
    caller_number: str = Field(default="", alias="callerNumber")
    agent: str = ""
    inbound_group: str = Field(default="", alias="inboundGroup")
    log_type: str | None = Field(default=None, alias="logType")
    default_path: str | None = Field(default=None, alias="defaultLogPath")
    custom_path: str | None = Field(default=None, alias="customLogPath")

    model_config = {"populate_by_name": True}


class PermissionCheckRequest(BaseModel):
    tier: TierSelection
    servers: list[str]


class PermissionCheckResponse(BaseModel):
    granted: bool
    message: Optional[str] = None


class LogLineSchema(BaseModel):
    server: str
    file: str
    file_id: str
    line_number: int
    raw: str
    matched_filters: list[str]


class LogFileResultSchema(BaseModel):
    file_id: str
    file_label: str
    server: str
    searched_file: str
    meta: dict[str, str]
    matched_count: int
    lines: list[LogLineSchema]


class LogFetchResponse(BaseModel):
    total_lines: int
    results: list[LogFileResultSchema]

# =============================================================================
# WEB LOG ANALYZER SCHEMA
# =============================================================================

class WebLogLineSchema(BaseModel):
    """
    Represents one physical line inside a log file.
    """

    line_number: int
    raw: str


class WebErrorBlockSchema(BaseModel):
    """
    One complete error block.

    Example:
        PHP Fatal Error
        Stack Trace...
        Stack Trace...
        Stack Trace...
    """

    error_id: str

    title: str

    severity: str

    start_line: int

    end_line: int

    total_lines: int

    timestamp: str | None = None

    lines: list[WebLogLineSchema]


class WebLogFileSchema(BaseModel):
    """
    Represents one analyzed log file.
    """

    server: str

    log_type: str

    file_name: str

    file_path: str

    total_lines: int

    total_errors: int

    errors: list[WebErrorBlockSchema]


class WebLogFetchResponse(BaseModel):
    """
    Response returned by the Web Log Analyzer.
    """

    success: bool

    message: str

    results: list[WebLogFileSchema]