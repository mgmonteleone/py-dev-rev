"""MCP tools for DevRev link operations."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.links import (
    LinksCreateRequest,
    LinksDeleteRequest,
    LinksGetRequest,
    LinksListRequest,
    LinkType,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_links_list(
    ctx: Context,
    object_id: str | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev links, optionally filtered by object ID.

    Args:
        object_id: Filter links by object ID (e.g., "don:core:dvrv-us-1:devo/1:ticket/123").
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        request = LinksListRequest(
            object=object_id,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        links = await app.client.links.list(request)
        items = serialize_models(list(links))
        return {"count": len(items), "links": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_links_get(
    ctx: Context,
    id: str,
) -> dict[str, Any]:
    """Get a DevRev link by ID.

    Args:
        id: Link ID (e.g., "don:core:dvrv-us-1:devo/1:link/123").
    """
    app = ctx.request_context.lifespan_context
    try:
        request = LinksGetRequest(id=id)
        link = await app.client.links.get(request)
        return serialize_model(link)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_links_create(
        ctx: Context,
        link_type: str,
        source: str,
        target: str,
    ) -> dict[str, Any]:
        """Create a link between two DevRev objects.

        Args:
            link_type: Type of link (e.g., "is_blocked_by", "is_related_to", "is_duplicate_of").
            source: Source object ID (e.g., "don:core:dvrv-us-1:devo/1:ticket/123").
            target: Target object ID (e.g., "don:core:dvrv-us-1:devo/1:ticket/456").
        """
        app = ctx.request_context.lifespan_context
        try:
            # Try to convert to LinkType enum, but allow custom link types
            try:
                link_type_value = LinkType[link_type.upper()]
            except KeyError:
                # Custom link type - pass as raw string
                link_type_value = link_type

            request = LinksCreateRequest(
                link_type=link_type_value,
                source=source,
                target=target,
            )
            link = await app.client.links.create(request)
            return serialize_model(link)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_links_delete(
        ctx: Context,
        id: str,
    ) -> dict[str, Any]:
        """Delete a DevRev link.

        Args:
            id: Link ID to delete.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = LinksDeleteRequest(id=id)
            await app.client.links.delete(request)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
