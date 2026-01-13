"""Parts service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.parts import (
    Part,
    PartsCreateRequest,
    PartsCreateResponse,
    PartsDeleteRequest,
    PartsDeleteResponse,
    PartsGetRequest,
    PartsGetResponse,
    PartsListRequest,
    PartsListResponse,
    PartsUpdateRequest,
    PartsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class PartsService(BaseService):
    """Service for managing DevRev Parts."""

    def create(self, request: PartsCreateRequest) -> Part:
        """Create a new part."""
        response = self._post("/parts.create", request, PartsCreateResponse)
        return response.part

    def get(self, request: PartsGetRequest) -> Part:
        """Get a part by ID."""
        response = self._post("/parts.get", request, PartsGetResponse)
        return response.part

    def list(self, request: PartsListRequest | None = None) -> Sequence[Part]:
        """List parts."""
        if request is None:
            request = PartsListRequest()
        response = self._post("/parts.list", request, PartsListResponse)
        return response.parts

    def update(self, request: PartsUpdateRequest) -> Part:
        """Update a part."""
        response = self._post("/parts.update", request, PartsUpdateResponse)
        return response.part

    def delete(self, request: PartsDeleteRequest) -> None:
        """Delete a part."""
        self._post("/parts.delete", request, PartsDeleteResponse)


class AsyncPartsService(AsyncBaseService):
    """Async service for managing DevRev Parts."""

    async def create(self, request: PartsCreateRequest) -> Part:
        """Create a new part."""
        response = await self._post("/parts.create", request, PartsCreateResponse)
        return response.part

    async def get(self, request: PartsGetRequest) -> Part:
        """Get a part by ID."""
        response = await self._post("/parts.get", request, PartsGetResponse)
        return response.part

    async def list(self, request: PartsListRequest | None = None) -> Sequence[Part]:
        """List parts."""
        if request is None:
            request = PartsListRequest()
        response = await self._post("/parts.list", request, PartsListResponse)
        return response.parts

    async def update(self, request: PartsUpdateRequest) -> Part:
        """Update a part."""
        response = await self._post("/parts.update", request, PartsUpdateResponse)
        return response.part

    async def delete(self, request: PartsDeleteRequest) -> None:
        """Delete a part."""
        await self._post("/parts.delete", request, PartsDeleteResponse)

