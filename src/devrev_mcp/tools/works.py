"""MCP tools for DevRev work item operations."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.works import IssuePriority, TicketSeverity, WorkType
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_works_list(
    ctx: Context[Any, Any, Any],
    type: list[str] | None = None,
    applies_to_part: list[str] | None = None,
    owned_by: list[str] | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev work items (tickets, issues, tasks).

    Args:
        type: Filter by work type(s): TICKET, ISSUE, TASK, OPPORTUNITY.
        applies_to_part: Filter by part ID(s) the work applies to.
        owned_by: Filter by owner user ID(s).
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        # Convert work type strings to enum, catching invalid values
        work_types = None
        if type:
            try:
                work_types = [WorkType[t.upper()] for t in type]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid work type: {e.args[0]}. "
                    f"Valid types: {', '.join(wt.name for wt in WorkType)}"
                ) from e
        response = await app.get_client().works.list(
            type=work_types,
            applies_to_part=applies_to_part,
            owned_by=owned_by,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        items = serialize_models(response.works)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="works")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_works_get(
    ctx: Context[Any, Any, Any],
    id: str,
) -> dict[str, Any]:
    """Get a DevRev work item by ID.

    Args:
        id: The work item ID (e.g., don:core:dvrv-us-1:devo/1:issue/123).
    """
    app = ctx.request_context.lifespan_context
    try:
        work = await app.get_client().works.get(id)
        return serialize_model(work)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_works_create(
        ctx: Context[Any, Any, Any],
        title: str,
        applies_to_part: str,
        type: str,
        owned_by: list[str],
        body: str | None = None,
        priority: str | None = None,
        severity: str | None = None,
    ) -> dict[str, Any]:
        """Create a new DevRev work item (ticket, issue, or task).

        Args:
            title: Title of the work item.
            applies_to_part: Part ID the work applies to.
            type: Work type: TICKET, ISSUE, TASK, or OPPORTUNITY.
            owned_by: List of user IDs who own this work item.
            body: Description/body of the work item.
            priority: Issue priority: P0, P1, P2, P3.
            severity: Ticket severity: BLOCKER, HIGH, MEDIUM, LOW.
        """
        app = ctx.request_context.lifespan_context
        try:
            # Convert enum strings, catching invalid values
            try:
                work_type = WorkType[type.upper()]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid work type: {e.args[0]}. "
                    f"Valid types: {', '.join(wt.name for wt in WorkType)}"
                ) from e

            issue_priority = None
            if priority:
                try:
                    issue_priority = IssuePriority[priority.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid priority: {e.args[0]}. "
                        f"Valid priorities: {', '.join(p.name for p in IssuePriority)}"
                    ) from e

            ticket_severity = None
            if severity:
                try:
                    ticket_severity = TicketSeverity[severity.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid severity: {e.args[0]}. "
                        f"Valid severities: {', '.join(s.name for s in TicketSeverity)}"
                    ) from e

            work = await app.get_client().works.create(
                title=title,
                applies_to_part=applies_to_part,
                type=work_type,
                owned_by=owned_by,
                body=body,
                priority=issue_priority,
                severity=ticket_severity,
            )
            return serialize_model(work)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_works_update(
        ctx: Context[Any, Any, Any],
        id: str,
        title: str | None = None,
        body: str | None = None,
        owned_by: list[str] | None = None,
        priority: str | None = None,
        severity: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing DevRev work item.

        Only provided fields will be updated; others remain unchanged.

        Args:
            id: The work item ID to update.
            title: New title for the work item.
            body: New description/body.
            owned_by: New list of owner user IDs.
            priority: New issue priority: P0, P1, P2, P3.
            severity: New ticket severity: BLOCKER, HIGH, MEDIUM, LOW.
        """
        app = ctx.request_context.lifespan_context
        try:
            # Convert enum strings, catching invalid values
            issue_priority = None
            if priority:
                try:
                    issue_priority = IssuePriority[priority.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid priority: {e.args[0]}. "
                        f"Valid priorities: {', '.join(p.name for p in IssuePriority)}"
                    ) from e

            ticket_severity = None
            if severity:
                try:
                    ticket_severity = TicketSeverity[severity.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid severity: {e.args[0]}. "
                        f"Valid severities: {', '.join(s.name for s in TicketSeverity)}"
                    ) from e

            work = await app.get_client().works.update(
                id,
                title=title,
                body=body,
                owned_by=owned_by,
                priority=issue_priority,
                severity=ticket_severity,
            )
            return serialize_model(work)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_works_delete(
        ctx: Context[Any, Any, Any],
        id: str,
    ) -> dict[str, Any]:
        """Delete a DevRev work item.

        Args:
            id: The work item ID to delete.
        """
        app = ctx.request_context.lifespan_context
        try:
            await app.get_client().works.delete(id)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_works_count(
    ctx: Context[Any, Any, Any],
    type: list[str] | None = None,
    owned_by: list[str] | None = None,
) -> dict[str, Any]:
    """Count DevRev work items matching filters.

    Args:
        type: Filter by work type(s): TICKET, ISSUE, TASK, OPPORTUNITY.
        owned_by: Filter by owner user ID(s).
    """
    app = ctx.request_context.lifespan_context
    try:
        # Convert work type strings to enum, catching invalid values
        work_types = None
        if type:
            try:
                work_types = [WorkType[t.upper()] for t in type]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid work type: {e.args[0]}. "
                    f"Valid types: {', '.join(wt.name for wt in WorkType)}"
                ) from e
        count = await app.get_client().works.count(type=work_types, owned_by=owned_by)
        return {"count": count}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_works_export(
    ctx: Context[Any, Any, Any],
    type: list[str] | None = None,
    first: int | None = None,
) -> dict[str, Any]:
    """Export DevRev work items.

    Returns a bulk export of work items. Use for large data retrieval.

    Args:
        type: Filter by work type(s): TICKET, ISSUE, TASK, OPPORTUNITY.
        first: Maximum number of items to export.
    """
    app = ctx.request_context.lifespan_context
    try:
        # Convert work type strings to enum, catching invalid values
        work_types = None
        if type:
            try:
                work_types = [WorkType[t.upper()] for t in type]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid work type: {e.args[0]}. "
                    f"Valid types: {', '.join(wt.name for wt in WorkType)}"
                ) from e
        works = await app.get_client().works.export(type=work_types, first=first)
        items = serialize_models(list(works))
        return {"count": len(items), "works": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
