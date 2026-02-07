"""MCP resources for DevRev part objects."""

from __future__ import annotations

import json
import logging

from devrev_mcp.server import mcp

logger = logging.getLogger(__name__)


@mcp.resource("devrev://part/{part_id}")
async def get_part_resource(part_id: str) -> str:
    """Get a DevRev part as a resource.

    Returns resource metadata with a pointer to the devrev_parts_get tool
    for fetching full part details.

    Args:
        part_id: The part ID (DON format).

    Returns:
        JSON string containing resource metadata and reference to the tool.
    """
    return json.dumps(
        {
            "uri": f"devrev://part/{part_id}",
            "type": "part",
            "id": part_id,
            "note": "Use devrev_parts_get tool to fetch full part details.",
        }
    )
