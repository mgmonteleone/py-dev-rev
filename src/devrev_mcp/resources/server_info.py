"""MCP resource for DevRev server information."""

from __future__ import annotations

import json
import logging
import platform
import sys

from devrev_mcp import __version__
from devrev_mcp.server import mcp

logger = logging.getLogger(__name__)


@mcp.resource("devrev://server/info")
async def get_server_info_resource() -> str:
    """Get DevRev MCP Server information as a resource.

    Returns static server metadata including version, Python version,
    and links. For dynamic information like uptime and latest PyPI version,
    use the devrev_server_info tool instead.

    Returns:
        JSON string containing server metadata.
    """
    return json.dumps(
        {
            "uri": "devrev://server/info",
            "type": "server_info",
            "name": "DevRev MCP Server",
            "version": __version__,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "links": {
                "github": "https://github.com/mgmonteleone/py-dev-rev",
                "documentation": "https://mgmonteleone.github.io/py-dev-rev/",
                "pypi": "https://pypi.org/project/devrev-Python-SDK/",
            },
            "note": "Use devrev_server_info tool for dynamic info (uptime, latest version check).",
        }
    )
