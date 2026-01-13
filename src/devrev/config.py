"""Configuration management for DevRev SDK.

This module provides configuration loading from environment variables
with optional .env file support for local development.
"""

from typing import Any, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DevRevConfig(BaseSettings):
    """DevRev SDK Configuration.

    Configuration is loaded from environment variables. For local development,
    use a .env file (never commit this file!).

    Environment Variables:
        DEVREV_API_TOKEN: API authentication token (required)
        DEVREV_BASE_URL: API base URL (default: https://api.devrev.ai)
        DEVREV_TIMEOUT: Request timeout in seconds (default: 30)
        DEVREV_MAX_RETRIES: Maximum retry attempts (default: 3)
        DEVREV_LOG_LEVEL: Logging level (default: WARN)

    Example:
        ```python
        from devrev import DevRevConfig

        # Load from environment
        config = DevRevConfig()

        # Or with explicit values
        config = DevRevConfig(
            api_token="your-token",
            log_level="DEBUG",
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

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARN", "WARNING", "ERROR"] = Field(
        default="WARN",
        description="Logging level",
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

        configure_logging(level=_config.log_level)
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

        config = configure(
            api_token="your-token",
            log_level="DEBUG",
            timeout=60,
        )
        ```
    """
    global _config
    _config = DevRevConfig(**kwargs)
    # Auto-configure logging based on config
    from devrev.utils.logging import configure_logging

    configure_logging(level=_config.log_level)
    return _config


def reset_config() -> None:
    """Reset the global configuration (primarily for testing)."""
    global _config
    _config = None
