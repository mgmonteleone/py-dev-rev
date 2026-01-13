"""Dev Users service for DevRev SDK.

This module provides the DevUsersService for managing DevRev developer users.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from devrev.models.dev_users import (
    DevUser,
    DevUsersActivateRequest,
    DevUsersActivateResponse,
    DevUsersCreateRequest,
    DevUsersCreateRequestStateEnum,
    DevUsersCreateResponse,
    DevUsersDeactivateRequest,
    DevUsersDeactivateResponse,
    DevUsersGetRequest,
    DevUsersGetResponse,
    DevUsersIdentitiesLinkRequest,
    DevUsersIdentitiesLinkResponse,
    DevUsersIdentitiesUnlinkRequest,
    DevUsersIdentitiesUnlinkResponse,
    DevUsersListRequest,
    DevUsersListResponse,
    DevUsersMergeRequest,
    DevUsersMergeResponse,
    DevUsersSelfRequest,
    DevUsersSelfResponse,
    DevUsersSelfUpdateRequest,
    DevUsersSelfUpdateResponse,
    DevUserState,
    DevUsersUpdateRequest,
    DevUsersUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class DevUsersService(BaseService):
    """Synchronous service for managing DevRev developer users."""

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the DevUsersService."""
        super().__init__(http_client)

    def create(
        self,
        email: str,
        *,
        display_name: str | None = None,
        full_name: str | None = None,
    ) -> DevUser:
        """Create a new Dev user.

        Note: New users are always created in the 'shadow' state.

        Args:
            email: User email address
            display_name: Display name
            full_name: Full name

        Returns:
            The created DevUser
        """
        request = DevUsersCreateRequest(
            email=email,
            state=DevUsersCreateRequestStateEnum.SHADOW,
            display_name=display_name,
            full_name=full_name,
        )
        response = self._post("/dev-users.create", request, DevUsersCreateResponse)
        return response.dev_user

    def get(self, id: str) -> DevUser:
        """Get a Dev user by ID.

        Args:
            id: Dev user ID

        Returns:
            The DevUser
        """
        request = DevUsersGetRequest(id=id)
        response = self._post("/dev-users.get", request, DevUsersGetResponse)
        return response.dev_user

    def list(
        self,
        *,
        cursor: str | None = None,
        email: list[str] | None = None,
        limit: int | None = None,
        state: list[DevUserState] | None = None,
    ) -> DevUsersListResponse:
        """List Dev users.

        Args:
            cursor: Pagination cursor
            email: Filter by emails
            limit: Maximum number of results
            state: Filter by user states

        Returns:
            Paginated list of Dev users
        """
        request = DevUsersListRequest(
            cursor=cursor,
            email=email,
            limit=limit,
            state=state,
        )
        return self._post("/dev-users.list", request, DevUsersListResponse)

    def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        full_name: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> DevUser:
        """Update a Dev user.

        Args:
            id: Dev user ID
            display_name: New display name
            full_name: New full name
            custom_fields: Custom fields to update

        Returns:
            The updated DevUser
        """
        request = DevUsersUpdateRequest(
            id=id,
            display_name=display_name,
            full_name=full_name,
            custom_fields=custom_fields,
        )
        response = self._post("/dev-users.update", request, DevUsersUpdateResponse)
        return response.dev_user

    def activate(self, id: str) -> DevUser:
        """Activate a Dev user.

        Args:
            id: Dev user ID

        Returns:
            The activated DevUser
        """
        request = DevUsersActivateRequest(id=id)
        response = self._post("/dev-users.activate", request, DevUsersActivateResponse)
        return response.dev_user

    def deactivate(self, id: str) -> None:
        """Deactivate a Dev user.

        Args:
            id: Dev user ID
        """
        request = DevUsersDeactivateRequest(id=id)
        self._post("/dev-users.deactivate", request, DevUsersDeactivateResponse)

    def identities_link(
        self,
        dev_user: str,
        id: str,
        issuer: str,
    ) -> DevUser:
        """Link an external identity to a Dev user.

        Args:
            dev_user: Dev user ID
            id: External identity ID
            issuer: Identity issuer

        Returns:
            The updated DevUser
        """
        request = DevUsersIdentitiesLinkRequest(
            dev_user=dev_user,
            id=id,
            issuer=issuer,
        )
        response = self._post("/dev-users.identities.link", request, DevUsersIdentitiesLinkResponse)
        return response.dev_user

    def identities_unlink(
        self,
        dev_user: str,
        id: str,
        issuer: str,
    ) -> DevUser:
        """Unlink an external identity from a Dev user.

        Args:
            dev_user: Dev user ID
            id: External identity ID
            issuer: Identity issuer

        Returns:
            The updated DevUser
        """
        request = DevUsersIdentitiesUnlinkRequest(
            dev_user=dev_user,
            id=id,
            issuer=issuer,
        )
        response = self._post(
            "/dev-users.identities.unlink", request, DevUsersIdentitiesUnlinkResponse
        )
        return response.dev_user

    def merge(self, primary_user: str, secondary_user: str) -> None:
        """Merge two Dev users.

        Args:
            primary_user: Primary user ID (will be retained)
            secondary_user: Secondary user ID (will be merged)
        """
        request = DevUsersMergeRequest(
            primary_user=primary_user,
            secondary_user=secondary_user,
        )
        self._post("/dev-users.merge", request, DevUsersMergeResponse)

    def self(self) -> DevUser:
        """Get the authenticated Dev user.

        Returns:
            The authenticated DevUser
        """
        request = DevUsersSelfRequest()
        response = self._post("/dev-users.self", request, DevUsersSelfResponse)
        return response.dev_user

    def self_update(
        self,
        *,
        display_name: str | None = None,
        full_name: str | None = None,
    ) -> DevUser:
        """Update the authenticated Dev user.

        Args:
            display_name: New display name
            full_name: New full name

        Returns:
            The updated DevUser
        """
        request = DevUsersSelfUpdateRequest(
            display_name=display_name,
            full_name=full_name,
        )
        response = self._post("/dev-users.self.update", request, DevUsersSelfUpdateResponse)
        return response.dev_user


