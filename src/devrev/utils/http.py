"""HTTP client utilities for DevRev SDK.

This module provides HTTP client implementations with retry logic,
rate limiting support, and proper error handling.
"""

from __future__ import annotations

import contextlib
import logging
import time
from typing import TYPE_CHECKING, Any, TypeVar

import httpx

from devrev.exceptions import (
    STATUS_CODE_TO_EXCEPTION,
    DevRevError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)

if TYPE_CHECKING:
    from pydantic import SecretStr

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF_FACTOR = 0.5
DEFAULT_RETRY_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def _calculate_backoff(attempt: int, backoff_factor: float = DEFAULT_RETRY_BACKOFF_FACTOR) -> float:
    """Calculate exponential backoff delay.

    Args:
        attempt: Current retry attempt (0-indexed)
        backoff_factor: Base factor for exponential calculation

    Returns:
        Delay in seconds before next retry
    """
    return float(backoff_factor * (2**attempt))


def _extract_error_message(response: httpx.Response) -> tuple[str, dict[str, Any] | None]:
    """Extract error message from API response.

    Args:
        response: HTTP response object

    Returns:
        Tuple of (error message, response body dict or None)
    """
    try:
        body = response.json()
        message = body.get("message") or body.get("error") or f"HTTP {response.status_code}"
        return message, body
    except Exception:
        return f"HTTP {response.status_code}: {response.text[:200]}", None


def _raise_for_status(response: httpx.Response) -> None:
    """Raise appropriate DevRev exception based on response status code.

    Args:
        response: HTTP response object

    Raises:
        DevRevError: Appropriate subclass based on status code
    """
    if response.is_success:
        return

    message, body = _extract_error_message(response)
    request_id = response.headers.get("x-request-id")

    exception_class = STATUS_CODE_TO_EXCEPTION.get(response.status_code, DevRevError)

    # Handle rate limiting specially
    if response.status_code == 429:
        retry_after = None
        retry_header = response.headers.get("retry-after")
        if retry_header:
            with contextlib.suppress(ValueError):
                retry_after = int(retry_header)
        raise RateLimitError(
            message,
            status_code=response.status_code,
            request_id=request_id,
            response_body=body,
            retry_after=retry_after,
        )

    raise exception_class(
        message,
        status_code=response.status_code,
        request_id=request_id,
        response_body=body,
    )


class HTTPClient:
    """Synchronous HTTP client with retry logic and rate limiting support.

    This client wraps httpx and provides:
    - Automatic retry with exponential backoff
    - Rate limiting support with Retry-After header
    - Proper timeout handling
    - Request/response logging

    Args:
        base_url: Base URL for all requests
        api_token: API authentication token
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    """

    def __init__(
        self,
        base_url: str,
        api_token: SecretStr,
        timeout: int = 30,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            base_url: Base URL for all requests
            api_token: API authentication token (SecretStr)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout),
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build default headers for requests."""
        return {
            "Authorization": f"Bearer {self._api_token.get_secret_value()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "devrev-python-sdk/0.1.0",
        }

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> HTTPClient:
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""
        self.close()

    def _should_retry(self, response: httpx.Response) -> bool:
        """Determine if request should be retried based on response.

        Args:
            response: HTTP response object

        Returns:
            True if request should be retried
        """
        return response.status_code in DEFAULT_RETRY_STATUS_CODES

    def _handle_retry(
        self,
        attempt: int,
        response: httpx.Response | None = None,
        _exception: Exception | None = None,
    ) -> float:
        """Handle retry logic and return wait time.

        Args:
            attempt: Current retry attempt
            response: HTTP response (if available)
            _exception: Exception that occurred (if any, unused but kept for interface)

        Returns:
            Seconds to wait before next retry
        """
        if response is not None and response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass

        return _calculate_backoff(attempt)

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: JSON body for the request
            params: Query parameters

        Returns:
            HTTP response object

        Raises:
            DevRevError: On API errors
            TimeoutError: On request timeout
            NetworkError: On network failures
        """
        url = f"{self._base_url}{endpoint}"
        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                logger.debug(
                    "Making %s request to %s (attempt %d/%d)",
                    method,
                    endpoint,
                    attempt + 1,
                    self._max_retries + 1,
                )

                response = self._client.request(
                    method=method,
                    url=endpoint,
                    json=json,
                    params=params,
                )

                if response.is_success:
                    return response

                if not self._should_retry(response) or attempt >= self._max_retries:
                    _raise_for_status(response)

                wait_time = self._handle_retry(attempt, response=response)
                logger.warning(
                    "Request to %s failed with status %d, retrying in %.2fs",
                    endpoint,
                    response.status_code,
                    wait_time,
                )
                time.sleep(wait_time)

            except httpx.TimeoutException as e:
                last_exception = e
                if attempt >= self._max_retries:
                    raise TimeoutError(
                        f"Request to {endpoint} timed out after {self._timeout}s"
                    ) from e
                wait_time = self._handle_retry(attempt, _exception=e)
                logger.warning("Request timeout, retrying in %.2fs", wait_time)
                time.sleep(wait_time)

            except httpx.RequestError as e:
                last_exception = e
                if attempt >= self._max_retries:
                    raise NetworkError(f"Network error connecting to {url}: {e}") from e
                wait_time = self._handle_retry(attempt, _exception=e)
                logger.warning("Network error, retrying in %.2fs", wait_time)
                time.sleep(wait_time)

        # Should not reach here, but just in case
        if last_exception:
            raise NetworkError(
                f"Request failed after {self._max_retries + 1} attempts"
            ) from last_exception
        raise DevRevError("Request failed unexpectedly")

    def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a POST request.

        Args:
            endpoint: API endpoint path
            data: JSON body for the request

        Returns:
            HTTP response object
        """
        return self.request("POST", endpoint, json=data)

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            HTTP response object
        """
        return self.request("GET", endpoint, params=params)


