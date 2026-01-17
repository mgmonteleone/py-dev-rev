"""DevRev Python SDK.

A modern, type-safe Python SDK for the DevRev API.
"""

from devrev.client import AsyncDevRevClient, DevRevClient
from devrev.config import DevRevConfig, configure, get_config
from devrev.exceptions import (
    AuthenticationError,
    CircuitBreakerError,
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
from devrev.utils.http import (
    CircuitBreakerConfig,
    CircuitState,
    ConnectionPoolConfig,
    TimeoutConfig,
)
from devrev.utils.logging import JSONFormatter, configure_logging

__version__ = "1.0.0"
__all__ = [
    # Version
    "__version__",
    # Clients
    "DevRevClient",
    "AsyncDevRevClient",
    # Configuration
    "DevRevConfig",
    "get_config",
    "configure",
    # HTTP Configuration
    "TimeoutConfig",
    "ConnectionPoolConfig",
    "CircuitBreakerConfig",
    "CircuitState",
    # Logging
    "configure_logging",
    "JSONFormatter",
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
    "CircuitBreakerError",
]
