"""DevRev MCP tools for tag management."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.tags import (
    TagsCreateRequest,
    TagsDeleteRequest,
    TagsGetRequest,
    TagsListRequest,
    TagsUpdateRequest,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_tags_list(
    ctx: Context, cursor: str | None = None, limit: int | None = None
) -> dict[str, Any]:
    """List DevRev tags.

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).

    Returns:
        Dictionary containing count and list of tags.

    Raises:
        RuntimeError: If the DevRev API request fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = TagsListRequest(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        tags = await app.get_client().tags.list(request)
        items = serialize_models(list(tags))
        return {"count": len(items), "tags": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_tags_get(ctx: Context, id: str) -> dict[str, Any]:
    """Get a DevRev tag by ID.

    Args:
        id: The tag ID.

    Returns:
        The tag details.

    Raises:
        RuntimeError: If the DevRev API request fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = TagsGetRequest(id=id)
        tag = await app.get_client().tags.get(request)
        return serialize_model(tag)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_tags_create(
        ctx: Context, name: str, description: str | None = None
    ) -> dict[str, Any]:
        """Create a new DevRev tag.

        Args:
            name: The tag name.
            description: Optional tag description.

        Returns:
            The created tag details.

        Raises:
            RuntimeError: If the DevRev API request fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = TagsCreateRequest(name=name, description=description)
            tag = await app.get_client().tags.create(request)
            return serialize_model(tag)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_tags_update(
        ctx: Context, id: str, name: str | None = None, description: str | None = None
    ) -> dict[str, Any]:
        """Update a DevRev tag.

        Args:
            id: The tag ID.
            name: Optional new tag name.
            description: Optional new tag description.

        Returns:
            The updated tag details.

        Raises:
            RuntimeError: If the DevRev API request fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = TagsUpdateRequest(id=id, name=name, description=description)
            tag = await app.get_client().tags.update(request)
            return serialize_model(tag)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_tags_delete(ctx: Context, id: str) -> dict[str, Any]:
        """Delete a DevRev tag.

        Args:
            id: The tag ID.

        Returns:
            Confirmation of deletion.

        Raises:
            RuntimeError: If the DevRev API request fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = TagsDeleteRequest(id=id)
            await app.get_client().tags.delete(request)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
