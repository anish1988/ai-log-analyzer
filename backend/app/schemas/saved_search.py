"""
Phase 4 - Saved Search API schemas.

These schemas are used only for explicitly saved searches.

A normal search request does not use these schemas.
"""

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SavedSearchTier = Literal[
    "all",
    "web",
    "db",
    "telephony",
]


class SavedSearchCreateRequest(BaseModel):
    """
    Request used when a user explicitly clicks "Save Search".
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    from_: date = Field(
        alias="from",
    )

    to: date

    tier: SavedSearchTier

    servers: list[str] = Field(
        default_factory=list,
    )

    search_filters: dict = Field(
        default_factory=dict,
        alias="searchFilters",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Saved search name is required."
            )

        return value

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("servers")
    @classmethod
    def validate_servers(
        cls,
        value: list[str],
    ) -> list[str]:

        return [
            server.strip()
            for server in value
            if server.strip()
        ]

    @field_validator("to")
    @classmethod
    def validate_date_range(
        cls,
        value: date,
        info,
    ) -> date:

        from_date = info.data.get("from_")

        if (
            from_date is not None
            and value < from_date
        ):
            raise ValueError(
                "End date cannot be before start date."
            )

        return value


class SavedSearchUpdateRequest(BaseModel):
    """
    Request used when a user edits an existing saved search.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    from_: date = Field(
        alias="from",
    )

    to: date

    tier: SavedSearchTier

    servers: list[str] = Field(
        default_factory=list,
    )

    search_filters: dict = Field(
        default_factory=dict,
        alias="searchFilters",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Saved search name is required."
            )

        return value

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("servers")
    @classmethod
    def validate_servers(
        cls,
        value: list[str],
    ) -> list[str]:

        return [
            server.strip()
            for server in value
            if server.strip()
        ]

    @field_validator("to")
    @classmethod
    def validate_date_range(
        cls,
        value: date,
        info,
    ) -> date:

        from_date = info.data.get("from_")

        if (
            from_date is not None
            and value < from_date
        ):
            raise ValueError(
                "End date cannot be before start date."
            )

        return value


class SavedSearchResponse(BaseModel):
    """
    Saved search returned by the API.
    """

    id: int

    user_id: str

    name: str

    description: str | None

    from_: date = Field(
        alias="from",
    )

    to: date

    tier: SavedSearchTier

    servers: list[str]

    search_filters: dict = Field(
        alias="searchFilters",
    )

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class SavedSearchListResponse(BaseModel):
    """
    Response containing the current user's saved searches.
    """

    items: list[SavedSearchResponse]

    total: int