"""MCP tools for DevRev SLA operations."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.slas import (
    SlasCreateRequest,
    SlasGetRequest,
    SlasListRequest,
    SlaStatus,
    SlasTransitionRequest,
    SlasUpdateRequest,
    SlaTrackerStatus,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_slas_list(
    ctx: Context[Any, Any, Any],
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev SLAs.

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        request = SlasListRequest(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        slas = await app.get_client().slas.list(request)
        items = serialize_models(list(slas))
        return {"count": len(items), "slas": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_slas_get(
    ctx: Context[Any, Any, Any],
    id: str,
) -> dict[str, Any]:
    """Get a DevRev SLA by ID.

    Args:
        id: SLA ID (e.g., "don:core:dvrv-us-1:devo/1:sla/123").
    """
    app = ctx.request_context.lifespan_context
    try:
        request = SlasGetRequest(id=id)
        sla = await app.get_client().slas.get(request)
        return serialize_model(sla)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_slas_create(
        ctx: Context[Any, Any, Any],
        name: str,
        description: str | None = None,
        target_time: int | None = None,
    ) -> dict[str, Any]:
        """Create a new DevRev SLA.

        Args:
            name: SLA name.
            description: SLA description.
            target_time: Target time in minutes.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = SlasCreateRequest(name=name, description=description, target_time=target_time)
            sla = await app.get_client().slas.create(request)
            return serialize_model(sla)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_slas_update(
        ctx: Context[Any, Any, Any],
        id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update a DevRev SLA.

        Args:
            id: SLA ID to update.
            name: New SLA name.
            description: New SLA description.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = SlasUpdateRequest(id=id, name=name, description=description)
            sla = await app.get_client().slas.update(request)
            return serialize_model(sla)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_slas_transition(
        ctx: Context[Any, Any, Any],
        id: str,
        status: str,
    ) -> dict[str, Any]:
        """Transition a DevRev SLA status.

        Args:
            id: SLA ID to transition.
            status: New status (draft, published, archived, active, paused, breached, completed).
        """
        app = ctx.request_context.lifespan_context
        try:
            # Try SlaStatus first, then SlaTrackerStatus, then use raw string
            resolved_status: SlaStatus | SlaTrackerStatus | str
            try:
                resolved_status = SlaStatus[status.upper()]
            except KeyError:
                try:
                    resolved_status = SlaTrackerStatus[status.upper()]
                except KeyError:
                    resolved_status = status

            request = SlasTransitionRequest(id=id, status=resolved_status)
            sla = await app.get_client().slas.transition(request)
            return serialize_model(sla)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
