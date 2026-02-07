"""MCP resources for DevRev article objects."""

from __future__ import annotations

import json
import logging

from devrev_mcp.server import mcp

logger = logging.getLogger(__name__)


@mcp.resource("devrev://article/{article_id}")
async def get_article_resource(article_id: str) -> str:
    """Get a DevRev article as a resource.

    Returns resource metadata with a pointer to the devrev_articles_get tool
    for fetching full article details.

    Args:
        article_id: The article ID (DON format).

    Returns:
        JSON string containing resource metadata and reference to the tool.
    """
    return json.dumps(
        {
            "uri": f"devrev://article/{article_id}",
            "type": "article",
            "id": article_id,
            "mime_type": "text/markdown",
            "note": "Use devrev_articles_get tool to fetch full article details.",
        }
    )
