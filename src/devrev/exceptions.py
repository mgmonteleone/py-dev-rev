"""DevRev SDK Exception Hierarchy.

All exceptions inherit from DevRevError, allowing users to catch
all SDK errors with a single except clause, or be more specific.

Exception Hierarchy:
    DevRevError (base)
    ├── AuthenticationError (401)
    ├── ForbiddenError (403)
    ├── NotFoundError (404)
    ├── ValidationError (400)
    ├── ConflictError (409)
    ├── RateLimitError (429)
    ├── ServerError (500)
    ├── ServiceUnavailableError (503)
    ├── ConfigurationError
    ├── TimeoutError
    └── NetworkError
"""

from typing import Any


class DevRevError(Exception):
    """Base exception for all DevRev SDK errors.

    All DevRev-specific exceptions inherit from this class,
    allowing users to catch all SDK errors with a single except clause.

    Attributes:
        message: Human-readable error description
        status_code: HTTP status code (if applicable)
        request_id: DevRev request ID for debugging
        response_body: Raw API response body
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        request_id: str | None = None,
        response_body: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: Human-readable error description
            status_code: HTTP status code (if applicable)
            request_id: DevRev request ID for support tickets
            response_body: Raw API response body for debugging
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.response_body = response_body

    def __str__(self) -> str:
        """Format error message with context."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


# HTTP Error Exceptions (mapped to status codes)


class AuthenticationError(DevRevError):
    """401 Unauthorized - Invalid or missing authentication.

    Raised when the API token is invalid, expired, or missing.
    """


class ForbiddenError(DevRevError):
    """403 Forbidden - Authenticated but not authorized.

    Raised when the user is authenticated but lacks permission
    to perform the requested action.
    """


class NotFoundError(DevRevError):
    """404 Not Found - Resource does not exist.

    Raised when the requested resource (account, work item, etc.)
    cannot be found.
    """


class ValidationError(DevRevError):
    """400 Bad Request - Invalid request parameters.

    Raised when the request contains invalid data or missing required fields.

    Attributes:
        field_errors: Mapping of field names to their validation errors
    """

    def __init__(
        self,
        message: str,
        *,
        field_errors: dict[str, list[str]] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Human-readable error description
            field_errors: Mapping of field names to their validation errors
            **kwargs: Additional arguments passed to DevRevError
        """
        super().__init__(message, **kwargs)
        self.field_errors = field_errors or {}


class ConflictError(DevRevError):
    """409 Conflict - Resource state conflict.

    Raised when the request conflicts with the current state
    of the resource (e.g., duplicate creation).
    """


class RateLimitError(DevRevError):
    """429 Too Many Requests - Rate limit exceeded.

    Raised when API rate limits are exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying
    """

    def __init__(
        self,
        message: str,
        *,
        retry_after: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Human-readable error description
            retry_after: Seconds to wait before retrying
            **kwargs: Additional arguments passed to DevRevError
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ServerError(DevRevError):
    """500 Internal Server Error - DevRev server error.

    Raised when DevRev's servers encounter an unexpected error.
    """


class ServiceUnavailableError(DevRevError):
    """503 Service Unavailable - Temporary service outage.

    Raised when the DevRev service is temporarily unavailable.
    """


# SDK-specific errors


class ConfigurationError(DevRevError):
    """SDK configuration error.

    Raised when the SDK is misconfigured (e.g., missing API key).
    """


class TimeoutError(DevRevError):
    """Request timed out.

    Raised when a request exceeds the configured timeout.
    """


class NetworkError(DevRevError):
    """Network connectivity error.

    Raised when there's a network-level failure (DNS, connection, etc.).
    """


class CircuitBreakerError(DevRevError):
    """Circuit breaker is open - service is unavailable.

    Raised when the circuit breaker pattern has opened due to
    repeated failures, preventing further requests until recovery.

    Attributes:
        recovery_timeout: Seconds until circuit breaker may allow requests
    """

    def __init__(
        self,
        message: str = "Circuit breaker is open - service temporarily unavailable",
        *,
        recovery_timeout: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize circuit breaker error.

        Args:
            message: Human-readable error description
            recovery_timeout: Seconds until circuit may close
            **kwargs: Additional arguments passed to DevRevError
        """
        super().__init__(message, **kwargs)
        self.recovery_timeout = recovery_timeout


# Status code to exception mapping for use in HTTP layer
STATUS_CODE_TO_EXCEPTION: dict[int, type[DevRevError]] = {
    400: ValidationError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    429: RateLimitError,
    500: ServerError,
    503: ServiceUnavailableError,
}
