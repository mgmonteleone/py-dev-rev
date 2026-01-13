"""DevRev Python SDK.

A modern, type-safe Python SDK for the DevRev API.
"""

from devrev.config import DevRevConfig, configure, get_config
from devrev.exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    DevRevError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)

__version__ = "0.1.0"
__all__ = [
    # Version
    "__version__",
    # Configuration
    "DevRevConfig",
    "get_config",
    "configure",
    # Exceptions
    "DevRevError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "ValidationError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "ServiceUnavailableError",
    "ConfigurationError",
    "TimeoutError",
    "NetworkError",
]
