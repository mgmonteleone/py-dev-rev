"""Configuration management for DevRev SDK.

This module provides configuration loading from environment variables
with optional .env file support for local development.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APIVersion(StrEnum):
    """DevRev API version selection.

    PUBLIC: Stable public API (default)
    BETA: Beta API with new features (may change)
    """

    PUBLIC = "public"
    BETA = "beta"


class DevRevConfig(BaseSettings):
    """DevRev SDK Configuration.

    Configuration is loaded from environment variables. For local development,
    use a .env file (never commit this file!).

    Environment Variables:
        DEVREV_API_TOKEN: API authentication token (required)
        DEVREV_BASE_URL: API base URL (default: https://api.devrev.ai)
        DEVREV_API_VERSION: API version (default: public, options: public, beta)
        DEVREV_TIMEOUT: Request timeout in seconds (default: 30)
        DEVREV_MAX_RETRIES: Maximum retry attempts (default: 3)
        DEVREV_LOG_LEVEL: Logging level (default: WARN)
        DEVREV_LOG_FORMAT: Log format - text or json (default: text)
        DEVREV_MAX_CONNECTIONS: Maximum connection pool size (default: 100)
        DEVREV_HTTP2: Enable HTTP/2 support (default: false)
        DEVREV_CIRCUIT_BREAKER_ENABLED: Enable circuit breaker (default: true)
        DEVREV_CIRCUIT_BREAKER_THRESHOLD: Failure threshold (default: 5)
        DEVREV_CIRCUIT_BREAKER_RECOVERY_TIMEOUT: Recovery timeout in seconds (default: 30)

    Example:
        ```python
        from devrev import DevRevConfig

        # Load from environment
        config = DevRevConfig()

        # Or with explicit values for production
        config = DevRevConfig(
            api_token="your-token",
            log_level="INFO",
            log_format="json",
            circuit_breaker_enabled=True,
        )
        ```
    """

    model_config = SettingsConfigDict(
        env_prefix="DEVREV_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Authentication
    api_token: SecretStr = Field(
        ...,
        description="DevRev API authentication token",
    )

    # API Settings
    base_url: str = Field(
        default="https://api.devrev.ai",
        description="DevRev API base URL",
    )
    api_version: APIVersion = Field(
        default=APIVersion.PUBLIC,
        description="DevRev API version (public or beta)",
    )

    # HTTP Settings
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of retry attempts",
    )

    # Connection Pool Settings (Performance)
    max_connections: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of connections in the pool",
    )
    max_keepalive_connections: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Maximum number of keep-alive connections",
    )
    keepalive_expiry: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Keep-alive connection expiry in seconds",
    )
    http2: bool = Field(
        default=False,
        description="Enable HTTP/2 support for improved performance",
    )

    # Circuit Breaker Settings (Reliability)
    circuit_breaker_enabled: bool = Field(
        default=True,
        description="Enable circuit breaker pattern for reliability",
    )
    circuit_breaker_threshold: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of failures before opening the circuit",
    )
    circuit_breaker_recovery_timeout: float = Field(
        default=30.0,
        ge=1.0,
        le=600.0,
        description="Seconds to wait before attempting recovery",
    )
    circuit_breaker_half_open_max_calls: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Number of test requests in half-open state",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR"] = Field(
        default="WARN",
        description="Logging level",
    )
    log_format: Literal["text", "json"] = Field(
        default="text",
        description="Log output format - 'text' for development, 'json' for production",
    )

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate and normalize base URL.

        Security: Enforces HTTPS-only connections to prevent credential leakage.

        Args:
            v: The base URL value

        Returns:
            Normalized URL without trailing slash

        Raises:
            ValueError: If URL uses insecure HTTP protocol
        """
        url = v.rstrip("/")
        # Security: Enforce HTTPS to prevent credential exposure
        if url.startswith("http://"):
            raise ValueError(
                "Insecure HTTP URLs are not allowed. Use HTTPS to protect your API credentials."
            )
        if not url.startswith("https://"):
            raise ValueError(
                "Base URL must start with 'https://'. "
                f"Got: {url[:50]}..."  # Truncate to avoid leaking full URL in errors
            )
        return url

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(
        cls, v: Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR"]
    ) -> Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR"]:
        """Normalize WARNING to WARN for consistency."""
        if v == "WARNING":
            return "WARN"
        return v

    @model_validator(mode="after")
    def validate_connection_pool(self) -> DevRevConfig:
        """Validate connection pool configuration.

        Ensures keepalive connections don't exceed max connections.
        """
        if self.max_keepalive_connections > self.max_connections:
            raise ValueError(
                f"max_keepalive_connections ({self.max_keepalive_connections}) "
                f"cannot exceed max_connections ({self.max_connections})"
            )
        return self


# Global configuration instance
_config: DevRevConfig | None = None


def get_config() -> DevRevConfig:
    """Get or create the global configuration instance.

    Returns:
        The global DevRevConfig instance

    Example:
        ```python
        from devrev import get_config

        config = get_config()
        print(f"Base URL: {config.base_url}")
        ```
    """
    global _config
    if _config is None:
        _config = DevRevConfig()
        # Auto-configure logging based on config
        from devrev.utils.logging import configure_logging

        configure_logging(level=_config.log_level, log_format=_config.log_format)
    return _config


def configure(**kwargs: Any) -> DevRevConfig:
    """Configure the SDK with custom settings.

    Args:
        **kwargs: Configuration options to override

    Returns:
        The new DevRevConfig instance

    Example:
        ```python
        from devrev import configure

        # Development
        config = configure(
            api_token="your-token",
            log_level="DEBUG",
            timeout=60,
        )

        # Production
        config = configure(
            api_token="your-token",
            log_level="INFO",
            log_format="json",
            circuit_breaker_enabled=True,
        )
        ```
    """
    global _config
    _config = DevRevConfig(**kwargs)
    # Auto-configure logging based on config
    from devrev.utils.logging import configure_logging

    configure_logging(level=_config.log_level, log_format=_config.log_format)
    return _config


def reset_config() -> None:
    """Reset the global configuration (primarily for testing)."""
    global _config
    _config = None