class AsyncDevUsersService(AsyncBaseService):
    """Asynchronous service for managing DevRev developer users."""

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncDevUsersService."""
        super().__init__(http_client)

    async def create(
        self,
        email: str,
        *,
        display_name: str | None = None,
        full_name: str | None = None,
    ) -> DevUser:
        """Create a new Dev user (in shadow state)."""
        request = DevUsersCreateRequest(
            email=email,
            state=DevUsersCreateRequestStateEnum.SHADOW,
            display_name=display_name,
            full_name=full_name,
        )
        response = await self._post("/dev-users.create", request, DevUsersCreateResponse)
        return response.dev_user

    async def get(self, id: str) -> DevUser:
        """Get a Dev user by ID."""
        request = DevUsersGetRequest(id=id)
        response = await self._post("/dev-users.get", request, DevUsersGetResponse)
        return response.dev_user

    async def list(
        self,
        *,
        cursor: str | None = None,
        email: list[str] | None = None,
        limit: int | None = None,
        state: list[DevUserState] | None = None,
    ) -> DevUsersListResponse:
        """List Dev users."""
        request = DevUsersListRequest(cursor=cursor, email=email, limit=limit, state=state)
        return await self._post("/dev-users.list", request, DevUsersListResponse)

    async def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        full_name: str | None = None,
    ) -> DevUser:
        """Update a Dev user."""
        request = DevUsersUpdateRequest(id=id, display_name=display_name, full_name=full_name)
        response = await self._post("/dev-users.update", request, DevUsersUpdateResponse)
        return response.dev_user

    async def activate(self, id: str) -> DevUser:
        """Activate a Dev user."""
        request = DevUsersActivateRequest(id=id)
        response = await self._post("/dev-users.activate", request, DevUsersActivateResponse)
        return response.dev_user

    async def deactivate(self, id: str) -> None:
        """Deactivate a Dev user."""
        request = DevUsersDeactivateRequest(id=id)
        await self._post("/dev-users.deactivate", request, DevUsersDeactivateResponse)

    async def merge(self, primary_user: str, secondary_user: str) -> None:
        """Merge two Dev users."""
        request = DevUsersMergeRequest(primary_user=primary_user, secondary_user=secondary_user)
        await self._post("/dev-users.merge", request, DevUsersMergeResponse)

    async def self(self) -> DevUser:
        """Get the authenticated Dev user."""
        request = DevUsersSelfRequest()
        response = await self._post("/dev-users.self", request, DevUsersSelfResponse)
        return response.dev_user

    async def self_update(
        self,
        *,
        display_name: str | None = None,
        full_name: str | None = None,
    ) -> DevUser:
        """Update the authenticated Dev user."""
        request = DevUsersSelfUpdateRequest(display_name=display_name, full_name=full_name)
        response = await self._post("/dev-users.self.update", request, DevUsersSelfUpdateResponse)
        return response.dev_user
