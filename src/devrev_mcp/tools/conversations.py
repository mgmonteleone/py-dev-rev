"""MCP tools for DevRev conversation operations."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.conversations import (
    ConversationsCreateRequest,
    ConversationsDeleteRequest,
    ConversationsGetRequest,
    ConversationsListRequest,
    ConversationsUpdateRequest,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_conversations_list(
    ctx: Context[Any, Any, Any],
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev conversations.

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        request = ConversationsListRequest(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        conversations = await app.get_client().conversations.list(request)
        items = serialize_models(list(conversations))
        return {"count": len(items), "conversations": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_conversations_get(
    ctx: Context[Any, Any, Any],
    id: str,
) -> dict[str, Any]:
    """Get a DevRev conversation by ID.

    Args:
        id: Conversation ID (e.g., "don:core:dvrv-us-1:devo/1:conversation/123").
    """
    app = ctx.request_context.lifespan_context
    try:
        request = ConversationsGetRequest(id=id)
        conversation = await app.get_client().conversations.get(request)
        return serialize_model(conversation)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_conversations_create(
        ctx: Context[Any, Any, Any],
        type: str = "support",
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Create a new DevRev conversation.

        Args:
            type: Conversation type (default: "support").
            title: Conversation title.
            description: Conversation description.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = ConversationsCreateRequest(type=type, title=title, description=description)
            conversation = await app.get_client().conversations.create(request)
            return serialize_model(conversation)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_conversations_update(
        ctx: Context[Any, Any, Any],
        id: str,
        title: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a DevRev conversation.

        Args:
            id: Conversation ID to update.
            title: New conversation title.
            description: New conversation description.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = ConversationsUpdateRequest(id=id, title=title, description=description)
            conversation = await app.get_client().conversations.update(request)
            return serialize_model(conversation)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_conversations_delete(
        ctx: Context[Any, Any, Any],
        id: str,
    ) -> dict[str, Any]:
        """Delete a DevRev conversation.

        Args:
            id: Conversation ID to delete.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = ConversationsDeleteRequest(id=id)
            await app.get_client().conversations.delete(request)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_conversations_export(
    ctx: Context[Any, Any, Any],
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Export DevRev conversations (beta API only).

    This endpoint is only available with the beta API. Calling this tool
    when the client is configured for the public API will result in an error.

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        response = await app.get_client().conversations.export(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
            return_response=True,
        )
        items = serialize_models(list(response.conversations))
        return paginated_response(
            items, next_cursor=response.next_cursor, total_label="conversations"
        )
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
