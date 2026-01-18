"""Engagement models for DevRev SDK.

This module contains Pydantic models for Engagement-related API operations.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class EngagementType(str, Enum):
    """Engagement type enumeration."""

    CALL = "call"
    CONVERSATION = "conversation"
    CUSTOM = "custom"
    DEFAULT = "default"
    EMAIL = "email"
    LINKED_IN = "linked_in"
    MEETING = "meeting"
    OFFLINE = "offline"
    SURVEY = "survey"


class Engagement(DevRevResponseModel):
    """DevRev Engagement model.

    Represents an engagement in DevRev.
    """

    id: str = Field(..., description="Engagement ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    title: str | None = Field(default=None, description="Engagement title")
    engagement_type: EngagementType | None = Field(default=None, description="Type of engagement")
    description: str | None = Field(default=None, description="Engagement description")
    members: list[str] | None = Field(default=None, description="Member user IDs")
    parent: str | None = Field(default=None, description="Parent engagement ID")
    scheduled_date: datetime | None = Field(default=None, description="Scheduled date/time")
    tags: list[str] | None = Field(default=None, description="Tag IDs")
    created_date: datetime | None = Field(
        default=None, alias="created_at", description="Creation timestamp"
    )
    modified_date: datetime | None = Field(
        default=None, alias="modified_at", description="Last modification timestamp"
    )


# Request Models


class EngagementsCreateRequest(DevRevBaseModel):
    """Request to create an engagement."""

    title: str = Field(..., description="Engagement title", min_length=1, max_length=256)
    engagement_type: EngagementType = Field(..., description="Type of engagement")
    description: str | None = Field(
        default=None, description="Engagement description", max_length=65536
    )
    members: list[str] | None = Field(default=None, description="Member user IDs")
    parent: str | None = Field(default=None, description="Parent engagement ID")
    scheduled_date: datetime | None = Field(default=None, description="Scheduled date/time")
    tags: list[str] | None = Field(default=None, description="Tag IDs")


class EngagementsGetRequest(DevRevBaseModel):
    """Request to get an engagement by ID."""

    id: str = Field(..., description="Engagement ID")


class EngagementsListRequest(DevRevBaseModel):
    """Request to list engagements."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results to return")
    engagement_type: list[EngagementType] | None = Field(
        default=None, description="Filter by engagement types"
    )
    members: list[str] | None = Field(default=None, description="Filter by member user IDs")
    parent: str | None = Field(default=None, description="Filter by parent engagement ID")


class EngagementsUpdateRequest(DevRevBaseModel):
    """Request to update an engagement."""

    id: str = Field(..., description="Engagement ID")
    title: str | None = Field(default=None, description="New title")
    description: str | None = Field(default=None, description="New description")
    engagement_type: EngagementType | None = Field(default=None, description="New engagement type")
    scheduled_date: datetime | None = Field(default=None, description="New scheduled date/time")


class EngagementsDeleteRequest(DevRevBaseModel):
    """Request to delete an engagement."""

    id: str = Field(..., description="Engagement ID to delete")


class EngagementsCountRequest(DevRevBaseModel):
    """Request to count engagements."""

    engagement_type: list[EngagementType] | None = Field(
        default=None, description="Filter by engagement types"
    )
    members: list[str] | None = Field(default=None, description="Filter by member user IDs")


# Response Models


class EngagementsCreateResponse(DevRevResponseModel):
    """Response from creating an engagement."""

    engagement: Engagement = Field(..., description="Created engagement")


class EngagementsGetResponse(DevRevResponseModel):
    """Response from getting an engagement."""

    engagement: Engagement = Field(..., description="Retrieved engagement")


class EngagementsListResponse(PaginatedResponse):
    """Response from listing engagements."""

    engagements: list[Engagement] = Field(..., description="List of engagements")


class EngagementsUpdateResponse(DevRevResponseModel):
    """Response from updating an engagement."""

    engagement: Engagement = Field(..., description="Updated engagement")


class EngagementsDeleteResponse(DevRevResponseModel):
    """Response from deleting an engagement."""

    pass  # Empty response body


class EngagementsCountResponse(DevRevResponseModel):
    """Response from counting engagements."""

    count: int = Field(..., description="Total count of engagements")
