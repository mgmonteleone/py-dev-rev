"""DevRev MCP Server - Groups Tools.

This module provides MCP tools for managing DevRev groups and group memberships.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.groups import (
    GroupMembersAddRequest,
    GroupMembersListRequest,
    GroupMembersRemoveRequest,
    GroupsCreateRequest,
    GroupsGetRequest,
    GroupsListRequest,
    GroupsUpdateRequest,
    GroupType,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_groups_list(
    ctx: Context, cursor: str | None = None, limit: int | None = None
) -> dict[str, Any]:
    """List all groups in the DevRev organization.

    Args:
        ctx: MCP context containing the DevRev client.
        cursor: Optional pagination cursor.
        limit: Optional maximum number of groups to return.

    Returns:
        Dictionary with count and list of groups.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = GroupsListRequest(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        groups = await app.get_client().groups.list(request)
        items = serialize_models(list(groups))
        return {"count": len(items), "groups": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_groups_get(ctx: Context, id: str) -> dict[str, Any]:
    """Get a specific group by ID.

    Args:
        ctx: MCP context containing the DevRev client.
        id: The group ID.

    Returns:
        The group details.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = GroupsGetRequest(id=id)
        group = await app.get_client().groups.get(request)
        return serialize_model(group)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_groups_create(
        ctx: Context,
        name: str,
        description: str | None = None,
        type: str | None = None,
    ) -> dict[str, Any]:
        """Create a new group.

        Args:
            ctx: MCP context containing the DevRev client.
            name: The group name.
            description: Optional group description.
            type: Optional group type (STATIC or DYNAMIC).

        Returns:
            The created group details.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            group_type = None
            if type:
                try:
                    group_type = GroupType[type.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid group type: {e.args[0]}. "
                        f"Valid types: {', '.join(t.name for t in GroupType)}"
                    ) from e
            request = GroupsCreateRequest(name=name, description=description, type=group_type)
            group = await app.get_client().groups.create(request)
            return serialize_model(group)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_groups_update(
        ctx: Context,
        id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing group.

        Args:
            ctx: MCP context containing the DevRev client.
            id: The group ID.
            name: Optional new group name.
            description: Optional new group description.

        Returns:
            The updated group details.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = GroupsUpdateRequest(id=id, name=name, description=description)
            group = await app.get_client().groups.update(request)
            return serialize_model(group)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_groups_add_member(ctx: Context, group: str, member: str) -> dict[str, Any]:
        """Add a member to a group.

        Args:
            ctx: MCP context containing the DevRev client.
            group: The group ID.
            member: The member ID to add.

        Returns:
            Confirmation dictionary with added status.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = GroupMembersAddRequest(group=group, member=member)
            await app.get_client().groups.add_member(request)
            return {"added": True, "group": group, "member": member}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_groups_remove_member(ctx: Context, group: str, member: str) -> dict[str, Any]:
        """Remove a member from a group.

        Args:
            ctx: MCP context containing the DevRev client.
            group: The group ID.
            member: The member ID to remove.

        Returns:
            Confirmation dictionary with removed status.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = GroupMembersRemoveRequest(group=group, member=member)
            await app.get_client().groups.remove_member(request)
            return {"removed": True, "group": group, "member": member}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_groups_list_members(
    ctx: Context, group: str, cursor: str | None = None, limit: int | None = None
) -> dict[str, Any]:
    """List members of a group.

    Args:
        ctx: MCP context containing the DevRev client.
        group: The group ID.
        cursor: Optional pagination cursor.
        limit: Optional maximum number of members to return.

    Returns:
        Dictionary with count and list of group members.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = GroupMembersListRequest(
            group=group,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        members = await app.get_client().groups.list_members(request)
        items = serialize_models(list(members))
        return {"count": len(items), "members": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_groups_members_count(ctx: Context, group_id: str) -> dict[str, Any]:
    """Get the count of members in a group (beta feature).

    Args:
        ctx: MCP context containing the DevRev client.
        group_id: The group ID.

    Returns:
        Dictionary with the member count.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        count = await app.get_client().groups.members_count(group_id=group_id)
        return {"count": count}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
