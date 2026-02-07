"""MCP tools for DevRev account operations."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev_mcp.server import mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_accounts_list(
    ctx: Context,
    display_name: list[str] | None = None,
    domains: list[str] | None = None,
    owned_by: list[str] | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev accounts.

    Args:
        display_name: Filter by account display name(s).
        domains: Filter by domain(s).
        owned_by: Filter by owner user ID(s).
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        response = await app.client.accounts.list(
            display_name=display_name,
            domains=domains,
            owned_by=owned_by,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        items = serialize_models(response.accounts)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="accounts")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_accounts_get(
    ctx: Context,
    id: str,
) -> dict[str, Any]:
    """Get a DevRev account by ID.

    Args:
        id: The account ID.
    """
    app = ctx.request_context.lifespan_context
    try:
        account = await app.client.accounts.get(id)
        return serialize_model(account)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_accounts_create(
    ctx: Context,
    display_name: str,
    description: str | None = None,
    domains: list[str] | None = None,
    external_refs: list[str] | None = None,
    owned_by: list[str] | None = None,
    tier: str | None = None,
) -> dict[str, Any]:
    """Create a new DevRev account.

    Args:
        display_name: Display name for the account.
        description: Account description.
        domains: List of domains associated with the account.
        external_refs: External reference IDs.
        owned_by: List of owner user IDs.
        tier: Account tier.
    """
    app = ctx.request_context.lifespan_context
    try:
        account = await app.client.accounts.create(
            display_name=display_name,
            description=description,
            domains=domains,
            external_refs=external_refs,
            owned_by=owned_by,
            tier=tier,
        )
        return serialize_model(account)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_accounts_update(
    ctx: Context,
    id: str,
    display_name: str | None = None,
    description: str | None = None,
    tier: str | None = None,
) -> dict[str, Any]:
    """Update an existing DevRev account.

    Only provided fields will be updated; others remain unchanged.

    Args:
        id: The account ID to update.
        display_name: New display name.
        description: New description.
        tier: New account tier.
    """
    app = ctx.request_context.lifespan_context
    try:
        account = await app.client.accounts.update(
            id,
            display_name=display_name,
            description=description,
            tier=tier,
        )
        return serialize_model(account)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_accounts_delete(
    ctx: Context,
    id: str,
) -> dict[str, Any]:
    """Delete a DevRev account.

    Args:
        id: The account ID to delete.
    """
    app = ctx.request_context.lifespan_context
    try:
        await app.client.accounts.delete(id)
        return {"deleted": True, "id": id}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_accounts_merge(
    ctx: Context,
    primary_account: str,
    secondary_account: str,
) -> dict[str, Any]:
    """Merge two DevRev accounts into one.

    The secondary account will be merged into the primary account.

    Args:
        primary_account: ID of the primary (surviving) account.
        secondary_account: ID of the secondary (merged) account.
    """
    app = ctx.request_context.lifespan_context
    try:
        account = await app.client.accounts.merge(
            primary_account=primary_account,
            secondary_account=secondary_account,
        )
        return serialize_model(account)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
