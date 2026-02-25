"""MCP tools for DevRev incident operations (beta API)."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.incidents import IncidentSeverity, IncidentStage
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_incidents_list(
    ctx: Context,
    stage: list[str] | None = None,
    severity: list[str] | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev incidents.

    Args:
        stage: Filter by incident stage(s): ACKNOWLEDGED, IDENTIFIED, MITIGATED, RESOLVED.
        severity: Filter by severity level(s): SEV0, SEV1, SEV2, SEV3.
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        stages = None
        if stage:
            try:
                stages = [IncidentStage[s.upper()] for s in stage]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid incident stage: {e.args[0]}. "
                    f"Valid stages: {', '.join(t.name for t in IncidentStage)}"
                ) from e
        severities = None
        if severity:
            try:
                severities = [IncidentSeverity[s.upper()] for s in severity]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid incident severity: {e.args[0]}. "
                    f"Valid severities: {', '.join(t.name for t in IncidentSeverity)}"
                ) from e
        response = await app.get_client().incidents.list(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
            stage=stages,
            severity=severities,
        )
        items = serialize_models(response.incidents)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="incidents")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_incidents_get(
    ctx: Context,
    id: str,
) -> dict[str, Any]:
    """Get a DevRev incident by ID.

    Args:
        id: The incident ID.
    """
    app = ctx.request_context.lifespan_context
    try:
        incident = await app.get_client().incidents.get(id)
        return serialize_model(incident)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_incidents_create(
        ctx: Context,
        title: str,
        body: str | None = None,
        severity: str | None = None,
        owned_by: list[str] | None = None,
        applies_to_parts: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new DevRev incident.

        Args:
            title: The incident title.
            body: The incident description/body.
            severity: Severity level: SEV0, SEV1, SEV2, SEV3.
            owned_by: List of user IDs who own this incident.
            applies_to_parts: List of part IDs this incident applies to.
        """
        app = ctx.request_context.lifespan_context
        try:
            severity_enum = None
            if severity:
                try:
                    severity_enum = IncidentSeverity[severity.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid incident severity: {e.args[0]}. "
                        f"Valid severities: {', '.join(t.name for t in IncidentSeverity)}"
                    ) from e
            incident = await app.get_client().incidents.create(
                title=title,
                body=body,
                severity=severity_enum,
                owned_by=owned_by,
                applies_to_parts=applies_to_parts,
            )
            return serialize_model(incident)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_incidents_update(
        ctx: Context,
        id: str,
        title: str | None = None,
        body: str | None = None,
        stage: str | None = None,
        severity: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing DevRev incident.

        Only provided fields will be updated; others remain unchanged.

        Args:
            id: The incident ID to update.
            title: New incident title.
            body: New incident description/body.
            stage: New stage: ACKNOWLEDGED, IDENTIFIED, MITIGATED, RESOLVED.
            severity: New severity level: SEV0, SEV1, SEV2, SEV3.
        """
        app = ctx.request_context.lifespan_context
        try:
            stage_enum = None
            if stage:
                try:
                    stage_enum = IncidentStage[stage.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid incident stage: {e.args[0]}. "
                        f"Valid stages: {', '.join(t.name for t in IncidentStage)}"
                    ) from e
            severity_enum = None
            if severity:
                try:
                    severity_enum = IncidentSeverity[severity.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid incident severity: {e.args[0]}. "
                        f"Valid severities: {', '.join(t.name for t in IncidentSeverity)}"
                    ) from e
            incident = await app.get_client().incidents.update(
                id,
                title=title,
                body=body,
                stage=stage_enum,
                severity=severity_enum,
            )
            return serialize_model(incident)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_incidents_delete(
        ctx: Context,
        id: str,
    ) -> dict[str, Any]:
        """Delete a DevRev incident.

        Args:
            id: The incident ID to delete.
        """
        app = ctx.request_context.lifespan_context
        try:
            await app.get_client().incidents.delete(id)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_incidents_group(
        ctx: Context,
        group_by: str,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Group DevRev incidents by a specified field.

        Args:
            group_by: Field to group by (e.g., severity, stage, owned_by).
            limit: Maximum number of groups to return.
        """
        app = ctx.request_context.lifespan_context
        try:
            groups = await app.get_client().incidents.group(group_by=group_by, limit=limit)
            items = serialize_models(groups)
            return {"count": len(items), "groups": items}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
