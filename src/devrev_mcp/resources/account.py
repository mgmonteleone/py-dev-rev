"""MCP resources for DevRev account objects."""

from __future__ import annotations

import json
import logging

from devrev_mcp.server import mcp

logger = logging.getLogger(__name__)


@mcp.resource("devrev://account/{account_id}")
async def get_account_resource(account_id: str) -> str:
    """Get a DevRev account as a resource.

    Returns account details including display name, domains, tier,
    and ownership information.

    Args:
        account_id: The account ID (DON format).

    Returns:
        JSON string containing resource metadata and reference to the tool.
    """
    return json.dumps(
        {
            "uri": f"devrev://account/{account_id}",
            "type": "account",
            "id": account_id,
            "note": "Use devrev_accounts_get tool to fetch full account details.",
        }
    )
