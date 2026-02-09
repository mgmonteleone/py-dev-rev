"""DevRev MCP Server - Engagements Tools.

This module provides MCP tools for managing DevRev engagements (calls, meetings, emails, etc.).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.engagements import EngagementType
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_engagements_list(
    ctx: Context,
    engagement_type: list[str] | None = None,
    members: list[str] | None = None,
    parent: str | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List engagements with optional filters.

    Args:
        ctx: MCP context
        engagement_type: Filter by engagement types (CALL, MEETING, EMAIL, etc.)
        members: Filter by member IDs
        parent: Filter by parent object ID
        cursor: Pagination cursor
        limit: Maximum number of results

    Returns:
        Paginated list of engagements
    """
    app = ctx.request_context.lifespan_context
    try:
        types = None
        if engagement_type:
            try:
                types = [EngagementType[t.upper()] for t in engagement_type]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid engagement type: {e.args[0]}. "
                    f"Valid types: {', '.join(t.name for t in EngagementType)}"
                ) from e
        response = await app.client.engagements.list(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
            engagement_type=types,
            members=members,
            parent=parent,
        )
        items = serialize_models(response.engagements)
        return paginated_response(
            items, next_cursor=response.next_cursor, total_label="engagements"
        )
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_engagements_get(ctx: Context, id: str) -> dict[str, Any]:
    """Get a specific engagement by ID.

    Args:
        ctx: MCP context
        id: Engagement ID

    Returns:
        Engagement details
    """
    app = ctx.request_context.lifespan_context
    try:
        engagement = await app.client.engagements.get(id)
        return serialize_model(engagement)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_engagements_create(
        ctx: Context,
        title: str,
        engagement_type: str,
        description: str | None = None,
        members: list[str] | None = None,
        parent: str | None = None,
        scheduled_date: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new engagement.

        Args:
            ctx: MCP context
            title: Engagement title
            engagement_type: Type (CALL, MEETING, EMAIL, CONVERSATION, etc.)
            description: Optional description
            members: Optional list of member IDs
            parent: Optional parent object ID
            scheduled_date: Optional scheduled date (ISO format)
            tags: Optional list of tags

        Returns:
            Created engagement
        """
        app = ctx.request_context.lifespan_context
        try:
            try:
                eng_type = EngagementType[engagement_type.upper()]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid engagement type: {e.args[0]}. "
                    f"Valid types: {', '.join(t.name for t in EngagementType)}"
                ) from e
            sched = None
            if scheduled_date:
                try:
                    sched = datetime.fromisoformat(scheduled_date)
                except ValueError as e:
                    raise RuntimeError(
                        f"Invalid scheduled_date format: {scheduled_date}. "
                        "Use ISO format (YYYY-MM-DDTHH:MM:SS)."
                    ) from e
            engagement = await app.client.engagements.create(
                title=title,
                engagement_type=eng_type,
                description=description,
                members=members,
                parent=parent,
                scheduled_date=sched,
                tags=tags,
            )
            return serialize_model(engagement)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_engagements_update(
        ctx: Context,
        id: str,
        title: str | None = None,
        description: str | None = None,
        engagement_type: str | None = None,
        scheduled_date: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing engagement.

        Args:
            ctx: MCP context
            id: Engagement ID
            title: Optional new title
            description: Optional new description
            engagement_type: Optional new type
            scheduled_date: Optional new scheduled date (ISO format)

        Returns:
            Updated engagement
        """
        app = ctx.request_context.lifespan_context
        try:
            eng_type = None
            if engagement_type:
                try:
                    eng_type = EngagementType[engagement_type.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid engagement type: {e.args[0]}. "
                        f"Valid types: {', '.join(t.name for t in EngagementType)}"
                    ) from e
            sched = None
            if scheduled_date:
                try:
                    sched = datetime.fromisoformat(scheduled_date)
                except ValueError as e:
                    raise RuntimeError(
                        f"Invalid scheduled_date format: {scheduled_date}. "
                        "Use ISO format (YYYY-MM-DDTHH:MM:SS)."
                    ) from e
            engagement = await app.client.engagements.update(
                id,
                title=title,
                description=description,
                engagement_type=eng_type,
                scheduled_date=sched,
            )
            return serialize_model(engagement)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_engagements_delete(ctx: Context, id: str) -> dict[str, Any]:
        """Delete an engagement.

        Args:
            ctx: MCP context
            id: Engagement ID

        Returns:
            Deletion confirmation
        """
        app = ctx.request_context.lifespan_context
        try:
            await app.client.engagements.delete(id)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_engagements_count(
    ctx: Context,
    engagement_type: list[str] | None = None,
    members: list[str] | None = None,
) -> dict[str, Any]:
    """Count engagements with optional filters.

    Args:
        ctx: MCP context
        engagement_type: Filter by engagement types
        members: Filter by member IDs

    Returns:
        Count of matching engagements
    """
    app = ctx.request_context.lifespan_context
    try:
        types = None
        if engagement_type:
            try:
                types = [EngagementType[t.upper()] for t in engagement_type]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid engagement type: {e.args[0]}. "
                    f"Valid types: {', '.join(t.name for t in EngagementType)}"
                ) from e
        count = await app.client.engagements.count(
            engagement_type=types,
            members=members,
        )
        return {"count": count}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
