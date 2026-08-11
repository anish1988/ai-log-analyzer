"""
Schemas for AI analysis requests and responses.
"""

from typing import Any

from pydantic import BaseModel, Field


class AIAnalysisRequest(BaseModel):

    tier: str

    errors: list[dict[str, Any]] = Field(
        min_length=1
    )


class AIAnalysisResponse(BaseModel):

    success: bool

    total_errors: int

    results: list[dict[str, Any]]