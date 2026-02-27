"""DevRev Python SDK.

A modern, type-safe Python SDK for the DevRev API.
"""

from devrev.client import AsyncDevRevClient, DevRevClient
from devrev.config import APIVersion, DevRevConfig, configure, get_config
from devrev.exceptions import (
    AuthenticationError,
    BetaAPIRequiredError,
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

__version__ = __import__("importlib.metadata", fromlist=["version"]).version("devrev-Python-SDK")
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
    "APIVersion",
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
    "BetaAPIRequiredError",
]
