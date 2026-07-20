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
    meta: dict[str, str]
    lines: list[LogLineSchema]


class LogFetchResponse(BaseModel):
    total_lines: int
    results: list[LogFileResultSchema]