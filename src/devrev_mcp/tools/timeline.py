"""MCP tools for DevRev timeline entry operations."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.timeline_entries import (
    TimelineEntriesCreateRequest,
    TimelineEntriesDeleteRequest,
    TimelineEntriesGetRequest,
    TimelineEntriesListRequest,
    TimelineEntriesUpdateRequest,
    TimelineEntryType,
)
from devrev_mcp.server import mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_timeline_list(
    ctx: Context,
    object_id: str,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List timeline entries for a DevRev object.

    Args:
        object_id: Parent object ID (e.g., "don:core:dvrv-us-1:devo/1:ticket/123").
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        request = TimelineEntriesListRequest(
            object=object_id,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        entries = await app.client.timeline_entries.list(request)
        items = serialize_models(list(entries))
        return {"count": len(items), "timeline_entries": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_timeline_get(
    ctx: Context,
    id: str,
) -> dict[str, Any]:
    """Get a DevRev timeline entry by ID.

    Args:
        id: Timeline entry ID (e.g., "don:core:dvrv-us-1:devo/1:timeline_entry/123").
    """
    app = ctx.request_context.lifespan_context
    try:
        request = TimelineEntriesGetRequest(id=id)
        entry = await app.client.timeline_entries.get(request)
        return serialize_model(entry)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_timeline_create(
    ctx: Context,
    object_id: str,
    type: str = "timeline_comment",
    body: str | None = None,
) -> dict[str, Any]:
    """Create a new DevRev timeline entry.

    Args:
        object_id: Parent object ID (e.g., "don:core:dvrv-us-1:devo/1:ticket/123").
        type: Entry type (default: "timeline_comment"). Valid values: "timeline_comment",
            "timeline_note", "timeline_event", "timeline_change_event".
        body: Entry content/body text.
    """
    app = ctx.request_context.lifespan_context
    try:
        # Convert string type to TimelineEntryType enum
        try:
            entry_type = TimelineEntryType[type.upper().replace("TIMELINE_", "")]
        except KeyError as exc:
            raise ValueError(
                f"Invalid timeline entry type: {type}. Valid values: "
                f"timeline_comment, timeline_note, timeline_event, timeline_change_event"
            ) from exc

        request = TimelineEntriesCreateRequest(object=object_id, type=entry_type, body=body)
        entry = await app.client.timeline_entries.create(request)
        return serialize_model(entry)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_timeline_update(
    ctx: Context,
    id: str,
    body: str | None = None,
) -> dict[str, Any]:
    """Update a DevRev timeline entry.

    Args:
        id: Timeline entry ID to update.
        body: New entry content/body text.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = TimelineEntriesUpdateRequest(id=id, body=body)
        entry = await app.client.timeline_entries.update(request)
        return serialize_model(entry)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_timeline_delete(
    ctx: Context,
    id: str,
) -> dict[str, Any]:
    """Delete a DevRev timeline entry.

    Args:
        id: Timeline entry ID to delete.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = TimelineEntriesDeleteRequest(id=id)
        await app.client.timeline_entries.delete(request)
        return {"deleted": True, "id": id}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
