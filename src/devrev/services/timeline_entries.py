"""Timeline Entries service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.timeline_entries import (
    TimelineEntriesCreateRequest,
    TimelineEntriesCreateResponse,
    TimelineEntriesDeleteRequest,
    TimelineEntriesDeleteResponse,
    TimelineEntriesGetRequest,
    TimelineEntriesGetResponse,
    TimelineEntriesListRequest,
    TimelineEntriesListResponse,
    TimelineEntriesUpdateRequest,
    TimelineEntriesUpdateResponse,
    TimelineEntry,
)
from devrev.services.base import AsyncBaseService, BaseService


class TimelineEntriesService(BaseService):
    """Service for managing DevRev Timeline Entries."""

    def create(self, request: TimelineEntriesCreateRequest) -> TimelineEntry:
        """Create a new timeline entry."""
        response = self._post("/timeline-entries.create", request, TimelineEntriesCreateResponse)
        return response.timeline_entry

    def get(self, request: TimelineEntriesGetRequest) -> TimelineEntry:
        """Get a timeline entry by ID."""
        response = self._post("/timeline-entries.get", request, TimelineEntriesGetResponse)
        return response.timeline_entry

    def list(self, request: TimelineEntriesListRequest) -> Sequence[TimelineEntry]:
        """List timeline entries for an object."""
        response = self._post("/timeline-entries.list", request, TimelineEntriesListResponse)
        return response.timeline_entries

    def update(self, request: TimelineEntriesUpdateRequest) -> TimelineEntry:
        """Update a timeline entry."""
        response = self._post("/timeline-entries.update", request, TimelineEntriesUpdateResponse)
        return response.timeline_entry

    def delete(self, request: TimelineEntriesDeleteRequest) -> None:
        """Delete a timeline entry."""
        self._post("/timeline-entries.delete", request, TimelineEntriesDeleteResponse)


class AsyncTimelineEntriesService(AsyncBaseService):
    """Async service for managing DevRev Timeline Entries."""

    async def create(self, request: TimelineEntriesCreateRequest) -> TimelineEntry:
        """Create a new timeline entry."""
        response = await self._post(
            "/timeline-entries.create", request, TimelineEntriesCreateResponse
        )
        return response.timeline_entry

    async def get(self, request: TimelineEntriesGetRequest) -> TimelineEntry:
        """Get a timeline entry by ID."""
        response = await self._post("/timeline-entries.get", request, TimelineEntriesGetResponse)
        return response.timeline_entry

    async def list(self, request: TimelineEntriesListRequest) -> Sequence[TimelineEntry]:
        """List timeline entries for an object."""
        response = await self._post("/timeline-entries.list", request, TimelineEntriesListResponse)
        return response.timeline_entries

    async def update(self, request: TimelineEntriesUpdateRequest) -> TimelineEntry:
        """Update a timeline entry."""
        response = await self._post(
            "/timeline-entries.update", request, TimelineEntriesUpdateResponse
        )
        return response.timeline_entry

    async def delete(self, request: TimelineEntriesDeleteRequest) -> None:
        """Delete a timeline entry."""
        await self._post("/timeline-entries.delete", request, TimelineEntriesDeleteResponse)
