"""MCP tools for DevRev webhook operations."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.webhooks import (
    WebhooksCreateRequest,
    WebhooksDeleteRequest,
    WebhooksGetRequest,
    WebhooksListRequest,
    WebhookStatus,
    WebhooksUpdateRequest,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.don_id import validate_don_id
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_webhooks_list(
    ctx: Context[Any, Any, Any],
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev webhooks.

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        request = WebhooksListRequest(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        webhooks = await app.get_client().webhooks.list(request)
        items = serialize_models(list(webhooks))
        return {"count": len(items), "webhooks": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_webhooks_get(
    ctx: Context[Any, Any, Any],
    id: str,
) -> dict[str, Any]:
    """Get a DevRev webhook by ID.

    Args:
        id: Webhook ID (e.g., "don:integration:dvrv-us-1:devo/1:webhook/123").
    """
    validate_don_id(id, "webhook", "devrev_webhooks_get")
    app = ctx.request_context.lifespan_context
    try:
        request = WebhooksGetRequest(id=id)
        webhook = await app.get_client().webhooks.get(request)
        return serialize_model(webhook)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_webhooks_create(
        ctx: Context[Any, Any, Any],
        url: str,
        event_types: list[str] | None = None,
        secret: str | None = None,
    ) -> dict[str, Any]:
        """Create a new DevRev webhook.

        Args:
            url: Target URL that will receive webhook event POSTs.
            event_types: Event types to subscribe to (default: all events).
            secret: Shared secret used to sign and verify webhook payloads.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = WebhooksCreateRequest(url=url, event_types=event_types, secret=secret)
            webhook = await app.get_client().webhooks.create(request)
            return serialize_model(webhook)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_webhooks_update(
        ctx: Context[Any, Any, Any],
        id: str,
        url: str | None = None,
        event_types: list[str] | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Update a DevRev webhook.

        Args:
            id: Webhook ID to update.
            url: New target URL.
            event_types: New list of event types to subscribe to.
            status: New status (active, inactive, unverified).
        """
        validate_don_id(id, "webhook", "devrev_webhooks_update")
        app = ctx.request_context.lifespan_context
        try:
            resolved_status: WebhookStatus | None = None
            if status is not None:
                try:
                    resolved_status = WebhookStatus(status.lower())
                except ValueError as e:
                    raise RuntimeError(
                        f"Invalid webhook status '{status}'. "
                        "Valid values: active, inactive, unverified."
                    ) from e
            request = WebhooksUpdateRequest(
                id=id, url=url, event_types=event_types, status=resolved_status
            )
            webhook = await app.get_client().webhooks.update(request)
            return serialize_model(webhook)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_webhooks_delete(
        ctx: Context[Any, Any, Any],
        id: str,
    ) -> dict[str, Any]:
        """Delete a DevRev webhook.

        Args:
            id: Webhook ID to delete.
        """
        validate_don_id(id, "webhook", "devrev_webhooks_delete")
        app = ctx.request_context.lifespan_context
        try:
            request = WebhooksDeleteRequest(id=id)
            await app.get_client().webhooks.delete(request)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
