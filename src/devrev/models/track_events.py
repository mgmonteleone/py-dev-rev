"""Track events models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class TrackEvent(DevRevBaseModel):
    """Event tracking model.
    
    Attributes:
        name: Event name
        properties: Optional event properties
        timestamp: Optional event timestamp
        user_id: Optional user ID associated with the event
    """
    
    name: str
    properties: dict | None = None
    timestamp: datetime | None = None
    user_id: str | None = None


class TrackEventsPublishRequest(DevRevBaseModel):
    """Request to publish tracking events.
    
    Attributes:
        events: List of events to publish
    """
    
    events: list[TrackEvent]


class TrackEventsPublishResponse(DevRevResponseModel):
    """Response from publishing tracking events.
    
    Attributes:
        success: Whether the events were published successfully
        count: Number of events published
    """
    
    success: bool
    count: int | None = None

