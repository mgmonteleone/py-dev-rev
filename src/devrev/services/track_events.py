"""Track events service for DevRev SDK."""

from __future__ import annotations

from devrev.models.track_events import (
    TrackEvent,
    TrackEventsPublishRequest,
    TrackEventsPublishResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class TrackEventsService(BaseService):
    """Service for publishing tracking events.

    Provides methods to publish analytics and tracking events.
    """

    def publish(self, events: list[TrackEvent]) -> TrackEventsPublishResponse:
        """Publish tracking events.

        Args:
            events: List of events to publish

        Returns:
            Response indicating success and event count
        """
        request = TrackEventsPublishRequest(events=events)
        return self._post("/track-events.publish", request, TrackEventsPublishResponse)


class AsyncTrackEventsService(AsyncBaseService):
    """Async service for publishing tracking events.

    Provides async methods to publish analytics and tracking events.
    """

    async def publish(self, events: list[TrackEvent]) -> TrackEventsPublishResponse:
        """Publish tracking events.

        Args:
            events: List of events to publish

        Returns:
            Response indicating success and event count
        """
        request = TrackEventsPublishRequest(events=events)
        return await self._post("/track-events.publish", request, TrackEventsPublishResponse)
