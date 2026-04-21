"""MCP tools for DevRev conversation operations."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.base import DateFilter
from devrev.models.conversations import (
    ConversationsCreateRequest,
    ConversationsDeleteRequest,
    ConversationsGetRequest,
    ConversationsListRequest,
    ConversationsUpdateRequest,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.don_id import validate_don_id
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


def _parse_iso_datetime(value: str, field_name: str) -> datetime:
    """Parse an ISO-8601 datetime string, accepting a trailing ``Z`` for UTC.

    Args:
        value: The ISO-8601 datetime string.
        field_name: Name of the parameter being parsed (for error messages).

    Returns:
        A parsed ``datetime`` instance.

    Raises:
        RuntimeError: If the string cannot be parsed.
    """
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise RuntimeError(
            f"Invalid {field_name} format: {value}. "
            "Use ISO-8601 format (e.g., 2025-01-01T00:00:00Z)."
        ) from e


@mcp.tool()
async def devrev_conversations_list(
    ctx: Context[Any, Any, Any],
    cursor: str | None = None,
    limit: int | None = None,
    modified_date_after: str | None = None,
    modified_date_before: str | None = None,
    sort_by: list[str] | None = None,
) -> dict[str, Any]:
    """List DevRev conversations.

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
        modified_date_after: Only include conversations modified after this
            ISO-8601 timestamp (e.g., "2025-01-01T00:00:00Z").
        modified_date_before: Only include conversations modified before this
            ISO-8601 timestamp.
        sort_by: Sort order entries (e.g., ["modified_date:desc"] or
            ["-modified_date"]).
    """
    app = ctx.request_context.lifespan_context
    try:
        modified_date: DateFilter | None = None
        if modified_date_after is not None or modified_date_before is not None:
            after_dt = (
                _parse_iso_datetime(modified_date_after, "modified_date_after")
                if modified_date_after is not None
                else None
            )
            before_dt = (
                _parse_iso_datetime(modified_date_before, "modified_date_before")
                if modified_date_before is not None
                else None
            )
            modified_date = DateFilter(after=after_dt, before=before_dt)
        request = ConversationsListRequest(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
            modified_date=modified_date,
            sort_by=sort_by,
        )
        conversations = await app.get_client().conversations.list(request)
        items = serialize_models(list(conversations))
        return {"count": len(items), "conversations": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_conversations_list_modified_since(
    ctx: Context[Any, Any, Any],
    after: str,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev conversations modified after a given ISO-8601 datetime.

    Streams pages newest-first, stopping when the cutoff is crossed or the
    ``limit`` is reached. The cutoff is supplied as an ISO-8601 string.

    Args:
        after: ISO-8601 datetime; only conversations modified after this are
            returned (e.g., "2025-01-01T00:00:00Z").
        limit: Maximum number of conversations to return overall.
    """
    app = ctx.request_context.lifespan_context
    after_dt = _parse_iso_datetime(after, "after")
    try:
        conversations = await app.get_client().conversations.list_modified_since(
            after=after_dt,
            limit=limit,
        )
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
    validate_don_id(id, "conversation", "devrev_conversations_get")
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
        validate_don_id(id, "conversation", "devrev_conversations_update")
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
        validate_don_id(id, "conversation", "devrev_conversations_delete")
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
