"""MCP resources for DevRev ticket objects."""

from __future__ import annotations

import json
import logging

from devrev_mcp.server import mcp

logger = logging.getLogger(__name__)


@mcp.resource("devrev://ticket/{ticket_id}")
async def get_ticket_resource(ticket_id: str) -> str:
    """Get a DevRev ticket as a resource.

    Returns full ticket details including title, body, stage, priority,
    severity, owner, and creation date.

    Args:
        ticket_id: The ticket ID (DON format).

    Returns:
        JSON string containing resource metadata and reference to the tool.
    """
    return json.dumps(
        {
            "uri": f"devrev://ticket/{ticket_id}",
            "type": "ticket",
            "id": ticket_id,
            "note": "Use devrev_works_get tool to fetch full ticket details.",
        }
    )
