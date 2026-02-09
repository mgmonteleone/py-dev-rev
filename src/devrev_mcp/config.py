"""Configuration for the DevRev MCP Server."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPServerConfig(BaseSettings):
    """MCP Server configuration loaded from environment variables.

    All settings can be overridden via environment variables with the MCP_ prefix.
    For example, MCP_LOG_LEVEL=DEBUG, MCP_TRANSPORT=streamable-http.
    """

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Server identity
    server_name: str = Field(
        default="DevRev MCP Server",
        description="Display name for the MCP server",
    )

    # Transport settings
    transport: Literal["stdio", "streamable-http", "sse"] = Field(
        default="stdio",
        description="Transport type: stdio (local), streamable-http (production), sse (legacy)",
    )
    host: str = Field(
        default="127.0.0.1",
        description="HTTP server bind host (for streamable-http and sse transports)",
    )
    port: int = Field(
        default=8080,
        description="HTTP server bind port (for streamable-http and sse transports)",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )
    log_format: Literal["text", "json"] = Field(
        default="json",
        description="Log output format",
    )

    # Tool settings
    enable_beta_tools: bool = Field(
        default=True,
        description="Enable beta API tools (search, recommendations, incidents, engagements)",
    )
    enable_destructive_tools: bool = Field(
        default=True,
        description="Enable create/update/delete tools",
    )

    # Pagination
    default_page_size: int = Field(
        default=25,
        description="Default page size for list operations",
    )
    max_page_size: int = Field(
        default=100,
        description="Maximum allowed page size for list operations",
    )

    # Authentication (for HTTP transports)
    auth_token: SecretStr | None = Field(
        default=None,
        description="Bearer token for HTTP transport authentication. If set, all HTTP requests must include this token.",
    )

    # Rate limiting
    rate_limit_rpm: int = Field(
        default=120,
        description="Maximum requests per minute per session (0 to disable)",
    )

    # Security
    enable_dns_rebinding_protection: bool = Field(
        default=True,
        description="Enable DNS rebinding protection for HTTP transports",
    )
    allowed_hosts: list[str] = Field(
        default_factory=list,
        description="Allowed Host header values for DNS rebinding protection",
    )
    cors_allowed_origins: list[str] = Field(
        default_factory=list,
        description="Allowed CORS origins for HTTP transports",
    )

    @model_validator(mode="after")
    def _validate_auth_token(self) -> MCPServerConfig:
        """Reject empty auth token strings."""
        if self.auth_token is not None and not self.auth_token.get_secret_value():
            self.auth_token = None  # Treat empty string as unset
        return self
