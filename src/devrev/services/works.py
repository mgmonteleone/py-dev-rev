"""Works service for DevRev SDK.

This module provides the WorksService for managing DevRev work items (issues and tickets).
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Any

from devrev.models.base import DateFilter, StageUpdate
from devrev.models.works import (
    IssuePriority,
    TicketSeverity,
    Work,
    WorksCountRequest,
    WorksCountResponse,
    WorksCreateRequest,
    WorksCreateResponse,
    WorksDeleteRequest,
    WorksDeleteResponse,
    WorksExportRequest,
    WorksExportResponse,
    WorksGetRequest,
    WorksGetResponse,
    WorksListRequest,
    WorksListResponse,
    WorksUpdateRequest,
    WorksUpdateRequestOwnedBy,
    WorksUpdateResponse,
    WorkType,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class WorksService(BaseService):
    """Synchronous service for managing DevRev work items.

    Provides methods for creating, reading, updating, and deleting issues and tickets.
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the WorksService."""
        super().__init__(http_client)

    def create(
        self,
        title: str,
        applies_to_part: str,
        type: WorkType,
        owned_by: Sequence[str],
        *,
        body: str | None = None,
        priority: IssuePriority | None = None,
        severity: TicketSeverity | None = None,
        target_close_date: datetime | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Work:
        """Create a new work item (issue or ticket).

        Args:
            title: Work item title
            applies_to_part: Part ID this work applies to
            type: Work type (issue or ticket)
            owned_by: Owner user IDs (required)
            body: Work item body/description
            priority: Issue priority (for issues)
            severity: Ticket severity (for tickets)
            target_close_date: Target close date
            custom_fields: Custom fields

        Returns:
            The created Work item
        """
        request = WorksCreateRequest(
            title=title,
            applies_to_part=applies_to_part,
            type=type,
            owned_by=list(owned_by),
            body=body,
            priority=priority,
            severity=severity,
            target_close_date=target_close_date,
            custom_fields=custom_fields,
        )
        response = self._post("/works.create", request, WorksCreateResponse)
        return response.work

    def get(self, id: str) -> Work:
        """Get a work item by ID.

        Args:
            id: Work item ID

        Returns:
            The Work item
        """
        request = WorksGetRequest(id=id)
        response = self._post("/works.get", request, WorksGetResponse)
        return response.work

    def list(
        self,
        *,
        type: Sequence[WorkType] | None = None,
        applies_to_part: Sequence[str] | None = None,
        created_by: Sequence[str] | None = None,
        created_date: DateFilter | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        owned_by: Sequence[str] | None = None,
        stage_name: Sequence[str] | None = None,
    ) -> WorksListResponse:
        """List work items.

        Args:
            type: Filter by work types
            applies_to_part: Filter by part IDs
            created_by: Filter by creator user IDs
            created_date: Filter by creation date
            cursor: Pagination cursor
            limit: Maximum number of results
            owned_by: Filter by owner user IDs
            stage_name: Filter by stage names

        Returns:
            Paginated list of work items
        """
        request = WorksListRequest(
            type=type,
            applies_to_part=applies_to_part,
            created_by=created_by,
            created_date=created_date,
            cursor=cursor,
            limit=limit,
            owned_by=owned_by,
            stage_name=stage_name,
        )
        return self._post("/works.list", request, WorksListResponse)

    def update(
        self,
        id: str,
        *,
        title: str | None = None,
        body: str | None = None,
        owned_by: Sequence[str] | None = None,
        stage: StageUpdate | None = None,
        priority: IssuePriority | None = None,
        severity: TicketSeverity | None = None,
        target_close_date: datetime | None = None,
    ) -> Work:
        """Update a work item.

        Args:
            id: Work item ID
            title: New title
            body: New body/description
            owned_by: New owner IDs
            stage: New stage
            priority: New priority (for issues)
            severity: New severity (for tickets)
            target_close_date: New target close date

        Returns:
            The updated Work item
        """
        owned_by_update = WorksUpdateRequestOwnedBy(set=owned_by) if owned_by else None
        request = WorksUpdateRequest(
            id=id,
            title=title,
            body=body,
            owned_by=owned_by_update,
            stage=stage,
            priority=priority,
            severity=severity,
            target_close_date=target_close_date,
        )
        response = self._post("/works.update", request, WorksUpdateResponse)
        return response.work

    def delete(self, id: str) -> None:
        """Delete a work item.

        Args:
            id: Work item ID to delete
        """
        request = WorksDeleteRequest(id=id)
        self._post("/works.delete", request, WorksDeleteResponse)

    def export(
        self,
        *,
        type: Sequence[WorkType] | None = None,
        applies_to_part: Sequence[str] | None = None,
        created_by: Sequence[str] | None = None,
        created_date: DateFilter | None = None,
        first: int | None = None,
    ) -> Sequence[Work]:
        """Export work items.

        Args:
            type: Filter by work types
            applies_to_part: Filter by part IDs
            created_by: Filter by creator user IDs
            created_date: Filter by creation date
            first: Maximum number of results

        Returns:
            List of exported work items
        """
        request = WorksExportRequest(
            type=type,
            applies_to_part=applies_to_part,
            created_by=created_by,
            created_date=created_date,
            first=first,
        )
        response = self._post("/works.export", request, WorksExportResponse)
        return response.works

    def count(
        self,
        *,
        type: Sequence[WorkType] | None = None,
        applies_to_part: Sequence[str] | None = None,
        created_by: Sequence[str] | None = None,
        owned_by: Sequence[str] | None = None,
    ) -> int:
        """Count work items.

        Args:
            type: Filter by work types
            applies_to_part: Filter by part IDs
            created_by: Filter by creator user IDs
            owned_by: Filter by owner user IDs

        Returns:
            Number of matching work items
        """
        request = WorksCountRequest(
            type=type,
            applies_to_part=applies_to_part,
            created_by=created_by,
            owned_by=owned_by,
        )
        response = self._post("/works.count", request, WorksCountResponse)
        return response.count


class AsyncWorksService(AsyncBaseService):
    """Asynchronous service for managing DevRev work items."""

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncWorksService."""
        super().__init__(http_client)

    async def create(
        self,
        title: str,
        applies_to_part: str,
        type: WorkType,
        owned_by: Sequence[str],
        *,
        body: str | None = None,
        priority: IssuePriority | None = None,
        severity: TicketSeverity | None = None,
        target_close_date: datetime | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Work:
        """Create a new work item."""
        request = WorksCreateRequest(
            title=title,
            applies_to_part=applies_to_part,
            type=type,
            owned_by=list(owned_by),
            body=body,
            priority=priority,
            severity=severity,
            target_close_date=target_close_date,
            custom_fields=custom_fields,
        )
        response = await self._post("/works.create", request, WorksCreateResponse)
        return response.work

    async def get(self, id: str) -> Work:
        """Get a work item by ID."""
        request = WorksGetRequest(id=id)
        response = await self._post("/works.get", request, WorksGetResponse)
        return response.work

    async def list(
        self,
        *,
        type: Sequence[WorkType] | None = None,
        applies_to_part: Sequence[str] | None = None,
        cursor: str | None = None,
        limit: int | None = None,
        owned_by: Sequence[str] | None = None,
    ) -> WorksListResponse:
        """List work items."""
        request = WorksListRequest(
            type=type,
            applies_to_part=applies_to_part,
            cursor=cursor,
            limit=limit,
            owned_by=owned_by,
        )
        return await self._post("/works.list", request, WorksListResponse)

    async def update(
        self,
        id: str,
        *,
        title: str | None = None,
        body: str | None = None,
        owned_by: Sequence[str] | None = None,
        priority: IssuePriority | None = None,
        severity: TicketSeverity | None = None,
    ) -> Work:
        """Update a work item."""
        owned_by_update = WorksUpdateRequestOwnedBy(set=owned_by) if owned_by else None
        request = WorksUpdateRequest(
            id=id,
            title=title,
            body=body,
            owned_by=owned_by_update,
            priority=priority,
            severity=severity,
        )
        response = await self._post("/works.update", request, WorksUpdateResponse)
        return response.work

    async def delete(self, id: str) -> None:
        """Delete a work item."""
        request = WorksDeleteRequest(id=id)
        await self._post("/works.delete", request, WorksDeleteResponse)

    async def export(
        self,
        *,
        type: Sequence[WorkType] | None = None,
        first: int | None = None,
    ) -> Sequence[Work]:
        """Export work items."""
        request = WorksExportRequest(type=type, first=first)
        response = await self._post("/works.export", request, WorksExportResponse)
        return response.works

    async def count(
        self,
        *,
        type: Sequence[WorkType] | None = None,
        owned_by: Sequence[str] | None = None,
    ) -> int:
        """Count work items."""
        request = WorksCountRequest(type=type, owned_by=owned_by)
        response = await self._post("/works.count", request, WorksCountResponse)
        return response.count
