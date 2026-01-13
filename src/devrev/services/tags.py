"""Tags service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.tags import (
    Tag,
    TagsCreateRequest,
    TagsCreateResponse,
    TagsDeleteRequest,
    TagsDeleteResponse,
    TagsGetRequest,
    TagsGetResponse,
    TagsListRequest,
    TagsListResponse,
    TagsUpdateRequest,
    TagsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class TagsService(BaseService):
    """Service for managing DevRev Tags."""

    def create(self, request: TagsCreateRequest) -> Tag:
        """Create a new tag."""
        response = self._post("/tags.create", request, TagsCreateResponse)
        return response.tag

    def get(self, request: TagsGetRequest) -> Tag:
        """Get a tag by ID."""
        response = self._post("/tags.get", request, TagsGetResponse)
        return response.tag

    def list(self, request: TagsListRequest | None = None) -> Sequence[Tag]:
        """List tags."""
        if request is None:
            request = TagsListRequest()
        response = self._post("/tags.list", request, TagsListResponse)
        return response.tags

    def update(self, request: TagsUpdateRequest) -> Tag:
        """Update a tag."""
        response = self._post("/tags.update", request, TagsUpdateResponse)
        return response.tag

    def delete(self, request: TagsDeleteRequest) -> None:
        """Delete a tag."""
        self._post("/tags.delete", request, TagsDeleteResponse)


class AsyncTagsService(AsyncBaseService):
    """Async service for managing DevRev Tags."""

    async def create(self, request: TagsCreateRequest) -> Tag:
        """Create a new tag."""
        response = await self._post("/tags.create", request, TagsCreateResponse)
        return response.tag

    async def get(self, request: TagsGetRequest) -> Tag:
        """Get a tag by ID."""
        response = await self._post("/tags.get", request, TagsGetResponse)
        return response.tag

    async def list(self, request: TagsListRequest | None = None) -> Sequence[Tag]:
        """List tags."""
        if request is None:
            request = TagsListRequest()
        response = await self._post("/tags.list", request, TagsListResponse)
        return response.tags

    async def update(self, request: TagsUpdateRequest) -> Tag:
        """Update a tag."""
        response = await self._post("/tags.update", request, TagsUpdateResponse)
        return response.tag

    async def delete(self, request: TagsDeleteRequest) -> None:
        """Delete a tag."""
        await self._post("/tags.delete", request, TagsDeleteResponse)
