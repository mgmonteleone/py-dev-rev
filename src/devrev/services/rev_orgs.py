"""Rev Orgs service for DevRev SDK.

This module provides the RevOrgsService for managing DevRev Rev Orgs
(Revenue Organizations).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from devrev.models.rev_orgs import (
    RevOrg,
    RevOrgsCreateRequest,
    RevOrgsCreateResponse,
    RevOrgsDeleteRequest,
    RevOrgsDeleteResponse,
    RevOrgsGetRequest,
    RevOrgsGetResponse,
    RevOrgsListRequest,
    RevOrgsListResponse,
    RevOrgsUpdateRequest,
    RevOrgsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class RevOrgsService(BaseService):
    """Synchronous service for managing DevRev Rev Orgs.

    Provides methods for creating, reading, updating, and deleting
    Rev Orgs (Revenue Organizations).

    Example:
        ```python
        from devrev import DevRevClient

        client = DevRevClient()
        rev_orgs = client.rev_orgs.list()
        ```
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the RevOrgsService."""
        super().__init__(http_client)

    def create(
        self,
        display_name: str,
        account: str,
        *,
        description: str | None = None,
        external_ref: str | None = None,
        tier: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> RevOrg:
        """Create a new rev org.

        Args:
            display_name: Rev org display name
            account: Parent account ID
            description: Rev org description
            external_ref: External reference identifier
            tier: Rev org tier
            custom_fields: Custom fields

        Returns:
            The created RevOrg
        """
        request = RevOrgsCreateRequest(
            display_name=display_name,
            account=account,
            description=description,
            external_ref=external_ref,
            tier=tier,
            custom_fields=custom_fields,
        )
        response = self._post("/rev-orgs.create", request, RevOrgsCreateResponse)
        return response.rev_org

    def get(self, id: str) -> RevOrg:
        """Get a rev org by ID.

        Args:
            id: Rev org ID

        Returns:
            The RevOrg
        """
        request = RevOrgsGetRequest(id=id)
        response = self._post("/rev-orgs.get", request, RevOrgsGetResponse)
        return response.rev_org

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        account: list[str] | None = None,
        display_name: list[str] | None = None,
        domains: list[str] | None = None,
        external_refs: list[str] | None = None,
        owned_by: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> RevOrgsListResponse:
        """List rev orgs.

        Args:
            cursor: Pagination cursor
            limit: Maximum number of results
            account: Filter by account IDs
            display_name: Filter by display names
            domains: Filter by domains
            external_refs: Filter by external refs
            owned_by: Filter by owner user IDs
            tags: Filter by tag IDs

        Returns:
            Paginated list of rev orgs
        """
        request = RevOrgsListRequest(
            cursor=cursor,
            limit=limit,
            account=account,
            display_name=display_name,
            domains=domains,
            external_refs=external_refs,
            owned_by=owned_by,
            tags=tags,
        )
        return self._post("/rev-orgs.list", request, RevOrgsListResponse)

    def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        description: str | None = None,
        tier: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> RevOrg:
        """Update a rev org.

        Args:
            id: Rev org ID
            display_name: New display name
            description: New description
            tier: New tier
            custom_fields: Custom fields to update

        Returns:
            The updated RevOrg
        """
        request = RevOrgsUpdateRequest(
            id=id,
            display_name=display_name,
            description=description,
            tier=tier,
            custom_fields=custom_fields,
        )
        response = self._post("/rev-orgs.update", request, RevOrgsUpdateResponse)
        return response.rev_org

    def delete(self, id: str) -> None:
        """Delete a rev org.

        Args:
            id: Rev org ID to delete
        """
        request = RevOrgsDeleteRequest(id=id)
        self._post("/rev-orgs.delete", request, RevOrgsDeleteResponse)


class AsyncRevOrgsService(AsyncBaseService):
    """Asynchronous service for managing DevRev Rev Orgs.

    Provides async methods for creating, reading, updating, and deleting
    Rev Orgs (Revenue Organizations).

    Example:
        ```python
        from devrev import AsyncDevRevClient

        async with AsyncDevRevClient() as client:
            rev_orgs = await client.rev_orgs.list()
        ```
    """

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncRevOrgsService."""
        super().__init__(http_client)

    async def create(
        self,
        display_name: str,
        account: str,
        *,
        description: str | None = None,
        external_ref: str | None = None,
        tier: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> RevOrg:
        """Create a new rev org."""
        request = RevOrgsCreateRequest(
            display_name=display_name,
            account=account,
            description=description,
            external_ref=external_ref,
            tier=tier,
            custom_fields=custom_fields,
        )
        response = await self._post("/rev-orgs.create", request, RevOrgsCreateResponse)
        return response.rev_org

    async def get(self, id: str) -> RevOrg:
        """Get a rev org by ID."""
        request = RevOrgsGetRequest(id=id)
        response = await self._post("/rev-orgs.get", request, RevOrgsGetResponse)
        return response.rev_org

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        account: list[str] | None = None,
        display_name: list[str] | None = None,
        domains: list[str] | None = None,
        external_refs: list[str] | None = None,
        owned_by: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> RevOrgsListResponse:
        """List rev orgs."""
        request = RevOrgsListRequest(
            cursor=cursor,
            limit=limit,
            account=account,
            display_name=display_name,
            domains=domains,
            external_refs=external_refs,
            owned_by=owned_by,
            tags=tags,
        )
        return await self._post("/rev-orgs.list", request, RevOrgsListResponse)

    async def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        description: str | None = None,
        tier: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> RevOrg:
        """Update a rev org."""
        request = RevOrgsUpdateRequest(
            id=id,
            display_name=display_name,
            description=description,
            tier=tier,
            custom_fields=custom_fields,
        )
        response = await self._post("/rev-orgs.update", request, RevOrgsUpdateResponse)
        return response.rev_org

    async def delete(self, id: str) -> None:
        """Delete a rev org."""
        request = RevOrgsDeleteRequest(id=id)
        await self._post("/rev-orgs.delete", request, RevOrgsDeleteResponse)
