"""Incidents service for DevRev SDK.

This module provides the IncidentsService for managing DevRev incidents.
"""

from __future__ import annotations

from builtins import list as list_type
from typing import TYPE_CHECKING

from devrev.models.incidents import (
    Incident,
    IncidentGroupItem,
    IncidentsCreateRequest,
    IncidentsCreateResponse,
    IncidentsDeleteRequest,
    IncidentsDeleteResponse,
    IncidentSeverity,
    IncidentsGetRequest,
    IncidentsGetResponse,
    IncidentsGroupRequest,
    IncidentsGroupResponse,
    IncidentsListRequest,
    IncidentsListResponse,
    IncidentStage,
    IncidentsUpdateRequest,
    IncidentsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class IncidentsService(BaseService):
    """Synchronous service for managing DevRev incidents.

    Provides methods for creating, reading, updating, and deleting incidents.

    Example:
        ```python
        from devrev import DevRevClient

        client = DevRevClient()
        incidents = client.incidents.list()
        ```
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the IncidentsService."""
        super().__init__(http_client)

    def create(
        self,
        title: str,
        *,
        body: str | None = None,
        severity: IncidentSeverity | None = None,
        owned_by: list[str] | None = None,
        applies_to_parts: list[str] | None = None,
    ) -> Incident:
        """Create a new incident.

        Args:
            title: Incident title
            body: Incident description
            severity: Incident severity
            owned_by: Owner user IDs
            applies_to_parts: Parts this incident applies to

        Returns:
            The created Incident
        """
        request = IncidentsCreateRequest(
            title=title,
            body=body,
            severity=severity,
            owned_by=owned_by,
            applies_to_parts=applies_to_parts,
        )
        response = self._post("/incidents.create", request, IncidentsCreateResponse)
        return response.incident

    def get(self, id: str) -> Incident:
        """Get an incident by ID.

        Args:
            id: Incident ID

        Returns:
            The Incident
        """
        request = IncidentsGetRequest(id=id)
        response = self._post("/incidents.get", request, IncidentsGetResponse)
        return response.incident

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        stage: list[IncidentStage] | None = None,
        severity: list[IncidentSeverity] | None = None,
    ) -> IncidentsListResponse:
        """List incidents.

        Args:
            cursor: Pagination cursor
            limit: Maximum number of results
            stage: Filter by stages
            severity: Filter by severities

        Returns:
            Paginated list of incidents
        """
        request = IncidentsListRequest(
            cursor=cursor,
            limit=limit,
            stage=stage,
            severity=severity,
        )
        return self._post("/incidents.list", request, IncidentsListResponse)

    def update(
        self,
        id: str,
        *,
        title: str | None = None,
        body: str | None = None,
        stage: IncidentStage | None = None,
        severity: IncidentSeverity | None = None,
    ) -> Incident:
        """Update an incident.

        Args:
            id: Incident ID
            title: New title
            body: New description
            stage: New stage
            severity: New severity

        Returns:
            The updated Incident
        """
        request = IncidentsUpdateRequest(
            id=id,
            title=title,
            body=body,
            stage=stage,
            severity=severity,
        )
        response = self._post("/incidents.update", request, IncidentsUpdateResponse)
        return response.incident

    def delete(self, id: str) -> None:
        """Delete an incident.

        Args:
            id: Incident ID to delete
        """
        request = IncidentsDeleteRequest(id=id)
        self._post("/incidents.delete", request, IncidentsDeleteResponse)

    def group(
        self,
        group_by: str,
        *,
        limit: int | None = None,
    ) -> list_type[IncidentGroupItem]:
        """Group incidents by a field.

        Args:
            group_by: Field to group by
            limit: Maximum number of results

        Returns:
            List of grouped incident results
        """
        request = IncidentsGroupRequest(
            group_by=group_by,
            limit=limit,
        )
        response = self._post("/incidents.group", request, IncidentsGroupResponse)
        return response.groups


class AsyncIncidentsService(AsyncBaseService):
    """Asynchronous service for managing DevRev incidents.

    Provides async methods for creating, reading, updating, and deleting incidents.

    Example:
        ```python
        from devrev import AsyncDevRevClient

        async with AsyncDevRevClient() as client:
            incidents = await client.incidents.list()
        ```
    """

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncIncidentsService."""
        super().__init__(http_client)

    async def create(
        self,
        title: str,
        *,
        body: str | None = None,
        severity: IncidentSeverity | None = None,
        owned_by: list[str] | None = None,
        applies_to_parts: list[str] | None = None,
    ) -> Incident:
        """Create a new incident."""
        request = IncidentsCreateRequest(
            title=title,
            body=body,
            severity=severity,
            owned_by=owned_by,
            applies_to_parts=applies_to_parts,
        )
        response = await self._post("/incidents.create", request, IncidentsCreateResponse)
        return response.incident

    async def get(self, id: str) -> Incident:
        """Get an incident by ID."""
        request = IncidentsGetRequest(id=id)
        response = await self._post("/incidents.get", request, IncidentsGetResponse)
        return response.incident

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        stage: list[IncidentStage] | None = None,
        severity: list[IncidentSeverity] | None = None,
    ) -> IncidentsListResponse:
        """List incidents."""
        request = IncidentsListRequest(
            cursor=cursor,
            limit=limit,
            stage=stage,
            severity=severity,
        )
        return await self._post("/incidents.list", request, IncidentsListResponse)

    async def update(
        self,
        id: str,
        *,
        title: str | None = None,
        body: str | None = None,
        stage: IncidentStage | None = None,
        severity: IncidentSeverity | None = None,
    ) -> Incident:
        """Update an incident."""
        request = IncidentsUpdateRequest(
            id=id,
            title=title,
            body=body,
            stage=stage,
            severity=severity,
        )
        response = await self._post("/incidents.update", request, IncidentsUpdateResponse)
        return response.incident

    async def delete(self, id: str) -> None:
        """Delete an incident."""
        request = IncidentsDeleteRequest(id=id)
        await self._post("/incidents.delete", request, IncidentsDeleteResponse)

    async def group(
        self,
        group_by: str,
        *,
        limit: int | None = None,
    ) -> list_type[IncidentGroupItem]:
        """Group incidents by a field."""
        request = IncidentsGroupRequest(
            group_by=group_by,
            limit=limit,
        )
        response = await self._post("/incidents.group", request, IncidentsGroupResponse)
        return response.groups