class AsyncHTTPClient:
    """Asynchronous HTTP client with retry logic and rate limiting support.

    This client wraps httpx and provides:
    - Automatic retry with exponential backoff
    - Rate limiting support with Retry-After header
    - Proper timeout handling
    - Request/response logging

    Args:
        base_url: Base URL for all requests
        api_token: API authentication token
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    """

    def __init__(
        self,
        base_url: str,
        api_token: SecretStr,
        timeout: int = 30,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize the async HTTP client.

        Args:
            base_url: Base URL for all requests
            api_token: API authentication token (SecretStr)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._timeout = timeout
        self._max_retries = max_retries
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(timeout),
            headers=self._build_headers(),
        )

    def _build_headers(self) -> dict[str, str]:
        """Build default headers for requests."""
        return {
            "Authorization": f"Bearer {self._api_token.get_secret_value()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "devrev-python-sdk/0.1.0",
        }

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHTTPClient:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.close()

    def _should_retry(self, response: httpx.Response) -> bool:
        """Determine if request should be retried based on response."""
        return response.status_code in DEFAULT_RETRY_STATUS_CODES

    def _handle_retry(
        self,
        attempt: int,
        response: httpx.Response | None = None,
        _exception: Exception | None = None,
    ) -> float:
        """Handle retry logic and return wait time."""
        if response is not None and response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass

        return _calculate_backoff(attempt)

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make an async HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: JSON body for the request
            params: Query parameters

        Returns:
            HTTP response object

        Raises:
            DevRevError: On API errors
            TimeoutError: On request timeout
            NetworkError: On network failures
        """
        import asyncio

        url = f"{self._base_url}{endpoint}"
        last_exception: Exception | None = None

        for attempt in range(self._max_retries + 1):
            try:
                logger.debug(
                    "Making async %s request to %s (attempt %d/%d)",
                    method,
                    endpoint,
                    attempt + 1,
                    self._max_retries + 1,
                )

                response = await self._client.request(
                    method=method,
                    url=endpoint,
                    json=json,
                    params=params,
                )

                if response.is_success:
                    return response

                if not self._should_retry(response) or attempt >= self._max_retries:
                    _raise_for_status(response)

                wait_time = self._handle_retry(attempt, response=response)
                logger.warning(
                    "Request to %s failed with status %d, retrying in %.2fs",
                    endpoint,
                    response.status_code,
                    wait_time,
                )
                await asyncio.sleep(wait_time)

            except httpx.TimeoutException as e:
                last_exception = e
                if attempt >= self._max_retries:
                    raise TimeoutError(
                        f"Request to {endpoint} timed out after {self._timeout}s"
                    ) from e
                wait_time = self._handle_retry(attempt, _exception=e)
                logger.warning("Request timeout, retrying in %.2fs", wait_time)
                await asyncio.sleep(wait_time)

            except httpx.RequestError as e:
                last_exception = e
                if attempt >= self._max_retries:
                    raise NetworkError(f"Network error connecting to {url}: {e}") from e
                wait_time = self._handle_retry(attempt, _exception=e)
                logger.warning("Network error, retrying in %.2fs", wait_time)
                await asyncio.sleep(wait_time)

        if last_exception:
            raise NetworkError(
                f"Request failed after {self._max_retries + 1} attempts"
            ) from last_exception
        raise DevRevError("Request failed unexpectedly")

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make an async POST request.

        Args:
            endpoint: API endpoint path
            data: JSON body for the request

        Returns:
            HTTP response object
        """
        return await self.request("POST", endpoint, json=data)

    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make an async GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            HTTP response object
        """
        return await self.request("GET", endpoint, params=params)
