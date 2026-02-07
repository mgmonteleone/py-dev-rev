"""DevRev MCP Server — main server setup and lifecycle management."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP

from devrev import APIVersion, AsyncDevRevClient
from devrev_mcp import __version__
from devrev_mcp.config import MCPServerConfig

logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context shared across all MCP tool invocations.

    Attributes:
        client: The async DevRev API client.
        config: The MCP server configuration.
    """

    client: AsyncDevRevClient
    config: MCPServerConfig


@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage the MCP server lifecycle.

    Creates the DevRev client and configuration on startup,
    and ensures proper cleanup on shutdown.

    Args:
        _server: The FastMCP server instance (unused).

    Yields:
        AppContext with initialized client and config.
    """
    config = MCPServerConfig()
    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO))
    logger.info(
        "Starting %s v%s (beta_tools=%s)",
        config.server_name,
        __version__,
        config.enable_beta_tools,
    )

    client = AsyncDevRevClient(api_version=APIVersion.BETA)
    try:
        yield AppContext(client=client, config=config)
    finally:
        await client.close()
        logger.info("DevRev MCP Server shut down.")


# Create the FastMCP server instance
mcp = FastMCP(
    "DevRev MCP Server",
    lifespan=app_lifespan,
)


# ----- Register tool modules -----
# These imports MUST be at the bottom to avoid circular imports.
# Each tool module imports `mcp` from this module to register its tools.
from devrev_mcp.tools import accounts as _accounts_tools  # noqa: E402, F401
from devrev_mcp.tools import articles as _articles_tools  # noqa: E402, F401
from devrev_mcp.tools import conversations as _conversations_tools  # noqa: E402, F401
from devrev_mcp.tools import engagements as _engagements_tools  # noqa: E402, F401
from devrev_mcp.tools import groups as _groups_tools  # noqa: E402, F401
from devrev_mcp.tools import incidents as _incidents_tools  # noqa: E402, F401
from devrev_mcp.tools import parts as _parts_tools  # noqa: E402, F401
from devrev_mcp.tools import recommendations as _recommendations_tools  # noqa: E402, F401
from devrev_mcp.tools import search as _search_tools  # noqa: E402, F401
from devrev_mcp.tools import tags as _tags_tools  # noqa: E402, F401
from devrev_mcp.tools import users as _users_tools  # noqa: E402, F401
from devrev_mcp.tools import works as _works_tools  # noqa: E402, F401
