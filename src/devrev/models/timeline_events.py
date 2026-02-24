"""Timeline event models for DevRev SDK.

This module contains Pydantic models for Timeline Change Events,
which track changes and activities on DevRev objects over time.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class TimelineEventType(StrEnum):
    """Timeline event type enumeration."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    STAGE_CHANGED = "stage_changed"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"
    COMMENT_ADDED = "comment_added"
    ATTACHMENT_ADDED = "attachment_added"
    TAG_ADDED = "tag_added"
    TAG_REMOVED = "tag_removed"
    LINKED = "linked"
    UNLINKED = "unlinked"
    PRIORITY_CHANGED = "priority_changed"
    DUE_DATE_CHANGED = "due_date_changed"
    CUSTOM = "custom"


class FieldChange(DevRevResponseModel):
    """Represents a single field change in a timeline event.

    Inherits from DevRevResponseModel for forward-compatibility with
    additional API fields.

    Attributes:
        field_name: Name of the changed field
        old_value: Previous value
        new_value: New value
    """

    field_name: str = Field(..., description="Name of the changed field")
    old_value: Any | None = Field(default=None, description="Previous value")
    new_value: Any | None = Field(default=None, description="New value")


class TimelineChangeEvent(DevRevResponseModel):
    """Timeline change event model.

    Represents a change or activity that occurred on a DevRev object,
    recorded in the object's timeline for audit and tracking purposes.

    Attributes:
        id: Unique event identifier
        object_id: ID of the object this event relates to
        object_type: Type of the object
        event_type: Type of the event
        actor_id: User who triggered the event
        timestamp: When the event occurred
        changes: List of field changes
        message: Human-readable event message
        metadata: Additional event metadata
    """

    id: str = Field(..., description="Unique event identifier")
    object_id: str = Field(..., description="ID of the related object")
    object_type: str = Field(..., description="Type of the related object")
    event_type: TimelineEventType = Field(..., description="Type of event")
    actor_id: str | None = Field(default=None, description="User who triggered event")
    timestamp: datetime = Field(..., description="When the event occurred")
    changes: list[FieldChange] | None = Field(default=None, description="List of field changes")
    message: str | None = Field(default=None, description="Human-readable message")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata")


# Request/Response models


class TimelineEventsGetRequest(DevRevBaseModel):
    """Request to get a timeline event by ID."""

    id: str = Field(..., description="Event ID")


class TimelineEventsGetResponse(DevRevResponseModel):
    """Response from getting a timeline event."""

    event: TimelineChangeEvent = Field(..., description="The timeline event")


class TimelineEventsListRequest(DevRevBaseModel):
    """Request to list timeline events for an object."""

    object_id: str = Field(..., description="Object ID to get events for")
    event_types: list[TimelineEventType] | None = Field(
        default=None, description="Filter by event types"
    )
    actor_id: str | None = Field(default=None, description="Filter by actor")
    since: datetime | None = Field(default=None, description="Events after this time")
    until: datetime | None = Field(default=None, description="Events before this time")
    limit: int | None = Field(default=None, description="Maximum results")
    cursor: str | None = Field(default=None, description="Pagination cursor")


class TimelineEventsListResponse(DevRevResponseModel):
    """Response from listing timeline events."""

    events: list[TimelineChangeEvent] = Field(..., description="List of events")
    next_cursor: str | None = Field(default=None, description="Next pagination cursor")
