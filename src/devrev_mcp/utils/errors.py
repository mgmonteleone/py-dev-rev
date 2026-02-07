"""Error handling utilities for DevRev MCP tools."""

from __future__ import annotations

from devrev.exceptions import (
    AuthenticationError,
    BetaAPIRequiredError,
    ConflictError,
    DevRevError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
)
from devrev.exceptions import (
    TimeoutError as DevRevTimeoutError,
)
from devrev.exceptions import (
    ValidationError as DevRevValidationError,
)


def format_devrev_error(error: DevRevError) -> str:
    """Format a DevRev SDK error into a user-friendly message.

    Args:
        error: The DevRev exception to format.

    Returns:
        A formatted error string with relevant details.
    """
    if isinstance(error, AuthenticationError):
        return f"Authentication failed: {error.message}. Check your DEVREV_API_TOKEN."
    if isinstance(error, ForbiddenError):
        return f"Permission denied: {error.message}"
    if isinstance(error, NotFoundError):
        return f"Not found: {error.message}"
    if isinstance(error, DevRevValidationError):
        fields = ""
        if error.field_errors:
            fields = " Fields: " + ", ".join(f"{k}: {v}" for k, v in error.field_errors.items())
        return f"Validation error: {error.message}.{fields}"
    if isinstance(error, ConflictError):
        return f"Conflict: {error.message}"
    if isinstance(error, RateLimitError):
        retry = f" Retry after {error.retry_after}s." if error.retry_after else ""
        return f"Rate limited: {error.message}.{retry}"
    if isinstance(error, ServerError):
        return f"DevRev server error: {error.message}"
    if isinstance(error, ServiceUnavailableError):
        return f"DevRev service unavailable: {error.message}"
    if isinstance(error, DevRevTimeoutError):
        return f"Request timed out: {error.message}"
    if isinstance(error, BetaAPIRequiredError):
        return (
            f"Beta API required: {error.message}. "
            "Set DEVREV_API_VERSION=beta to enable beta features."
        )
    return f"DevRev API error: {error.message}"
