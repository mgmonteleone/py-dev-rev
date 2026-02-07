"""Configuration for the DevRev MCP Server."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPServerConfig(BaseSettings):
    """MCP Server configuration loaded from environment variables.

    All settings can be overridden via environment variables with the MCP_ prefix.
    For example, MCP_LOG_LEVEL=DEBUG, MCP_DEFAULT_PAGE_SIZE=50.
    """

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    server_name: str = Field(
        default="DevRev MCP Server",
        description="Display name for the MCP server",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )
    enable_beta_tools: bool = Field(
        default=True,
        description="Enable beta API tools (search, recommendations)",
    )
    default_page_size: int = Field(
        default=25,
        description="Default page size for list operations",
    )
    max_page_size: int = Field(
        default=100,
        description="Maximum allowed page size for list operations",
    )
