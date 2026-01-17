"""Rev Users service for DevRev SDK.

This module provides the RevUsersService for managing DevRev customer users.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from devrev.models.rev_users import (
    RevUser,
    RevUsersAssociationsAddRequest,
    RevUsersAssociationsAddResponse,
    RevUsersAssociationsListRequest,
    RevUsersAssociationsListResponse,
    RevUsersAssociationsRemoveRequest,
    RevUsersAssociationsRemoveResponse,
    RevUsersCreateRequest,
    RevUsersCreateResponse,
    RevUsersDeletePersonalDataRequest,
    RevUsersDeletePersonalDataResponse,
    RevUsersDeleteRequest,
    RevUsersDeleteResponse,
    RevUsersGetPersonalDataRequest,
    RevUsersGetPersonalDataResponse,
    RevUsersGetRequest,
    RevUsersGetResponse,
    RevUsersLinkRequest,
    RevUsersLinkResponse,
    RevUsersListRequest,
    RevUsersListResponse,
    RevUsersMergeRequest,
    RevUsersMergeResponse,
    RevUsersUnlinkRequest,
    RevUsersUnlinkResponse,
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

    def associations_add(
        self,
        id: str,
        *,
        account: str | None = None,
        workspace: str | None = None,
    ) -> None:
        """Add associations to a Rev user (beta only).

        Args:
            id: Rev user ID
            account: Account ID to associate
            workspace: Workspace ID to associate

        Note:
            This method is only available with beta API.
        """
        request = RevUsersAssociationsAddRequest(id=id, account=account, workspace=workspace)
        self._post("/rev-users.associations.add", request, RevUsersAssociationsAddResponse)

    def associations_list(
        self,
        id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> RevUsersAssociationsListResponse:
        """List associations for a Rev user (beta only).

        Args:
            id: Rev user ID
            cursor: Pagination cursor
            limit: Maximum number of results

        Returns:
            Paginated list of associations

        Note:
            This method is only available with beta API.
        """
        request = RevUsersAssociationsListRequest(id=id, cursor=cursor, limit=limit)
        return self._post("/rev-users.associations.list", request, RevUsersAssociationsListResponse)

    def associations_remove(
        self,
        id: str,
        *,
        account: str | None = None,
        workspace: str | None = None,
    ) -> None:
        """Remove associations from a Rev user (beta only).

        Args:
            id: Rev user ID
            account: Account ID to remove
            workspace: Workspace ID to remove

        Note:
            This method is only available with beta API.
        """
        request = RevUsersAssociationsRemoveRequest(id=id, account=account, workspace=workspace)
        self._post("/rev-users.associations.remove", request, RevUsersAssociationsRemoveResponse)

    def delete_personal_data(self, id: str) -> None:
        """Delete personal data for a Rev user (beta only).

        This method is used for GDPR compliance to delete personal data.

        Args:
            id: Rev user ID

        Note:
            This method is only available with beta API.
        """
        request = RevUsersDeletePersonalDataRequest(id=id)
        self._post("/rev-users.delete-personal-data", request, RevUsersDeletePersonalDataResponse)

    def get_personal_data(self, id: str) -> dict[str, Any]:
        """Get personal data for a Rev user (beta only).

        Args:
            id: Rev user ID

        Returns:
            Personal data for the user

        Note:
            This method is only available with beta API.
        """
        request = RevUsersGetPersonalDataRequest(id=id)
        response = self._post("/rev-users.personal-data", request, RevUsersGetPersonalDataResponse)
        return response.personal_data

    def link(self, id: str, rev_org: str) -> None:
        """Link a Rev user to an organization (beta only).

        Args:
            id: Rev user ID
            rev_org: Rev organization ID to link to

        Note:
            This method is only available with beta API.
        """
        request = RevUsersLinkRequest(id=id, rev_org=rev_org)
        self._post("/rev-users.link", request, RevUsersLinkResponse)

    def unlink(self, id: str, rev_org: str) -> None:
        """Unlink a Rev user from an organization (beta only).

        Args:
            id: Rev user ID
            rev_org: Rev organization ID to unlink from

        Note:
            This method is only available with beta API.
        """
        request = RevUsersUnlinkRequest(id=id, rev_org=rev_org)
        self._post("/rev-users.unlink", request, RevUsersUnlinkResponse)


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
        request = RevUsersListRequest(cursor=cursor, email=email, limit=limit, rev_org=rev_org)
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
        request = RevUsersMergeRequest(primary_user=primary_user, secondary_user=secondary_user)
        await self._post("/rev-users.merge", request, RevUsersMergeResponse)

    async def associations_add(
        self,
        id: str,
        *,
        account: str | None = None,
        workspace: str | None = None,
    ) -> None:
        """Add associations to a Rev user (beta only).

        Args:
            id: Rev user ID
            account: Account ID to associate
            workspace: Workspace ID to associate

        Note:
            This method is only available with beta API.
        """
        request = RevUsersAssociationsAddRequest(id=id, account=account, workspace=workspace)
        await self._post("/rev-users.associations.add", request, RevUsersAssociationsAddResponse)

    async def associations_list(
        self,
        id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> RevUsersAssociationsListResponse:
        """List associations for a Rev user (beta only).

        Args:
            id: Rev user ID
            cursor: Pagination cursor
            limit: Maximum number of results

        Returns:
            Paginated list of associations

        Note:
            This method is only available with beta API.
        """
        request = RevUsersAssociationsListRequest(id=id, cursor=cursor, limit=limit)
        return await self._post("/rev-users.associations.list", request, RevUsersAssociationsListResponse)

    async def associations_remove(
        self,
        id: str,
        *,
        account: str | None = None,
        workspace: str | None = None,
    ) -> None:
        """Remove associations from a Rev user (beta only).

        Args:
            id: Rev user ID
            account: Account ID to remove
            workspace: Workspace ID to remove

        Note:
            This method is only available with beta API.
        """
        request = RevUsersAssociationsRemoveRequest(id=id, account=account, workspace=workspace)
        await self._post("/rev-users.associations.remove", request, RevUsersAssociationsRemoveResponse)

    async def delete_personal_data(self, id: str) -> None:
        """Delete personal data for a Rev user (beta only).

        This method is used for GDPR compliance to delete personal data.

        Args:
            id: Rev user ID

        Note:
            This method is only available with beta API.
        """
        request = RevUsersDeletePersonalDataRequest(id=id)
        await self._post("/rev-users.delete-personal-data", request, RevUsersDeletePersonalDataResponse)

    async def get_personal_data(self, id: str) -> dict[str, Any]:
        """Get personal data for a Rev user (beta only).

        Args:
            id: Rev user ID

        Returns:
            Personal data for the user

        Note:
            This method is only available with beta API.
        """
        request = RevUsersGetPersonalDataRequest(id=id)
        response = await self._post("/rev-users.personal-data", request, RevUsersGetPersonalDataResponse)
        return response.personal_data

    async def link(self, id: str, rev_org: str) -> None:
        """Link a Rev user to an organization (beta only).

        Args:
            id: Rev user ID
            rev_org: Rev organization ID to link to

        Note:
            This method is only available with beta API.
        """
        request = RevUsersLinkRequest(id=id, rev_org=rev_org)
        await self._post("/rev-users.link", request, RevUsersLinkResponse)

    async def unlink(self, id: str, rev_org: str) -> None:
        """Unlink a Rev user from an organization (beta only).

        Args:
            id: Rev user ID
            rev_org: Rev organization ID to unlink from

        Note:
            This method is only available with beta API.
        """
        request = RevUsersUnlinkRequest(id=id, rev_org=rev_org)
        await self._post("/rev-users.unlink", request, RevUsersUnlinkResponse)
