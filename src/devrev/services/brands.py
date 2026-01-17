"""Brands service for DevRev SDK.

This module provides the BrandsService for managing DevRev brands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from devrev.models.brands import (
    Brand,
    BrandsCreateRequest,
    BrandsCreateResponse,
    BrandsDeleteRequest,
    BrandsDeleteResponse,
    BrandsGetRequest,
    BrandsGetResponse,
    BrandsListRequest,
    BrandsListResponse,
    BrandsUpdateRequest,
    BrandsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class BrandsService(BaseService):
    """Synchronous service for managing DevRev brands.

    Provides methods for creating, reading, updating, and deleting brands.

    Example:
        ```python
        from devrev import DevRevClient

        client = DevRevClient()
        brands = client.brands.list()
        ```
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the BrandsService."""
        super().__init__(http_client)

    def create(
        self,
        name: str,
        *,
        description: str | None = None,
        logo_url: str | None = None,
    ) -> Brand:
        """Create a new brand.

        Args:
            name: Brand name
            description: Brand description
            logo_url: Brand logo URL

        Returns:
            The created Brand
        """
        request = BrandsCreateRequest(
            name=name,
            description=description,
            logo_url=logo_url,
        )
        response = self._post("/brands.create", request, BrandsCreateResponse)
        return response.brand

    def get(self, id: str) -> Brand:
        """Get a brand by ID.

        Args:
            id: Brand ID

        Returns:
            The Brand
        """
        request = BrandsGetRequest(id=id)
        response = self._post("/brands.get", request, BrandsGetResponse)
        return response.brand

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> BrandsListResponse:
        """List brands.

        Args:
            cursor: Pagination cursor
            limit: Maximum number of results

        Returns:
            Paginated list of brands
        """
        request = BrandsListRequest(
            cursor=cursor,
            limit=limit,
        )
        return self._post("/brands.list", request, BrandsListResponse)

    def update(
        self,
        id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
    ) -> Brand:
        """Update a brand.

        Args:
            id: Brand ID
            name: New brand name
            description: New description
            logo_url: New logo URL

        Returns:
            The updated Brand
        """
        request = BrandsUpdateRequest(
            id=id,
            name=name,
            description=description,
            logo_url=logo_url,
        )
        response = self._post("/brands.update", request, BrandsUpdateResponse)
        return response.brand

    def delete(self, id: str) -> None:
        """Delete a brand.

        Args:
            id: Brand ID to delete
        """
        request = BrandsDeleteRequest(id=id)
        self._post("/brands.delete", request, BrandsDeleteResponse)


class AsyncBrandsService(AsyncBaseService):
    """Asynchronous service for managing DevRev brands.

    Provides async methods for creating, reading, updating, and deleting brands.

    Example:
        ```python
        from devrev import AsyncDevRevClient

        async with AsyncDevRevClient() as client:
            brands = await client.brands.list()
        ```
    """

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncBrandsService."""
        super().__init__(http_client)

    async def create(
        self,
        name: str,
        *,
        description: str | None = None,
        logo_url: str | None = None,
    ) -> Brand:
        """Create a new brand."""
        request = BrandsCreateRequest(
            name=name,
            description=description,
            logo_url=logo_url,
        )
        response = await self._post("/brands.create", request, BrandsCreateResponse)
        return response.brand

    async def get(self, id: str) -> Brand:
        """Get a brand by ID."""
        request = BrandsGetRequest(id=id)
        response = await self._post("/brands.get", request, BrandsGetResponse)
        return response.brand

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> BrandsListResponse:
        """List brands."""
        request = BrandsListRequest(
            cursor=cursor,
            limit=limit,
        )
        return await self._post("/brands.list", request, BrandsListResponse)

    async def update(
        self,
        id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        logo_url: str | None = None,
    ) -> Brand:
        """Update a brand."""
        request = BrandsUpdateRequest(
            id=id,
            name=name,
            description=description,
            logo_url=logo_url,
        )
        response = await self._post("/brands.update", request, BrandsUpdateResponse)
        return response.brand

    async def delete(self, id: str) -> None:
        """Delete a brand."""
        request = BrandsDeleteRequest(id=id)
        await self._post("/brands.delete", request, BrandsDeleteResponse)
