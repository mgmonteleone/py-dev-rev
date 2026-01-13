"""Rev Users service for DevRev SDK.

This module provides the RevUsersService for managing DevRev customer users.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from devrev.models.rev_users import (
    RevUser,
    RevUsersCreateRequest,
    RevUsersCreateResponse,
    RevUsersDeleteRequest,
    RevUsersDeleteResponse,
    RevUsersGetRequest,
    RevUsersGetResponse,
    RevUsersListRequest,
    RevUsersListResponse,
    RevUsersMergeRequest,
    RevUsersMergeResponse,
    RevUsersUpdateRequest,
    RevUsersUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class RevUsersService(BaseService):
    """Synchronous service for managing DevRev customer users."""

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the RevUsersService."""
        super().__init__(http_client)

    def create(
        self,
        rev_org: str,
        *,
        display_name: str | None = None,
        email: str | None = None,
        phone_numbers: list[str] | None = None,
        external_ref: str | None = None,
    ) -> RevUser:
        """Create a new Rev user.

        Args:
            rev_org: Rev organization ID
            display_name: Display name
            email: Email address
            phone_numbers: Phone numbers
            external_ref: External reference identifier

        Returns:
            The created RevUser
        """
        request = RevUsersCreateRequest(
            rev_org=rev_org,
            display_name=display_name,
            email=email,
            phone_numbers=phone_numbers,
            external_ref=external_ref,
        )
        response = self._post("/rev-users.create", request, RevUsersCreateResponse)
        return response.rev_user

    def get(self, id: str) -> RevUser:
        """Get a Rev user by ID.

        Args:
            id: Rev user ID

        Returns:
            The RevUser
        """
        request = RevUsersGetRequest(id=id)
        response = self._post("/rev-users.get", request, RevUsersGetResponse)
        return response.rev_user

    def list(
        self,
        *,
        cursor: str | None = None,
        email: list[str] | None = None,
        limit: int | None = None,
        rev_org: list[str] | None = None,
        external_ref: list[str] | None = None,
    ) -> RevUsersListResponse:
        """List Rev users.

        Args:
            cursor: Pagination cursor
            email: Filter by emails
            limit: Maximum number of results
            rev_org: Filter by Rev org IDs
            external_ref: Filter by external refs

        Returns:
            Paginated list of Rev users
        """
        request = RevUsersListRequest(
            cursor=cursor,
            email=email,
            limit=limit,
            rev_org=rev_org,
            external_ref=external_ref,
        )
        return self._post("/rev-users.list", request, RevUsersListResponse)

    def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        email: str | None = None,
        phone_numbers: Sequence[str] | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> RevUser:
        """Update a Rev user.

        Args:
            id: Rev user ID
            display_name: New display name
            email: New email address
            phone_numbers: New phone numbers
            custom_fields: Custom fields to update

        Returns:
            The updated RevUser
        """
        request = RevUsersUpdateRequest(
            id=id,
            display_name=display_name,
            email=email,
            phone_numbers=phone_numbers,
            custom_fields=custom_fields,
        )
        response = self._post("/rev-users.update", request, RevUsersUpdateResponse)
        return response.rev_user

    def delete(self, id: str) -> None:
        """Delete a Rev user.

        Args:
            id: Rev user ID
        """
        request = RevUsersDeleteRequest(id=id)
        self._post("/rev-users.delete", request, RevUsersDeleteResponse)

    def merge(self, primary_user: str, secondary_user: str) -> None:
        """Merge two Rev users.

        Args:
            primary_user: Primary user ID (will be retained)
            secondary_user: Secondary user ID (will be merged)
        """
        request = RevUsersMergeRequest(
            primary_user=primary_user,
            secondary_user=secondary_user,
        )
        self._post("/rev-users.merge", request, RevUsersMergeResponse)


class AsyncRevUsersService(AsyncBaseService):
    """Asynchronous service for managing DevRev customer users."""

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncRevUsersService."""
        super().__init__(http_client)

    async def create(
        self,
        rev_org: str,
        *,
        display_name: str | None = None,
        email: str | None = None,
        phone_numbers: list[str] | None = None,
        external_ref: str | None = None,
    ) -> RevUser:
        """Create a new Rev user."""
        request = RevUsersCreateRequest(
            rev_org=rev_org,
            display_name=display_name,
            email=email,
            phone_numbers=phone_numbers,
            external_ref=external_ref,
        )
        response = await self._post("/rev-users.create", request, RevUsersCreateResponse)
        return response.rev_user

    async def get(self, id: str) -> RevUser:
        """Get a Rev user by ID."""
        request = RevUsersGetRequest(id=id)
        response = await self._post("/rev-users.get", request, RevUsersGetResponse)
        return response.rev_user

    async def list(
        self,
        *,
        cursor: str | None = None,
        email: list[str] | None = None,
        limit: int | None = None,
        rev_org: list[str] | None = None,
    ) -> RevUsersListResponse:
        """List Rev users."""
        request = RevUsersListRequest(
            cursor=cursor, email=email, limit=limit, rev_org=rev_org
        )
        return await self._post("/rev-users.list", request, RevUsersListResponse)

    async def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        email: str | None = None,
        phone_numbers: Sequence[str] | None = None,
    ) -> RevUser:
        """Update a Rev user."""
        request = RevUsersUpdateRequest(
            id=id, display_name=display_name, email=email, phone_numbers=phone_numbers
        )
        response = await self._post("/rev-users.update", request, RevUsersUpdateResponse)
        return response.rev_user

    async def delete(self, id: str) -> None:
        """Delete a Rev user."""
        request = RevUsersDeleteRequest(id=id)
        await self._post("/rev-users.delete", request, RevUsersDeleteResponse)

    async def merge(self, primary_user: str, secondary_user: str) -> None:
        """Merge two Rev users."""
        request = RevUsersMergeRequest(
            primary_user=primary_user, secondary_user=secondary_user
        )
        await self._post("/rev-users.merge", request, RevUsersMergeResponse)
