"""Accounts service for DevRev SDK.

This module provides the AccountsService for managing DevRev accounts.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from devrev.models.accounts import (
    Account,
    AccountsCreateRequest,
    AccountsCreateResponse,
    AccountsDeleteRequest,
    AccountsDeleteResponse,
    AccountsExportRequest,
    AccountsExportResponse,
    AccountsGetRequest,
    AccountsGetResponse,
    AccountsListRequest,
    AccountsListResponse,
    AccountsMergeRequest,
    AccountsMergeResponse,
    AccountsUpdateRequest,
    AccountsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class AccountsService(BaseService):
    """Synchronous service for managing DevRev accounts.

    Provides methods for creating, reading, updating, and deleting accounts.

    Example:
        ```python
        from devrev import DevRevClient

        client = DevRevClient()
        accounts = client.accounts.list()
        ```
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the AccountsService."""
        super().__init__(http_client)

    def create(
        self,
        display_name: str,
        *,
        description: str | None = None,
        domains: list[str] | None = None,
        external_refs: list[str] | None = None,
        owned_by: list[str] | None = None,
        tier: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Account:
        """Create a new account.

        Args:
            display_name: Account display name
            description: Account description
            domains: Associated domains
            external_refs: External references
            owned_by: Owner user IDs
            tier: Account tier
            custom_fields: Custom fields

        Returns:
            The created Account
        """
        request = AccountsCreateRequest(
            display_name=display_name,
            description=description,
            domains=domains,
            external_refs=external_refs,
            owned_by=owned_by,
            tier=tier,
            custom_fields=custom_fields,
        )
        response = self._post("/accounts.create", request, AccountsCreateResponse)
        return response.account

    def get(self, id: str) -> Account:
        """Get an account by ID.

        Args:
            id: Account ID

        Returns:
            The Account
        """
        request = AccountsGetRequest(id=id)
        response = self._post("/accounts.get", request, AccountsGetResponse)
        return response.account

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        display_name: list[str] | None = None,
        domains: list[str] | None = None,
        owned_by: list[str] | None = None,
    ) -> AccountsListResponse:
        """List accounts.

        Args:
            cursor: Pagination cursor
            limit: Maximum number of results
            display_name: Filter by display names
            domains: Filter by domains
            owned_by: Filter by owner user IDs

        Returns:
            Paginated list of accounts
        """
        request = AccountsListRequest(
            cursor=cursor,
            limit=limit,
            display_name=display_name,
            domains=domains,
            owned_by=owned_by,
        )
        return self._post("/accounts.list", request, AccountsListResponse)

    def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        description: str | None = None,
        tier: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Account:
        """Update an account.

        Args:
            id: Account ID
            display_name: New display name
            description: New description
            tier: New tier
            custom_fields: Custom fields to update

        Returns:
            The updated Account
        """
        request = AccountsUpdateRequest(
            id=id,
            display_name=display_name,
            description=description,
            tier=tier,
            custom_fields=custom_fields,
        )
        response = self._post("/accounts.update", request, AccountsUpdateResponse)
        return response.account

    def delete(self, id: str) -> None:
        """Delete an account.

        Args:
            id: Account ID to delete
        """
        request = AccountsDeleteRequest(id=id)
        self._post("/accounts.delete", request, AccountsDeleteResponse)

    def merge(self, primary_account: str, secondary_account: str) -> Account:
        """Merge two accounts.

        Args:
            primary_account: Primary account ID (will be retained)
            secondary_account: Secondary account ID (will be merged)

        Returns:
            The merged Account
        """
        request = AccountsMergeRequest(
            primary_account=primary_account,
            secondary_account=secondary_account,
        )
        response = self._post("/accounts.merge", request, AccountsMergeResponse)
        return response.account

    def export(
        self,
        *,
        created_by: Sequence[str] | None = None,
        first: int | None = None,
    ) -> Sequence[Account]:
        """Export accounts.

        Args:
            created_by: Filter by creator user IDs
            first: Maximum number of results

        Returns:
            List of exported accounts
        """
        request = AccountsExportRequest(
            created_by=created_by,
            first=first,
        )
        response = self._post("/accounts.export", request, AccountsExportResponse)
        return response.accounts


class AsyncAccountsService(AsyncBaseService):
    """Asynchronous service for managing DevRev accounts.

    Provides async methods for creating, reading, updating, and deleting accounts.

    Example:
        ```python
        from devrev import AsyncDevRevClient

        async with AsyncDevRevClient() as client:
            accounts = await client.accounts.list()
        ```
    """

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncAccountsService."""
        super().__init__(http_client)

    async def create(
        self,
        display_name: str,
        *,
        description: str | None = None,
        domains: list[str] | None = None,
        external_refs: list[str] | None = None,
        owned_by: list[str] | None = None,
        tier: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Account:
        """Create a new account."""
        request = AccountsCreateRequest(
            display_name=display_name,
            description=description,
            domains=domains,
            external_refs=external_refs,
            owned_by=owned_by,
            tier=tier,
            custom_fields=custom_fields,
        )
        response = await self._post("/accounts.create", request, AccountsCreateResponse)
        return response.account

    async def get(self, id: str) -> Account:
        """Get an account by ID."""
        request = AccountsGetRequest(id=id)
        response = await self._post("/accounts.get", request, AccountsGetResponse)
        return response.account

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        display_name: list[str] | None = None,
        domains: list[str] | None = None,
        owned_by: list[str] | None = None,
    ) -> AccountsListResponse:
        """List accounts."""
        request = AccountsListRequest(
            cursor=cursor,
            limit=limit,
            display_name=display_name,
            domains=domains,
            owned_by=owned_by,
        )
        return await self._post("/accounts.list", request, AccountsListResponse)

    async def update(
        self,
        id: str,
        *,
        display_name: str | None = None,
        description: str | None = None,
        tier: str | None = None,
        custom_fields: dict[str, Any] | None = None,
    ) -> Account:
        """Update an account."""
        request = AccountsUpdateRequest(
            id=id,
            display_name=display_name,
            description=description,
            tier=tier,
            custom_fields=custom_fields,
        )
        response = await self._post("/accounts.update", request, AccountsUpdateResponse)
        return response.account

    async def delete(self, id: str) -> None:
        """Delete an account."""
        request = AccountsDeleteRequest(id=id)
        await self._post("/accounts.delete", request, AccountsDeleteResponse)

    async def merge(self, primary_account: str, secondary_account: str) -> Account:
        """Merge two accounts."""
        request = AccountsMergeRequest(
            primary_account=primary_account,
            secondary_account=secondary_account,
        )
        response = await self._post("/accounts.merge", request, AccountsMergeResponse)
        return response.account

    async def export(
        self,
        *,
        created_by: Sequence[str] | None = None,
        first: int | None = None,
    ) -> Sequence[Account]:
        """Export accounts."""
        request = AccountsExportRequest(
            created_by=created_by,
            first=first,
        )
        response = await self._post("/accounts.export", request, AccountsExportResponse)
        return response.accounts
