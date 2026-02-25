"""DevRev MCP Server - Parts Tools.

This module provides MCP tools for managing DevRev parts (products, capabilities,
features, and enhancements).
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.parts import (
    PartsCreateRequest,
    PartsDeleteRequest,
    PartsGetRequest,
    PartsUpdateRequest,
    PartType,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_parts_list(
    ctx: Context[Any, Any, Any], cursor: str | None = None, limit: int | None = None
) -> dict[str, Any]:
    """List DevRev parts (products, capabilities, features, enhancements).

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).

    Returns:
        Dictionary containing list of parts and pagination info.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        response = await app.get_client().parts.list(
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
            cursor=cursor,
        )
        items = serialize_models(response.parts)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="parts")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_parts_get(ctx: Context[Any, Any, Any], id: str) -> dict[str, Any]:
    """Get a specific DevRev part by ID.

    Args:
        id: The ID of the part to retrieve.

    Returns:
        Dictionary containing the part details.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        part = await app.get_client().parts.get(PartsGetRequest(id=id))
        return serialize_model(part)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_parts_create(
        ctx: Context[Any, Any, Any],
        name: str,
        type: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new DevRev part.

        Args:
            name: The name of the part.
            type: The type of part (PRODUCT, CAPABILITY, FEATURE, ENHANCEMENT).
            description: Optional description of the part.

        Returns:
            Dictionary containing the created part details.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            try:
                part_type = PartType[type.upper()]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid part type: {e.args[0]}. "
                    f"Valid types: {', '.join(t.name for t in PartType)}"
                ) from e
            request = PartsCreateRequest(
                name=name,
                type=part_type,
                description=description,
            )
            part = await app.get_client().parts.create(request)
            return serialize_model(part)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_parts_update(
        ctx: Context[Any, Any, Any],
        id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing DevRev part.

        Args:
            id: The ID of the part to update.
            name: Optional new name for the part.
            description: Optional new description for the part.

        Returns:
            Dictionary containing the updated part details.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = PartsUpdateRequest(
                id=id,
                name=name,
                description=description,
            )
            part = await app.get_client().parts.update(request)
            return serialize_model(part)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_parts_delete(ctx: Context[Any, Any, Any], id: str) -> dict[str, Any]:
        """Delete a DevRev part.

        Args:
            id: The ID of the part to delete.

        Returns:
            Dictionary confirming the deletion.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            await app.get_client().parts.delete(PartsDeleteRequest(id=id))
            return {"success": True, "message": f"Part {id} deleted successfully"}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
