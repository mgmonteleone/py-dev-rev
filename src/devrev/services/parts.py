"""Parts service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.parts import (
    ParentPartFilter,
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


def _build_parent_part_filter(
    parent_part_parts: Sequence[str] | None,
    parent_part_level: int | None,
) -> ParentPartFilter | None:
    """Build a ``ParentPartFilter`` from explicit list parameters.

    Args:
        parent_part_parts: Part IDs to fetch the hierarchy for.
        parent_part_level: Number of hierarchy levels to fetch.

    Returns:
        A ``ParentPartFilter`` when ``parent_part_parts`` is provided, else None.
    """
    if parent_part_parts:
        return ParentPartFilter(parts=list(parent_part_parts), level=parent_part_level)
    return None


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

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        parent_part_parts: Sequence[str] | None = None,
        parent_part_level: int | None = None,
    ) -> PartsListResponse:
        """List parts.

        Args:
            limit: Maximum number of results to return (1-100).
            cursor: Pagination cursor from previous response.
            parent_part_parts: Filter to the hierarchy of these part IDs.
            parent_part_level: Number of hierarchy levels to fetch (requires
                ``parent_part_parts``).

        Returns:
            PartsListResponse with parts and next_cursor for pagination.
        """
        request = PartsListRequest(
            limit=limit,
            cursor=cursor,
            parent_part=_build_parent_part_filter(parent_part_parts, parent_part_level),
        )
        return self._post("/parts.list", request, PartsListResponse)

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

    async def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        parent_part_parts: Sequence[str] | None = None,
        parent_part_level: int | None = None,
    ) -> PartsListResponse:
        """List parts.

        Args:
            limit: Maximum number of results to return (1-100).
            cursor: Pagination cursor from previous response.
            parent_part_parts: Filter to the hierarchy of these part IDs.
            parent_part_level: Number of hierarchy levels to fetch (requires
                ``parent_part_parts``).

        Returns:
            PartsListResponse with parts and next_cursor for pagination.
        """
        request = PartsListRequest(
            limit=limit,
            cursor=cursor,
            parent_part=_build_parent_part_filter(parent_part_parts, parent_part_level),
        )
        return await self._post("/parts.list", request, PartsListResponse)

    async def update(self, request: PartsUpdateRequest) -> Part:
        """Update a part."""
        response = await self._post("/parts.update", request, PartsUpdateResponse)
        return response.part

    async def delete(self, request: PartsDeleteRequest) -> None:
        """Delete a part."""
        await self._post("/parts.delete", request, PartsDeleteResponse)
