"""MCP resources for DevRev conversation objects."""

from __future__ import annotations

import json
import logging

from devrev_mcp.server import mcp

logger = logging.getLogger(__name__)


@mcp.resource("devrev://conversation/{conversation_id}")
async def get_conversation_resource(conversation_id: str) -> str:
    """Get a DevRev conversation as a resource.

    Returns resource metadata with a pointer to the devrev_conversations_get tool
    for fetching full conversation details.

    Args:
        conversation_id: The conversation ID (DON format).

    Returns:
        JSON string containing resource metadata and reference to the tool.
    """
    return json.dumps(
        {
            "uri": f"devrev://conversation/{conversation_id}",
            "type": "conversation",
            "id": conversation_id,
            "note": "Use devrev_conversations_get tool to fetch full conversation details.",
        }
    )
