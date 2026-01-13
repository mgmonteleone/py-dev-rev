"""Timeline Entry models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import (
    DevRevBaseModel,
    DevRevResponseModel,
    PaginatedResponse,
    UserSummary,
)


class TimelineEntryType(str, Enum):
    """Timeline entry type enumeration."""

    COMMENT = "timeline_comment"
    NOTE = "timeline_note"
    EVENT = "timeline_event"


class TimelineEntry(DevRevResponseModel):
    """DevRev Timeline Entry model."""

    id: str = Field(..., description="Timeline entry ID")
    type: TimelineEntryType | None = Field(default=None, description="Entry type")
    body: str | None = Field(default=None, description="Entry content")
    object_id: str | None = Field(default=None, description="Parent object ID")
    created_by: UserSummary | None = Field(default=None, description="Creator")
    created_date: datetime | None = Field(default=None, description="Creation date")
    modified_date: datetime | None = Field(default=None, description="Last modified")


class TimelineEntriesCreateRequest(DevRevBaseModel):
    """Request to create a timeline entry."""

    object: str = Field(..., description="Parent object ID")
    type: TimelineEntryType = Field(..., description="Entry type")
    body: str | None = Field(default=None, description="Entry content")


class TimelineEntriesGetRequest(DevRevBaseModel):
    """Request to get a timeline entry by ID."""

    id: str = Field(..., description="Timeline entry ID")


class TimelineEntriesDeleteRequest(DevRevBaseModel):
    """Request to delete a timeline entry."""

    id: str = Field(..., description="Timeline entry ID to delete")


class TimelineEntriesListRequest(DevRevBaseModel):
    """Request to list timeline entries."""

    object: str = Field(..., description="Parent object ID")
    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, ge=1, le=100, description="Max results")


class TimelineEntriesUpdateRequest(DevRevBaseModel):
    """Request to update a timeline entry."""

    id: str = Field(..., description="Timeline entry ID")
    body: str | None = Field(default=None, description="New content")


class TimelineEntriesCreateResponse(DevRevResponseModel):
    """Response from creating a timeline entry."""

    timeline_entry: TimelineEntry = Field(..., description="Created entry")


class TimelineEntriesGetResponse(DevRevResponseModel):
    """Response from getting a timeline entry."""

    timeline_entry: TimelineEntry = Field(..., description="Retrieved entry")


class TimelineEntriesListResponse(PaginatedResponse):
    """Response from listing timeline entries."""

    timeline_entries: list[TimelineEntry] = Field(..., description="List of entries")


class TimelineEntriesUpdateResponse(DevRevResponseModel):
    """Response from updating a timeline entry."""

    timeline_entry: TimelineEntry = Field(..., description="Updated entry")


class TimelineEntriesDeleteResponse(DevRevResponseModel):
    """Response from deleting a timeline entry."""

    pass

