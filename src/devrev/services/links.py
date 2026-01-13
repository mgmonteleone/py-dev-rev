"""Links service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.links import (
    Link,
    LinksCreateRequest,
    LinksCreateResponse,
    LinksDeleteRequest,
    LinksDeleteResponse,
    LinksGetRequest,
    LinksGetResponse,
    LinksListRequest,
    LinksListResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class LinksService(BaseService):
    """Service for managing DevRev Links."""

    def create(self, request: LinksCreateRequest) -> Link:
        """Create a new link."""
        response = self._post("/links.create", request, LinksCreateResponse)
        return response.link

    def get(self, request: LinksGetRequest) -> Link:
        """Get a link by ID."""
        response = self._post("/links.get", request, LinksGetResponse)
        return response.link

    def list(self, request: LinksListRequest | None = None) -> Sequence[Link]:
        """List links."""
        if request is None:
            request = LinksListRequest()
        response = self._post("/links.list", request, LinksListResponse)
        return response.links

    def delete(self, request: LinksDeleteRequest) -> None:
        """Delete a link."""
        self._post("/links.delete", request, LinksDeleteResponse)


class AsyncLinksService(AsyncBaseService):
    """Async service for managing DevRev Links."""

    async def create(self, request: LinksCreateRequest) -> Link:
        """Create a new link."""
        response = await self._post("/links.create", request, LinksCreateResponse)
        return response.link

    async def get(self, request: LinksGetRequest) -> Link:
        """Get a link by ID."""
        response = await self._post("/links.get", request, LinksGetResponse)
        return response.link

    async def list(self, request: LinksListRequest | None = None) -> Sequence[Link]:
        """List links."""
        if request is None:
            request = LinksListRequest()
        response = await self._post("/links.list", request, LinksListResponse)
        return response.links

    async def delete(self, request: LinksDeleteRequest) -> None:
        """Delete a link."""
        await self._post("/links.delete", request, LinksDeleteResponse)
