"""UOMs service for DevRev SDK.

This module provides the UomsService for managing DevRev UOMs (Units of Measure).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from devrev.models.uoms import (
    Uom,
    UomAggregationType,
    UomMetricScope,
    UomsCountRequest,
    UomsCountResponse,
    UomsCreateRequest,
    UomsCreateResponse,
    UomsDeleteRequest,
    UomsDeleteResponse,
    UomsGetRequest,
    UomsGetResponse,
    UomsListRequest,
    UomsListResponse,
    UomsUpdateRequest,
    UomsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.utils.http import AsyncHTTPClient, HTTPClient


class UomsService(BaseService):
    """Synchronous service for managing DevRev UOMs.

    Provides methods for creating, reading, updating, and deleting UOMs.

    Example:
        ```python
        from devrev import DevRevClient

        client = DevRevClient()
        uoms = client.uoms.list()
        ```
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the UomsService."""
        super().__init__(http_client)

    def create(
        self,
        name: str,
        aggregation_type: UomAggregationType,
        *,
        description: str | None = None,
        metric_scope: UomMetricScope | None = None,
        dimensions: list[str] | None = None,
        part: str | None = None,
        product: str | None = None,
        is_enabled: bool = True,
    ) -> Uom:
        """Create a new UOM.

        Args:
            name: UOM name
            aggregation_type: Aggregation type
            description: UOM description
            metric_scope: Metric scope
            dimensions: Dimensions
            part: Associated part ID
            product: Associated product ID
            is_enabled: Whether UOM is enabled

        Returns:
            The created Uom
        """
        request = UomsCreateRequest(
            name=name,
            aggregation_type=aggregation_type,
            description=description,
            metric_scope=metric_scope,
            dimensions=dimensions,
            part=part,
            product=product,
            is_enabled=is_enabled,
        )
        response = self._post("/uoms.create", request, UomsCreateResponse)
        return response.uom

    def get(self, id: str) -> Uom:
        """Get a UOM by ID.

        Args:
            id: UOM ID

        Returns:
            The Uom
        """
        request = UomsGetRequest(id=id)
        response = self._post("/uoms.get", request, UomsGetResponse)
        return response.uom

    def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        aggregation_type: list[UomAggregationType] | None = None,
        is_enabled: bool | None = None,
    ) -> UomsListResponse:
        """List UOMs.

        Args:
            cursor: Pagination cursor
            limit: Maximum number of results
            aggregation_type: Filter by aggregation types
            is_enabled: Filter by enabled status

        Returns:
            Paginated list of UOMs
        """
        request = UomsListRequest(
            cursor=cursor,
            limit=limit,
            aggregation_type=aggregation_type,
            is_enabled=is_enabled,
        )
        return self._post("/uoms.list", request, UomsListResponse)

    def update(
        self,
        id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        is_enabled: bool | None = None,
    ) -> Uom:
        """Update a UOM.

        Args:
            id: UOM ID
            name: New UOM name
            description: New description
            is_enabled: New enabled status

        Returns:
            The updated Uom
        """
        request = UomsUpdateRequest(
            id=id,
            name=name,
            description=description,
            is_enabled=is_enabled,
        )
        response = self._post("/uoms.update", request, UomsUpdateResponse)
        return response.uom

    def delete(self, id: str) -> None:
        """Delete a UOM.

        Args:
            id: UOM ID to delete
        """
        request = UomsDeleteRequest(id=id)
        self._post("/uoms.delete", request, UomsDeleteResponse)

    def count(
        self,
        *,
        aggregation_type: list[UomAggregationType] | None = None,
        is_enabled: bool | None = None,
    ) -> int:
        """Count UOMs.

        Args:
            aggregation_type: Filter by aggregation types
            is_enabled: Filter by enabled status

        Returns:
            Count of UOMs
        """
        request = UomsCountRequest(
            aggregation_type=aggregation_type,
            is_enabled=is_enabled,
        )
        response = self._post("/uoms.count", request, UomsCountResponse)
        return response.count


class AsyncUomsService(AsyncBaseService):
    """Asynchronous service for managing DevRev UOMs.

    Provides async methods for creating, reading, updating, and deleting UOMs.

    Example:
        ```python
        from devrev import AsyncDevRevClient

        async with AsyncDevRevClient() as client:
            uoms = await client.uoms.list()
        ```
    """

    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """Initialize the AsyncUomsService."""
        super().__init__(http_client)

    async def create(
        self,
        name: str,
        aggregation_type: UomAggregationType,
        *,
        description: str | None = None,
        metric_scope: UomMetricScope | None = None,
        dimensions: list[str] | None = None,
        part: str | None = None,
        product: str | None = None,
        is_enabled: bool = True,
    ) -> Uom:
        """Create a new UOM."""
        request = UomsCreateRequest(
            name=name,
            aggregation_type=aggregation_type,
            description=description,
            metric_scope=metric_scope,
            dimensions=dimensions,
            part=part,
            product=product,
            is_enabled=is_enabled,
        )
        response = await self._post("/uoms.create", request, UomsCreateResponse)
        return response.uom

    async def get(self, id: str) -> Uom:
        """Get a UOM by ID."""
        request = UomsGetRequest(id=id)
        response = await self._post("/uoms.get", request, UomsGetResponse)
        return response.uom

    async def list(
        self,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        aggregation_type: list[UomAggregationType] | None = None,
        is_enabled: bool | None = None,
    ) -> UomsListResponse:
        """List UOMs."""
        request = UomsListRequest(
            cursor=cursor,
            limit=limit,
            aggregation_type=aggregation_type,
            is_enabled=is_enabled,
        )
        return await self._post("/uoms.list", request, UomsListResponse)

    async def update(
        self,
        id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        is_enabled: bool | None = None,
    ) -> Uom:
        """Update a UOM."""
        request = UomsUpdateRequest(
            id=id,
            name=name,
            description=description,
            is_enabled=is_enabled,
        )
        response = await self._post("/uoms.update", request, UomsUpdateResponse)
        return response.uom

    async def delete(self, id: str) -> None:
        """Delete a UOM."""
        request = UomsDeleteRequest(id=id)
        await self._post("/uoms.delete", request, UomsDeleteResponse)

    async def count(
        self,
        *,
        aggregation_type: list[UomAggregationType] | None = None,
        is_enabled: bool | None = None,
    ) -> int:
        """Count UOMs."""
        request = UomsCountRequest(
            aggregation_type=aggregation_type,
            is_enabled=is_enabled,
        )
        response = await self._post("/uoms.count", request, UomsCountResponse)
        return response.count

