"""Base service class for DevRev SDK.

This module provides the base service class that all API services inherit from.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, TypeVar, overload

from pydantic import BaseModel

if TYPE_CHECKING:
    from devrev.client import AsyncDevRevClient, DevRevClient
    from devrev.utils.http import AsyncHTTPClient, HTTPClient

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class BaseService:
    """Base class for synchronous DevRev API services.

    Provides common functionality for making API requests
    and parsing responses into Pydantic models.

    Args:
        http_client: The HTTP client to use for requests
        parent_client: Optional reference to parent DevRevClient for cross-service access
    """

    def __init__(
        self, http_client: HTTPClient, parent_client: DevRevClient | None = None
    ) -> None:
        """Initialize the service.

        Args:
            http_client: The HTTP client to use for requests
            parent_client: Optional reference to parent DevRevClient for cross-service access
        """
        self._http = http_client
        self._parent_client = parent_client

    @overload
    def _post(
        self,
        endpoint: str,
        request: BaseModel | None,
        response_type: type[T],
    ) -> T: ...

    @overload
    def _post(
        self,
        endpoint: str,
        request: BaseModel | None = None,
        response_type: None = None,
    ) -> dict[str, Any]: ...

    def _post(
        self,
        endpoint: str,
        request: BaseModel | None = None,
        response_type: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Make a POST request and parse the response.

        Args:
            endpoint: API endpoint path
            request: Request model to serialize as JSON body
            response_type: Response model type to parse into

        Returns:
            Parsed response model or raw dict if no response_type
        """
        data = request.model_dump(exclude_none=True, by_alias=True) if request else None
        response = self._http.post(endpoint, data=data)

        # Handle empty responses (204 No Content or empty body)
        if response.status_code == 204 or not response.content:
            json_data: dict[str, Any] = {}
        else:
            json_data = response.json()

        if response_type:
            return response_type.model_validate(json_data)
        return json_data

    @overload
    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None,
        response_type: type[T],
    ) -> T: ...

    @overload
    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        response_type: None = None,
    ) -> dict[str, Any]: ...

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        response_type: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Make a GET request and parse the response.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            response_type: Response model type to parse into

        Returns:
            Parsed response model or raw dict if no response_type
        """
        response = self._http.get(endpoint, params=params)

        # Handle empty responses (204 No Content or empty body)
        if response.status_code == 204 or not response.content:
            json_data: dict[str, Any] = {}
        else:
            json_data = response.json()

        if response_type:
            return response_type.model_validate(json_data)
        return json_data


class AsyncBaseService:
    """Base class for asynchronous DevRev API services.

    Provides common functionality for making async API requests
    and parsing responses into Pydantic models.

    Args:
        http_client: The async HTTP client to use for requests
        parent_client: Optional reference to parent AsyncDevRevClient for cross-service access
    """

    def __init__(
        self, http_client: AsyncHTTPClient, parent_client: AsyncDevRevClient | None = None
    ) -> None:
        """Initialize the service.

        Args:
            http_client: The async HTTP client to use for requests
            parent_client: Optional reference to parent AsyncDevRevClient for cross-service access
        """
        self._http = http_client
        self._parent_client = parent_client

    @overload
    async def _post(
        self,
        endpoint: str,
        request: BaseModel | None,
        response_type: type[T],
    ) -> T: ...

    @overload
    async def _post(
        self,
        endpoint: str,
        request: BaseModel | None = None,
        response_type: None = None,
    ) -> dict[str, Any]: ...

    async def _post(
        self,
        endpoint: str,
        request: BaseModel | None = None,
        response_type: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Make an async POST request and parse the response.

        Args:
            endpoint: API endpoint path
            request: Request model to serialize as JSON body
            response_type: Response model type to parse into

        Returns:
            Parsed response model or raw dict if no response_type
        """
        data = request.model_dump(exclude_none=True, by_alias=True) if request else None
        response = await self._http.post(endpoint, data=data)

        # Handle empty responses (204 No Content or empty body)
        if response.status_code == 204 or not response.content:
            json_data: dict[str, Any] = {}
        else:
            json_data = response.json()

        if response_type:
            return response_type.model_validate(json_data)
        return json_data

    @overload
    async def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None,
        response_type: type[T],
    ) -> T: ...

    @overload
    async def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        response_type: None = None,
    ) -> dict[str, Any]: ...

    async def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        response_type: type[T] | None = None,
    ) -> T | dict[str, Any]:
        """Make an async GET request and parse the response.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            response_type: Response model type to parse into

        Returns:
            Parsed response model or raw dict if no response_type
        """
        response = await self._http.get(endpoint, params=params)

        # Handle empty responses (204 No Content or empty body)
        if response.status_code == 204 or not response.content:
            json_data: dict[str, Any] = {}
        else:
            json_data = response.json()

        if response_type:
            return response_type.model_validate(json_data)
        return json_data
