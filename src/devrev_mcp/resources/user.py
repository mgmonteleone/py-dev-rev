"""MCP resources for DevRev user objects (dev users and rev users)."""

from __future__ import annotations

import json
import logging

from devrev_mcp.server import mcp

logger = logging.getLogger(__name__)


@mcp.resource("devrev://user/dev/{user_id}")
async def get_dev_user_resource(user_id: str) -> str:
    """Get a DevRev developer user as a resource.

    Returns dev user details including display name, email,
    state, and role information.

    Args:
        user_id: The dev user ID (DON format).

    Returns:
        JSON string containing resource metadata and reference to the tool.
    """
    return json.dumps(
        {
            "uri": f"devrev://user/dev/{user_id}",
            "type": "dev_user",
            "id": user_id,
            "note": "Use devrev_dev_users_get tool to fetch full dev user details.",
        }
    )


@mcp.resource("devrev://user/rev/{user_id}")
async def get_rev_user_resource(user_id: str) -> str:
    """Get a DevRev customer (rev) user as a resource.

    Returns rev user details including display name, email,
    phone numbers, and associated rev org.

    Args:
        user_id: The rev user ID (DON format).

    Returns:
        JSON string containing resource metadata and reference to the tool.
    """
    return json.dumps(
        {
            "uri": f"devrev://user/rev/{user_id}",
            "type": "rev_user",
            "id": user_id,
            "note": "Use devrev_rev_users_get tool to fetch full rev user details.",
        }
    )
