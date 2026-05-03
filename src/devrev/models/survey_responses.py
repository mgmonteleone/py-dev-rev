"""Survey response models for DevRev SDK.

This module contains Pydantic models for the ``surveys.responses.list`` API.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import ConfigDict, Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class SurveyResponsesListMode(StrEnum):
    """Survey response cursor iteration mode."""

    AFTER = "after"
    BEFORE = "before"


class SurveyResponse(DevRevResponseModel):
    """DevRev survey response model."""

    model_config = ConfigDict(extra="allow", populate_by_name=True, str_strip_whitespace=True)

    id: str = Field(..., description="Survey response ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    created_by: dict[str, Any] | None = Field(default=None, description="Creator user summary")
    created_date: datetime | None = Field(default=None, description="Creation timestamp")
    modified_by: dict[str, Any] | None = Field(default=None, description="Modifier user summary")
    modified_date: datetime | None = Field(default=None, description="Last modification timestamp")
    object_version: int | None = Field(default=None, description="Object version")
    dispatch_id: str | None = Field(default=None, description="Dispatched survey ID")
    dispatched_channels: list[dict[str, Any]] | None = Field(
        default=None,
        description="Channels on which the survey was dispatched",
    )
    object: str | None = Field(default=None, description="Object for which the survey was taken")
    recipient: dict[str, Any] | str | None = Field(default=None, description="Survey recipient")
    response: dict[str, Any] | str | int | float | bool | None = Field(
        default=None,
        description="Survey response payload",
    )
    stage: dict[str, Any] | int | str | None = Field(default=None, description="Survey stage")
    survey: dict[str, Any] | str | None = Field(default=None, description="Survey summary or ID")


class SurveyResponsesListRequest(DevRevBaseModel):
    """Request to list survey responses."""

    created_by: list[str] | None = Field(default=None, description="Creator user filters")
    cursor: str | None = Field(default=None, description="Pagination cursor")
    dispatch_ids: list[str] | None = Field(default=None, description="Survey dispatch IDs")
    limit: int | None = Field(default=None, ge=1, le=100, description="Maximum results")
    mode: SurveyResponsesListMode | None = Field(default=None, description="Cursor iteration mode")
    object_id: str | None = Field(
        default=None,
        alias="object",
        description="Single object ID to filter responses by",
    )
    objects: list[str] | None = Field(default=None, description="Object IDs to filter responses by")
    recipient: list[str] | None = Field(default=None, description="Recipient user filters")
    sort_by: list[str] | None = Field(default=None, description="Sort order entries")
    stages: list[int] | None = Field(default=None, description="Survey response stage filters")
    surveys: list[str] | None = Field(default=None, description="Survey IDs to filter by")


class SurveyResponsesListResponse(PaginatedResponse):
    """Response from listing survey responses."""

    survey_responses: list[SurveyResponse] = Field(
        default_factory=list,
        description="List of survey responses",
    )
