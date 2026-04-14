"""MCP tools for DevRev rev org operations."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.don_id import validate_don_id
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_rev_orgs_list(
    ctx: Context[Any, Any, Any],
    account: list[str] | None = None,
    display_name: list[str] | None = None,
    domains: list[str] | None = None,
    owned_by: list[str] | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev rev orgs.

    Args:
        account: Filter by account ID(s).
        display_name: Filter by rev org display name(s).
        domains: Filter by domain(s).
        owned_by: Filter by owner user ID(s).
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        response = await app.get_client().rev_orgs.list(
            account=account,
            display_name=display_name,
            domains=domains,
            owned_by=owned_by,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        items = serialize_models(response.rev_orgs)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="rev_orgs")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_rev_orgs_get(
    ctx: Context[Any, Any, Any],
    id: str,
) -> dict[str, Any]:
    """Get a DevRev rev org by ID.

    Args:
        id: The rev org ID.
    """
    validate_don_id(id, "revo", "devrev_rev_orgs_get")
    app = ctx.request_context.lifespan_context
    try:
        rev_org = await app.get_client().rev_orgs.get(id)
        return serialize_model(rev_org)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_rev_orgs_create(
        ctx: Context[Any, Any, Any],
        display_name: str,
        account: str,
        description: str | None = None,
        external_ref: str | None = None,
        tier: str | None = None,
    ) -> dict[str, Any]:
        """Create a new rev org.

        Args:
            display_name: Display name for the rev org.
            account: Parent account ID.
            description: Rev org description.
            external_ref: External reference identifier.
            tier: Rev org tier.
        """
        app = ctx.request_context.lifespan_context
        try:
            rev_org = await app.get_client().rev_orgs.create(
                display_name=display_name,
                account=account,
                description=description,
                external_ref=external_ref,
                tier=tier,
            )
            return serialize_model(rev_org)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_rev_orgs_update(
        ctx: Context[Any, Any, Any],
        id: str,
        display_name: str | None = None,
        description: str | None = None,
        tier: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing rev org.

        Only provided fields will be updated; others remain unchanged.

        Args:
            id: The rev org ID to update.
            display_name: New display name.
            description: New description.
            tier: New tier.
        """
        validate_don_id(id, "revo", "devrev_rev_orgs_update")
        app = ctx.request_context.lifespan_context
        try:
            rev_org = await app.get_client().rev_orgs.update(
                id,
                display_name=display_name,
                description=description,
                tier=tier,
            )
            return serialize_model(rev_org)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_rev_orgs_delete(
        ctx: Context[Any, Any, Any],
        id: str,
    ) -> dict[str, Any]:
        """Delete a rev org.

        Args:
            id: The rev org ID to delete.
        """
        validate_don_id(id, "revo", "devrev_rev_orgs_delete")
        app = ctx.request_context.lifespan_context
        try:
            await app.get_client().rev_orgs.delete(id)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
