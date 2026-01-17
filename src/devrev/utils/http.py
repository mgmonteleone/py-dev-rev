"""HTTP client utilities for DevRev SDK.

This module provides HTTP client implementations with retry logic,
rate limiting support, proper error handling, connection pooling,
and circuit breaker patterns for production reliability.
"""

from __future__ import annotations

import contextlib
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, TypeVar

import httpx

from devrev.exceptions import (
    STATUS_CODE_TO_EXCEPTION,
    CircuitBreakerError,
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

# Default connection pool configuration for optimal performance
DEFAULT_MAX_CONNECTIONS = 100
DEFAULT_MAX_KEEPALIVE_CONNECTIONS = 20
DEFAULT_KEEPALIVE_EXPIRY = 30.0  # seconds

# Circuit breaker defaults
DEFAULT_CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
DEFAULT_CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 30.0  # seconds
DEFAULT_CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS = 3


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern.

    Attributes:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Seconds to wait before testing recovery
        half_open_max_calls: Max calls allowed in half-open state
        enabled: Whether circuit breaker is enabled
    """

    failure_threshold: int = DEFAULT_CIRCUIT_BREAKER_FAILURE_THRESHOLD
    recovery_timeout: float = DEFAULT_CIRCUIT_BREAKER_RECOVERY_TIMEOUT
    half_open_max_calls: int = DEFAULT_CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS
    enabled: bool = True


@dataclass
class CircuitBreakerState:
    """Internal state for circuit breaker.

    Thread-safe state management for the circuit breaker pattern.
    """

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float = 0.0
    half_open_calls: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            self.failure_count = 0
            self.half_open_calls = 0
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker closed - service recovered")

    def record_failure(self, config: CircuitBreakerConfig) -> None:
        """Record a failed call."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning("Circuit breaker opened - failure in half-open state")
            elif self.failure_count >= config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(
                    "Circuit breaker opened - %d consecutive failures",
                    self.failure_count,
                )

    def can_execute(self, config: CircuitBreakerConfig) -> bool:
        """Check if a request can be executed."""
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True

            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has elapsed
                elapsed = time.monotonic() - self.last_failure_time
                if elapsed >= config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 1
                    logger.info("Circuit breaker half-open - testing recovery")
                    return True
                return False

            # HALF_OPEN state
            if self.half_open_calls < config.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False


@dataclass
class ConnectionPoolConfig:
    """Configuration for HTTP connection pooling.

    Optimizes connection reuse for better performance.

    Attributes:
        max_connections: Maximum total connections in pool
        max_keepalive_connections: Maximum idle connections to keep alive
        keepalive_expiry: Seconds before idle connection is closed
        http2: Whether to enable HTTP/2 support
    """

    max_connections: int = DEFAULT_MAX_CONNECTIONS
    max_keepalive_connections: int = DEFAULT_MAX_KEEPALIVE_CONNECTIONS
    keepalive_expiry: float = DEFAULT_KEEPALIVE_EXPIRY
    http2: bool = False


@dataclass
class TimeoutConfig:
    """Fine-grained timeout configuration.

    Attributes:
        connect: Timeout for establishing connection (seconds)
        read: Timeout for reading response (seconds)
        write: Timeout for sending request (seconds)
        pool: Timeout for acquiring connection from pool (seconds)
    """

    connect: float = 5.0
    read: float = 30.0
    write: float = 30.0
    pool: float = 10.0

    def to_httpx_timeout(self) -> httpx.Timeout:
        """Convert to httpx.Timeout object."""
        return httpx.Timeout(
            connect=self.connect,
            read=self.read,
            write=self.write,
            pool=self.pool,
        )

    @classmethod
    def from_total(cls, total: float) -> TimeoutConfig:
        """Create TimeoutConfig from a total timeout value.

        Args:
            total: Total timeout in seconds

        Returns:
            TimeoutConfig with distributed timeout values
        """
        return cls(
            connect=min(5.0, total / 6),
            read=total,
            write=total,
            pool=min(10.0, total / 3),
        )


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
    - Proper timeout handling with fine-grained control
    - Connection pooling for optimal performance
    - Circuit breaker pattern for reliability
    - ETag/conditional request support
    - Request/response logging

    Args:
        base_url: Base URL for all requests
        api_token: API authentication token
        timeout: Request timeout in seconds or TimeoutConfig
        max_retries: Maximum number of retry attempts
        pool_config: Connection pool configuration
        circuit_breaker_config: Circuit breaker configuration
    """

    def __init__(
        self,
        base_url: str,
        api_token: SecretStr,
        timeout: int | TimeoutConfig = 30,
        max_retries: int = DEFAULT_MAX_RETRIES,
        pool_config: ConnectionPoolConfig | None = None,
        circuit_breaker_config: CircuitBreakerConfig | None = None,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            base_url: Base URL for all requests
            api_token: API authentication token (SecretStr)
            timeout: Request timeout in seconds or TimeoutConfig for fine-grained control
            max_retries: Maximum number of retry attempts
            pool_config: Connection pool configuration for performance tuning
            circuit_breaker_config: Circuit breaker settings for reliability
        """
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._max_retries = max_retries

        # Configure timeout
        if isinstance(timeout, TimeoutConfig):
            self._timeout_config = timeout
            self._timeout = timeout.read  # Use read timeout as primary
        else:
            self._timeout_config = TimeoutConfig.from_total(float(timeout))
            self._timeout = timeout

        # Configure connection pool
        self._pool_config = pool_config or ConnectionPoolConfig()

        # Configure circuit breaker
        self._circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self._circuit_breaker_state = CircuitBreakerState()

        # ETag cache for conditional requests
        self._etag_cache: dict[str, str] = {}

        # Build the httpx client with optimized settings
        limits = httpx.Limits(
            max_connections=self._pool_config.max_connections,
            max_keepalive_connections=self._pool_config.max_keepalive_connections,
            keepalive_expiry=self._pool_config.keepalive_expiry,
        )

        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout_config.to_httpx_timeout(),
            headers=self._build_headers(),
            limits=limits,
            http2=self._pool_config.http2,
        )

    def _build_headers(self) -> dict[str, str]:
        """Build default headers for requests."""
        return {
            "Authorization": f"Bearer {self._api_token.get_secret_value()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "devrev-python-sdk/1.0.0",
        }

    @property
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is currently open."""
        return self._circuit_breaker_state.state == CircuitState.OPEN

    @property
    def circuit_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self._circuit_breaker_state.state

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> HTTPClient:
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""
        self.close()

    def _check_circuit_breaker(self) -> None:
        """Check if request is allowed by circuit breaker."""
        if not self._circuit_breaker_config.enabled:
            return

        if not self._circuit_breaker_state.can_execute(self._circuit_breaker_config):
            raise CircuitBreakerError(
                recovery_timeout=self._circuit_breaker_config.recovery_timeout
            )

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
        headers: dict[str, str] | None = None,
        use_etag: bool = True,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic and circuit breaker.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: JSON body for the request
            params: Query parameters
            headers: Additional headers to include
            use_etag: Whether to use ETag caching for GET requests

        Returns:
            HTTP response object

        Raises:
            DevRevError: On API errors
            TimeoutError: On request timeout
            NetworkError: On network failures
            CircuitBreakerError: If circuit breaker is open
        """
        # Check circuit breaker
        self._check_circuit_breaker()

        url = f"{self._base_url}{endpoint}"
        last_exception: Exception | None = None

        # Prepare headers with ETag support
        request_headers = dict(headers) if headers else {}
        # Include params in cache key to avoid ETag collisions for different query params
        params_str = "&".join(f"{k}={v}" for k, v in sorted(params.items())) if params else ""
        cache_key = f"{method}:{endpoint}?{params_str}" if params_str else f"{method}:{endpoint}"

        if use_etag and method == "GET" and cache_key in self._etag_cache:
            request_headers["If-None-Match"] = self._etag_cache[cache_key]

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
                    headers=request_headers if request_headers else None,
                )

                if response.is_success:
                    # Record success for circuit breaker
                    self._circuit_breaker_state.record_success()

                    # Cache ETag if present
                    etag = response.headers.get("etag")
                    if etag and method == "GET":
                        self._etag_cache[cache_key] = etag

                    return response

                # Handle 304 Not Modified - return a synthetic 200 response
                # to avoid downstream callers failing on response.json()
                if response.status_code == 304:
                    self._circuit_breaker_state.record_success()
                    # Return a 200 response with empty body for 304
                    # This allows callers to handle it uniformly
                    return httpx.Response(
                        status_code=200,
                        headers=response.headers,
                        json={"_not_modified": True},
                        request=response.request,
                    )

                if not self._should_retry(response) or attempt >= self._max_retries:
                    self._circuit_breaker_state.record_failure(self._circuit_breaker_config)
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
                    self._circuit_breaker_state.record_failure(self._circuit_breaker_config)
                    raise TimeoutError(
                        f"Request to {endpoint} timed out after {self._timeout}s"
                    ) from e
                wait_time = self._handle_retry(attempt, _exception=e)
                logger.warning("Request timeout, retrying in %.2fs", wait_time)
                time.sleep(wait_time)

            except httpx.RequestError as e:
                last_exception = e
                if attempt >= self._max_retries:
                    self._circuit_breaker_state.record_failure(self._circuit_breaker_config)
                    raise NetworkError(f"Network error connecting to {url}: {e}") from e
                wait_time = self._handle_retry(attempt, _exception=e)
                logger.warning("Network error, retrying in %.2fs", wait_time)
                time.sleep(wait_time)

        # Should not reach here, but just in case
        self._circuit_breaker_state.record_failure(self._circuit_breaker_config)
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
        return self.request("POST", endpoint, json=data, use_etag=False)

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

    def health_check(self, timeout: float = 5.0) -> bool:
        """Perform a health check on the API.

        Attempts a lightweight request to verify connectivity
        and service availability.

        Args:
            timeout: Timeout for the health check request

        Returns:
            True if the API is healthy, False otherwise
        """
        if self.is_circuit_open:
            logger.debug("Health check skipped - circuit breaker is open")
            return False

        try:
            # Use a dedicated timeout for health checks without mutating client state
            # Use relative path without leading slash to properly join with base_url
            response = self._client.get("health", timeout=httpx.Timeout(timeout))

            return response.is_success or response.status_code == 404

        except Exception as e:
            logger.debug("Health check failed: %s", str(e))
            return False

    def clear_etag_cache(self) -> None:
        """Clear the ETag cache."""
        self._etag_cache.clear()

    def reset_circuit_breaker(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        with self._circuit_breaker_state._lock:
            self._circuit_breaker_state.state = CircuitState.CLOSED
            self._circuit_breaker_state.failure_count = 0
            self._circuit_breaker_state.half_open_calls = 0
        logger.info("Circuit breaker manually reset")


class AsyncHTTPClient:
    """Asynchronous HTTP client with retry logic and rate limiting support.

    This client wraps httpx and provides:
    - Automatic retry with exponential backoff
    - Rate limiting support with Retry-After header
    - Proper timeout handling with fine-grained control
    - Connection pooling for optimal performance
    - Circuit breaker pattern for reliability
    - ETag/conditional request support
    - Request/response logging

    Args:
        base_url: Base URL for all requests
        api_token: API authentication token
        timeout: Request timeout in seconds or TimeoutConfig
        max_retries: Maximum number of retry attempts
        pool_config: Connection pool configuration
        circuit_breaker_config: Circuit breaker configuration
    """

    def __init__(
        self,
        base_url: str,
        api_token: SecretStr,
        timeout: int | TimeoutConfig = 30,
        max_retries: int = DEFAULT_MAX_RETRIES,
        pool_config: ConnectionPoolConfig | None = None,
        circuit_breaker_config: CircuitBreakerConfig | None = None,
    ) -> None:
        """Initialize the async HTTP client.

        Args:
            base_url: Base URL for all requests
            api_token: API authentication token (SecretStr)
            timeout: Request timeout in seconds or TimeoutConfig for fine-grained control
            max_retries: Maximum number of retry attempts
            pool_config: Connection pool configuration for performance tuning
            circuit_breaker_config: Circuit breaker settings for reliability
        """
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._max_retries = max_retries

        # Configure timeout
        if isinstance(timeout, TimeoutConfig):
            self._timeout_config = timeout
            self._timeout = timeout.read
        else:
            self._timeout_config = TimeoutConfig.from_total(float(timeout))
            self._timeout = timeout

        # Configure connection pool
        self._pool_config = pool_config or ConnectionPoolConfig()

        # Configure circuit breaker
        self._circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self._circuit_breaker_state = CircuitBreakerState()

        # ETag cache for conditional requests
        self._etag_cache: dict[str, str] = {}

        # Build the httpx client with optimized settings
        limits = httpx.Limits(
            max_connections=self._pool_config.max_connections,
            max_keepalive_connections=self._pool_config.max_keepalive_connections,
            keepalive_expiry=self._pool_config.keepalive_expiry,
        )

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout_config.to_httpx_timeout(),
            headers=self._build_headers(),
            limits=limits,
            http2=self._pool_config.http2,
        )

    def _build_headers(self) -> dict[str, str]:
        """Build default headers for requests."""
        return {
            "Authorization": f"Bearer {self._api_token.get_secret_value()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "devrev-python-sdk/1.0.0",
        }

    @property
    def is_circuit_open(self) -> bool:
        """Check if circuit breaker is currently open."""
        return self._circuit_breaker_state.state == CircuitState.OPEN

    @property
    def circuit_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self._circuit_breaker_state.state

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHTTPClient:
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager."""
        await self.close()

    def _check_circuit_breaker(self) -> None:
        """Check if request is allowed by circuit breaker."""
        if not self._circuit_breaker_config.enabled:
            return

        if not self._circuit_breaker_state.can_execute(self._circuit_breaker_config):
            raise CircuitBreakerError(
                recovery_timeout=self._circuit_breaker_config.recovery_timeout
            )

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
        headers: dict[str, str] | None = None,
        use_etag: bool = True,
    ) -> httpx.Response:
        """Make an async HTTP request with retry logic and circuit breaker.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            json: JSON body for the request
            params: Query parameters
            headers: Additional headers to include
            use_etag: Whether to use ETag caching for GET requests

        Returns:
            HTTP response object

        Raises:
            DevRevError: On API errors
            TimeoutError: On request timeout
            NetworkError: On network failures
            CircuitBreakerError: If circuit breaker is open
        """
        import asyncio

        # Check circuit breaker
        self._check_circuit_breaker()

        url = f"{self._base_url}{endpoint}"
        last_exception: Exception | None = None

        # Prepare headers with ETag support
        request_headers = dict(headers) if headers else {}
        # Include params in cache key to avoid ETag collisions for different query params
        params_str = "&".join(f"{k}={v}" for k, v in sorted(params.items())) if params else ""
        cache_key = f"{method}:{endpoint}?{params_str}" if params_str else f"{method}:{endpoint}"

        if use_etag and method == "GET" and cache_key in self._etag_cache:
            request_headers["If-None-Match"] = self._etag_cache[cache_key]

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
                    headers=request_headers if request_headers else None,
                )

                if response.is_success:
                    # Record success for circuit breaker
                    self._circuit_breaker_state.record_success()

                    # Cache ETag if present
                    etag = response.headers.get("etag")
                    if etag and method == "GET":
                        self._etag_cache[cache_key] = etag

                    return response

                # Handle 304 Not Modified - return a synthetic 200 response
                # to avoid downstream callers failing on response.json()
                if response.status_code == 304:
                    self._circuit_breaker_state.record_success()
                    # Return a 200 response with empty body for 304
                    # This allows callers to handle it uniformly
                    return httpx.Response(
                        status_code=200,
                        headers=response.headers,
                        json={"_not_modified": True},
                        request=response.request,
                    )

                if not self._should_retry(response) or attempt >= self._max_retries:
                    self._circuit_breaker_state.record_failure(self._circuit_breaker_config)
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
                    self._circuit_breaker_state.record_failure(self._circuit_breaker_config)
                    raise TimeoutError(
                        f"Request to {endpoint} timed out after {self._timeout}s"
                    ) from e
                wait_time = self._handle_retry(attempt, _exception=e)
                logger.warning("Request timeout, retrying in %.2fs", wait_time)
                await asyncio.sleep(wait_time)

            except httpx.RequestError as e:
                last_exception = e
                if attempt >= self._max_retries:
                    self._circuit_breaker_state.record_failure(self._circuit_breaker_config)
                    raise NetworkError(f"Network error connecting to {url}: {e}") from e
                wait_time = self._handle_retry(attempt, _exception=e)
                logger.warning("Network error, retrying in %.2fs", wait_time)
                await asyncio.sleep(wait_time)

        self._circuit_breaker_state.record_failure(self._circuit_breaker_config)
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
        return await self.request("POST", endpoint, json=data, use_etag=False)

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

    async def health_check(self, timeout: float = 5.0) -> bool:
        """Perform an async health check on the API.

        Args:
            timeout: Timeout for the health check request

        Returns:
            True if the API is healthy, False otherwise
        """
        if self.is_circuit_open:
            logger.debug("Health check skipped - circuit breaker is open")
            return False

        try:
            # Use relative path without leading slash to properly join with base_url
            response = await self._client.get("health", timeout=httpx.Timeout(timeout))
            return response.is_success or response.status_code == 404
        except Exception as e:
            logger.debug("Health check failed: %s", str(e))
            return False

    def clear_etag_cache(self) -> None:
        """Clear the ETag cache."""
        self._etag_cache.clear()

    def reset_circuit_breaker(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        with self._circuit_breaker_state._lock:
            self._circuit_breaker_state.state = CircuitState.CLOSED
            self._circuit_breaker_state.failure_count = 0
            self._circuit_breaker_state.half_open_calls = 0
        logger.info("Circuit breaker manually reset")
