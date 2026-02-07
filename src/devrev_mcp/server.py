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

    # Use beta API version only if beta tools are enabled
    api_version = APIVersion.BETA if config.enable_beta_tools else APIVersion.PUBLIC
    client = AsyncDevRevClient(api_version=api_version)
    try:
        yield AppContext(client=client, config=config)
    finally:
        await client.close()
        logger.info("DevRev MCP Server shut down.")


# Create the FastMCP server instance
# Note: server name is set from config during lifespan, but FastMCP requires a name at init
# We use the default here, which matches the config default
_config = MCPServerConfig()
mcp = FastMCP(
    _config.server_name,
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
from devrev_mcp.tools import links as _links_tools  # noqa: E402, F401
from devrev_mcp.tools import parts as _parts_tools  # noqa: E402, F401
from devrev_mcp.tools import tags as _tags_tools  # noqa: E402, F401
from devrev_mcp.tools import timeline as _timeline_tools  # noqa: E402, F401
from devrev_mcp.tools import users as _users_tools  # noqa: E402, F401
from devrev_mcp.tools import works as _works_tools  # noqa: E402, F401

# Beta tools are only imported if enabled in config
if _config.enable_beta_tools:
    from devrev_mcp.tools import recommendations as _recommendations_tools  # noqa: E402, F401
    from devrev_mcp.tools import search as _search_tools  # noqa: E402, F401

# ----- Register resource modules -----
# These imports MUST be at the bottom to avoid circular imports.
# Each resource module imports `mcp` from this module to register its resources.
from devrev_mcp.resources import account as _account_resources  # noqa: E402, F401
from devrev_mcp.resources import article as _article_resources  # noqa: E402, F401
from devrev_mcp.resources import conversation as _conversation_resources  # noqa: E402, F401
from devrev_mcp.resources import part as _part_resources  # noqa: E402, F401
from devrev_mcp.resources import ticket as _ticket_resources  # noqa: E402, F401
from devrev_mcp.resources import user as _user_resources  # noqa: E402, F401

# ----- Register prompt modules -----
# These imports MUST be at the bottom to avoid circular imports.
# Each prompt module imports `mcp` from this module to register its prompts.
from devrev_mcp.prompts import escalation as _escalation_prompts  # noqa: E402, F401
from devrev_mcp.prompts import investigate as _investigate_prompts  # noqa: E402, F401
from devrev_mcp.prompts import response as _response_prompts  # noqa: E402, F401
from devrev_mcp.prompts import summarize as _summarize_prompts  # noqa: E402, F401
from devrev_mcp.prompts import triage as _triage_prompts  # noqa: E402, F401
