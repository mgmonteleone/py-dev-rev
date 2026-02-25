"""MCP tools for DevRev user operations (dev users and rev users)."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.dev_users import DevUserState
from devrev_mcp.server import mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_dev_users_list(
    ctx: Context[Any, Any, Any],
    email: list[str] | None = None,
    state: list[str] | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev developer users.

    Args:
        email: Filter by email address(es).
        state: Filter by state(s): ACTIVE, DEACTIVATED, SHADOW.
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        user_states = [DevUserState(s.lower()) for s in state] if state else None
        response = await app.get_client().dev_users.list(
            email=email,
            state=user_states,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        items = serialize_models(response.dev_users)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="dev_users")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_dev_users_get(
    ctx: Context[Any, Any, Any],
    id: str,
) -> dict[str, Any]:
    """Get a DevRev developer user by ID.

    Args:
        id: The dev user ID.
    """
    app = ctx.request_context.lifespan_context
    try:
        user = await app.get_client().dev_users.get(id)
        return serialize_model(user)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_rev_users_list(
    ctx: Context[Any, Any, Any],
    email: list[str] | None = None,
    rev_org: list[str] | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev customer (rev) users.

    Args:
        email: Filter by email address(es).
        rev_org: Filter by rev org ID(s).
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        response = await app.get_client().rev_users.list(
            email=email,
            rev_org=rev_org,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        items = serialize_models(response.rev_users)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="rev_users")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_rev_users_get(
    ctx: Context[Any, Any, Any],
    id: str,
) -> dict[str, Any]:
    """Get a DevRev customer (rev) user by ID.

    Args:
        id: The rev user ID.
    """
    app = ctx.request_context.lifespan_context
    try:
        user = await app.get_client().rev_users.get(id)
        return serialize_model(user)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_rev_users_create(
    ctx: Context[Any, Any, Any],
    rev_org: str,
    display_name: str | None = None,
    email: str | None = None,
    phone_numbers: list[str] | None = None,
    external_ref: str | None = None,
) -> dict[str, Any]:
    """Create a new DevRev customer (rev) user.

    Args:
        rev_org: The rev org ID to associate the user with.
        display_name: Display name for the user.
        email: Email address.
        phone_numbers: List of phone numbers.
        external_ref: External reference ID.
    """
    app = ctx.request_context.lifespan_context
    try:
        user = await app.get_client().rev_users.create(
            rev_org=rev_org,
            display_name=display_name,
            email=email,
            phone_numbers=phone_numbers,
            external_ref=external_ref,
        )
        return serialize_model(user)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
