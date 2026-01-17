"""Engagements service for DevRev SDK.

This module provides the EngagementsService for managing DevRev engagements.
"""

from __future__ import annotations

from builtins import list as list_type
from datetime import datetime
from typing import TYPE_CHECKING

from devrev.models.engagements import (
    Engagement,
    EngagementsCountRequest,
    EngagementsCountResponse,
    EngagementsCreateRequest,
    EngagementsCreateResponse,
    EngagementsDeleteRequest,
    EngagementsDeleteResponse,
    EngagementsGetRequest,
    EngagementsGetResponse,
    EngagementsListRequest,
    EngagementsListResponse,
    EngagementsUpdateRequest,
    EngagementsUpdateResponse,
    EngagementType,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class EngagementsService(BaseService):
    """Synchronous service for managing DevRev engagements.

    Provides methods for creating, reading, updating, and deleting engagements.

    Example:
        ```python
        from devrev import DevRevClient

        client = DevRevClient()
        engagements = client.engagements.list()
        ```
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the EngagementsService."""
        super().__init__(http_client)

    def create(
        self,
        title: str,
        engagement_type: EngagementType,
        *,
        description: str | None = None,
        members: list[str] | None = None,
        parent: str | None = None,
        scheduled_date: datetime | None = None,
        tags: list[str] | None = None,
    ) -> Engagement:
        """Create a new engagement.

        Args:
            title: Engagement title
            engagement_type: Type of engagement
            description: Engagement description
            members: Member user IDs
            parent: Parent engagement ID
            scheduled_date: Scheduled date/time
            tags: Tag IDs

        Returns:
            The created Engagement
        """
        request = EngagementsCreateRequest(
            title=title,
            engagement_type=engagement_type,
            description=description,
            members=members,
            parent=parent,
            scheduled_date=scheduled_date,
            tags=tags,
        )
        response = self._post("/engagements.create", request, EngagementsCreateResponse)
        return response.engagement

    def get(self, id: str) -> Engagement:
        """Get an engagement by ID.

        Args:
            id: Engagement ID

        Returns:
            The Engagement
        """
        request = EngagementsGetRequest(id=id)
        response = self._post("/engagements.get", request, EngagementsGetResponse)
        return response.engagement

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        engagement_type: list[EngagementType] | None = None,
        members: list[str] | None = None,
        parent: str | None = None,
    ) -> EngagementsListResponse:
        """List engagements.

        Args:
            cursor: Pagination cursor
            limit: Maximum number of results
            engagement_type: Filter by engagement types
            members: Filter by member user IDs
            parent: Filter by parent engagement ID

        Returns:
            Paginated list of engagements
        """
        request = EngagementsListRequest(
            cursor=cursor,
            limit=limit,
            engagement_type=engagement_type,
            members=members,
            parent=parent,
        )
        return self._post("/engagements.list", request, EngagementsListResponse)

    def update(
        self,
        id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        engagement_type: EngagementType | None = None,
        scheduled_date: datetime | None = None,
    ) -> Engagement:
        """Update an engagement.

        Args:
            id: Engagement ID
            title: New title
            description: New description
            engagement_type: New engagement type
            scheduled_date: New scheduled date/time

        Returns:
            The updated Engagement
        """
        request = EngagementsUpdateRequest(
            id=id,
            title=title,
            description=description,
            engagement_type=engagement_type,
            scheduled_date=scheduled_date,
        )
        response = self._post("/engagements.update", request, EngagementsUpdateResponse)
        return response.engagement

    def delete(self, id: str) -> None:
        """Delete an engagement.

        Args:
            id: Engagement ID to delete
        """
        request = EngagementsDeleteRequest(id=id)
        self._post("/engagements.delete", request, EngagementsDeleteResponse)

    def count(
        self,
        *,
        engagement_type: list_type[EngagementType] | None = None,
        members: list_type[str] | None = None,
    ) -> int:
        """Count engagements.

        Args:
            engagement_type: Filter by engagement types
            members: Filter by member user IDs

        Returns:
            Total count of engagements
        """
        request = EngagementsCountRequest(
            engagement_type=engagement_type,
            members=members,
        )
        response = self._post("/engagements.count", request, EngagementsCountResponse)
        return response.count


class AsyncEngagementsService(AsyncBaseService):
    """Asynchronous service for managing DevRev engagements.

    Provides async methods for creating, reading, updating, and deleting engagements.

    Example:
        ```python
        from devrev import AsyncDevRevClient

        async with AsyncDevRevClient() as client:
            engagements = await client.engagements.list()
        ```
    """

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncEngagementsService."""
        super().__init__(http_client)

    async def create(
        self,
        title: str,
        engagement_type: EngagementType,
        *,
        description: str | None = None,
        members: list[str] | None = None,
        parent: str | None = None,
        scheduled_date: datetime | None = None,
        tags: list[str] | None = None,
    ) -> Engagement:
        """Create a new engagement."""
        request = EngagementsCreateRequest(
            title=title,
            engagement_type=engagement_type,
            description=description,
            members=members,
            parent=parent,
            scheduled_date=scheduled_date,
            tags=tags,
        )
        response = await self._post("/engagements.create", request, EngagementsCreateResponse)
        return response.engagement

    async def get(self, id: str) -> Engagement:
        """Get an engagement by ID."""
        request = EngagementsGetRequest(id=id)
        response = await self._post("/engagements.get", request, EngagementsGetResponse)
        return response.engagement

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        engagement_type: list[EngagementType] | None = None,
        members: list[str] | None = None,
        parent: str | None = None,
    ) -> EngagementsListResponse:
        """List engagements."""
        request = EngagementsListRequest(
            cursor=cursor,
            limit=limit,
            engagement_type=engagement_type,
            members=members,
            parent=parent,
        )
        return await self._post("/engagements.list", request, EngagementsListResponse)

    async def update(
        self,
        id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        engagement_type: EngagementType | None = None,
        scheduled_date: datetime | None = None,
    ) -> Engagement:
        """Update an engagement."""
        request = EngagementsUpdateRequest(
            id=id,
            title=title,
            description=description,
            engagement_type=engagement_type,
            scheduled_date=scheduled_date,
        )
        response = await self._post("/engagements.update", request, EngagementsUpdateResponse)
        return response.engagement

    async def delete(self, id: str) -> None:
        """Delete an engagement."""
        request = EngagementsDeleteRequest(id=id)
        await self._post("/engagements.delete", request, EngagementsDeleteResponse)

    async def count(
        self,
        *,
        engagement_type: list_type[EngagementType] | None = None,
        members: list_type[str] | None = None,
    ) -> int:
        """Count engagements."""
        request = EngagementsCountRequest(
            engagement_type=engagement_type,
            members=members,
        )
        response = await self._post("/engagements.count", request, EngagementsCountResponse)
        return response.count
