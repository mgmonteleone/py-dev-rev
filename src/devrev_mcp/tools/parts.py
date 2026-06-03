"""DevRev MCP Server - Parts Tools.

This module provides MCP tools for managing DevRev parts (products, capabilities,
features, and enhancements).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.base import ObjectSummary
from devrev.models.links import (
    Link,
    LinksCreateRequest,
    LinksDeleteRequest,
    LinksListRequest,
)
from devrev.models.parts import (
    Part,
    PartsCreateRequest,
    PartsDeleteRequest,
    PartsGetRequest,
    PartsUpdateRequest,
    PartType,
)
from devrev.models.tags import Tag
from devrev.models.works import Work
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.don_id import validate_don_id
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)

# Bound for recursive child re-creation to guard against cycles / runaway depth.
_MAX_MOVE_DEPTH = 20


# ---------------------------------------------------------------------------
# Helpers for the part-move workaround.
#
# The DevRev public API cannot change a part's parent via parts.update, so
# re-parenting is implemented by recreating the part under the new parent and
# relinking the references the API does let us move (work items and links).
# These small, pure helpers are unit-tested directly.
# ---------------------------------------------------------------------------


def _extract_owner_ids(part: Part) -> list[str]:
    """Return the owner user IDs for a part (empty list when unset)."""
    if not part.owned_by:
        return []
    return [owner.id for owner in part.owned_by]


def _extract_tag_ids(part: Part) -> list[str]:
    """Return the tag IDs for a part (empty list when unset).

    ``Part.tags`` holds ``TagWithValue`` entries whose ``tag`` field is either a
    full ``Tag`` model (responses) or a raw tag-ID string. Only the tag IDs can
    be supplied back to ``parts.create``; tag values are not preserved.
    """
    if not part.tags:
        return []
    tag_ids: list[str] = []
    for entry in part.tags:
        tag = entry.tag
        tag_ids.append(tag.id if isinstance(tag, Tag) else tag)
    return tag_ids


def _extract_object_id(obj: str | ObjectSummary | dict[str, Any]) -> str | None:
    """Return the object ID from a link source/target value.

    Link endpoints come back as a raw ID string, an ``ObjectSummary``, or a
    plain dict depending on the API response shape.
    """
    if isinstance(obj, str):
        return obj
    if isinstance(obj, ObjectSummary):
        return obj.id
    if isinstance(obj, dict):
        value = obj.get("id")
        return value if isinstance(value, str) else None
    return None


def _replace_link_endpoint(link: Link, old_id: str, new_id: str) -> tuple[str, str] | None:
    """Compute the (source, target) IDs for an equivalent link after a move.

    Replaces whichever endpoint equals ``old_id`` with ``new_id``. Returns
    ``None`` when neither endpoint matches ``old_id`` (the link cannot be
    safely recreated and should be skipped, not dropped silently).
    """
    source_id = _extract_object_id(link.source)
    target_id = _extract_object_id(link.target)
    if source_id is None or target_id is None:
        return None
    if source_id == old_id:
        return new_id, target_id
    if target_id == old_id:
        return source_id, new_id
    return None


@dataclass
class _MovePlanNode:
    """A node in the part-move plan: a part plus the references to migrate."""

    source_part: Part
    works: list[Work]
    links: list[Link]
    children: list[_MovePlanNode]


@dataclass
class _MoveResult:
    """Accumulates operations, counts, and warnings across a move."""

    planned: list[dict[str, Any]] = field(default_factory=list)
    completed: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    unsupported_children: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    counts: dict[str, int] = field(
        default_factory=lambda: {
            "child_parts_found": 0,
            "work_items_found": 0,
            "links_found": 0,
            "parts_created": 0,
            "works_relinked": 0,
            "links_recreated": 0,
            "links_skipped": 0,
            "parts_deleted": 0,
        }
    )


async def _gather_child_parts(client: Any, part_id: str) -> list[Part]:
    """Return the direct child parts of ``part_id`` via parts.list pagination."""
    children: list[Part] = []
    cursor: str | None = None
    while True:
        response = await client.parts.list(
            parent_part_parts=[part_id], parent_part_level=1, cursor=cursor
        )
        for child in response.parts:
            if child.id != part_id:
                children.append(child)
        cursor = response.next_cursor
        if not cursor:
            break
    return children


async def _gather_part_works(client: Any, part_id: str) -> list[Work]:
    """Return all work items that apply to ``part_id`` via works.list pagination."""
    works: list[Work] = []
    cursor: str | None = None
    while True:
        response = await client.works.list(applies_to_part=[part_id], cursor=cursor)
        works.extend(response.works)
        cursor = response.next_cursor
        if not cursor:
            break
    return works


async def _gather_part_links(client: Any, part_id: str) -> list[Link]:
    """Return the links attached to ``part_id``."""
    links = await client.links.list(LinksListRequest(object=part_id))
    return list(links)


async def _build_move_plan(
    client: Any,
    part: Part,
    *,
    recreate_children: bool,
    result: _MoveResult,
    depth: int = 0,
) -> _MovePlanNode:
    """Read-only traversal building the move plan and detecting blockers.

    Gathers the part's work items, links, and (optionally, recursively) child
    parts. Child parts are only planned when ``recreate_children`` is true;
    otherwise they are recorded under ``unsupported_children`` so callers can
    block before any mutation. Parts without a resolvable type are recorded as
    blockers since ``parts.create`` requires a type.
    """
    if part.type is None:
        result.blockers.append(f"Part {part.id} has no type; cannot recreate it.")

    works = await _gather_part_works(client, part.id)
    links = await _gather_part_links(client, part.id)
    child_parts = await _gather_child_parts(client, part.id)

    result.counts["work_items_found"] += len(works)
    result.counts["links_found"] += len(links)
    result.counts["child_parts_found"] += len(child_parts)

    children_nodes: list[_MovePlanNode] = []
    if child_parts:
        if not recreate_children:
            result.unsupported_children.extend(child.id for child in child_parts)
        elif depth + 1 > _MAX_MOVE_DEPTH:
            result.blockers.append(
                f"Maximum move depth ({_MAX_MOVE_DEPTH}) exceeded at part {part.id}."
            )
            result.unsupported_children.extend(child.id for child in child_parts)
        else:
            for child in child_parts:
                children_nodes.append(
                    await _build_move_plan(
                        client,
                        child,
                        recreate_children=recreate_children,
                        result=result,
                        depth=depth + 1,
                    )
                )

    return _MovePlanNode(source_part=part, works=works, links=links, children=children_nodes)


def _record_planned_operations(
    node: _MovePlanNode, target_parent_id: str, result: _MoveResult
) -> None:
    """Append a human-readable description of the planned mutations (no I/O)."""
    source_id = node.source_part.id
    placeholder = f"<new-part-for:{source_id}>"
    result.planned.append(
        {
            "op": "create_part",
            "source_part_id": source_id,
            "name": node.source_part.name,
            "type": node.source_part.type.value if node.source_part.type else None,
            "parent_part": target_parent_id,
            "new_part_id": placeholder,
        }
    )
    for work in node.works:
        result.planned.append(
            {
                "op": "relink_work",
                "work_id": work.id,
                "from_part": source_id,
                "to_part": placeholder,
            }
        )
    for link in node.links:
        replaced = _replace_link_endpoint(link, source_id, placeholder)
        if replaced is None:
            result.skipped.append(
                {
                    "op": "recreate_link",
                    "link_id": link.id,
                    "reason": "source part is not an endpoint of this link",
                }
            )
            continue
        new_source, new_target = replaced
        result.planned.append(
            {
                "op": "create_link",
                "link_type": link.link_type,
                "source": new_source,
                "target": new_target,
                "replaces_link_id": link.id,
            }
        )
        result.planned.append({"op": "delete_link", "link_id": link.id})
    for child in node.children:
        _record_planned_operations(child, placeholder, result)


async def _execute_move(
    client: Any, node: _MovePlanNode, target_parent_id: str, result: _MoveResult
) -> Part:
    """Perform the planned mutations for ``node`` and recurse into children.

    Returns the newly created part. Links are recreated before the old link is
    deleted so a partial failure never drops a relationship.
    """
    part = node.source_part
    created: Part = await client.parts.create(
        PartsCreateRequest(
            name=part.name,
            type=part.type,
            description=part.description,
            owned_by=_extract_owner_ids(part) or None,
            parent_part=[target_parent_id],
            tags=_extract_tag_ids(part) or None,
        )
    )
    new_id = created.id
    result.completed.append(
        {
            "op": "create_part",
            "source_part_id": part.id,
            "new_part_id": new_id,
            "parent_part": target_parent_id,
        }
    )
    result.counts["parts_created"] += 1

    for work in node.works:
        await client.works.update(work.id, applies_to_part=new_id)
        result.completed.append({"op": "relink_work", "work_id": work.id, "to_part": new_id})
        result.counts["works_relinked"] += 1

    for link in node.links:
        replaced = _replace_link_endpoint(link, part.id, new_id)
        if replaced is None:
            result.skipped.append(
                {
                    "op": "recreate_link",
                    "link_id": link.id,
                    "reason": "source part is not an endpoint of this link",
                }
            )
            result.counts["links_skipped"] += 1
            continue
        new_source, new_target = replaced
        await client.links.create(
            LinksCreateRequest(link_type=link.link_type, source=new_source, target=new_target)
        )
        result.completed.append(
            {
                "op": "create_link",
                "link_type": link.link_type,
                "source": new_source,
                "target": new_target,
                "replaces_link_id": link.id,
            }
        )
        await client.links.delete(LinksDeleteRequest(id=link.id))
        result.completed.append({"op": "delete_link", "link_id": link.id})
        result.counts["links_recreated"] += 1

    for child in node.children:
        await _execute_move(client, child, new_id, result)

    return created


def _collect_old_ids_postorder(node: _MovePlanNode) -> list[str]:
    """Return original part IDs in post-order (children before their parent)."""
    ids: list[str] = []
    for child in node.children:
        ids.extend(_collect_old_ids_postorder(child))
    ids.append(node.source_part.id)
    return ids


@mcp.tool()
async def devrev_parts_list(
    ctx: Context[Any, Any, Any], cursor: str | None = None, limit: int | None = None
) -> dict[str, Any]:
    """List DevRev parts (products, capabilities, features, enhancements).

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).

    Returns:
        Dictionary containing list of parts and pagination info.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        response = await app.get_client().parts.list(
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
            cursor=cursor,
        )
        items = serialize_models(response.parts)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="parts")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_parts_get(ctx: Context[Any, Any, Any], id: str) -> dict[str, Any]:
    """Get a specific DevRev part by ID.

    Args:
        id: The ID of the part to retrieve.

    Returns:
        Dictionary containing the part details.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    validate_don_id(id, "part", "devrev_parts_get")
    app = ctx.request_context.lifespan_context
    try:
        part = await app.get_client().parts.get(PartsGetRequest(id=id))
        return serialize_model(part)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_parts_create(
        ctx: Context[Any, Any, Any],
        name: str,
        type: str,
        description: str | None = None,
        owned_by: list[str] | None = None,
        parent_part: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new DevRev part.

        Args:
            name: The name of the part.
            type: The type of part (PRODUCT, CAPABILITY, FEATURE, ENHANCEMENT).
            description: Optional description of the part.
            owned_by: List of owner user IDs (e.g., ["DEVU-4"] or full DON IDs).
            parent_part: Parent part ID (required for capability/feature/enhancement).
                Array with at most 1 element.
            tags: List of tag IDs to associate with the part.

        Returns:
            Dictionary containing the created part details.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            try:
                part_type = PartType[type.upper()]
            except KeyError as e:
                raise RuntimeError(
                    f"Invalid part type: {e.args[0]}. "
                    f"Valid types: {', '.join(t.name for t in PartType)}"
                ) from e
            # Validate parent_part is provided for non-product parts
            if part_type != PartType.PRODUCT and not parent_part:
                raise RuntimeError(
                    f"parent_part is required when creating a {part_type.name} part. "
                    "Only PRODUCT parts can be created without a parent."
                )
            request = PartsCreateRequest(
                name=name,
                type=part_type,
                description=description,
                owned_by=owned_by,
                parent_part=parent_part,
                tags=tags,
            )
            part = await app.get_client().parts.create(request)
            return serialize_model(part)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_parts_update(
        ctx: Context[Any, Any, Any],
        id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing DevRev part.

        Args:
            id: The ID of the part to update.
            name: Optional new name for the part.
            description: Optional new description for the part.

        Returns:
            Dictionary containing the updated part details.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        validate_don_id(id, "part", "devrev_parts_update")
        app = ctx.request_context.lifespan_context
        try:
            request = PartsUpdateRequest(
                id=id,
                name=name,
                description=description,
            )
            part = await app.get_client().parts.update(request)
            return serialize_model(part)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_parts_delete(ctx: Context[Any, Any, Any], id: str) -> dict[str, Any]:
        """Delete a DevRev part.

        Args:
            id: The ID of the part to delete.

        Returns:
            Dictionary confirming the deletion.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        validate_don_id(id, "part", "devrev_parts_delete")
        app = ctx.request_context.lifespan_context
        try:
            await app.get_client().parts.delete(PartsDeleteRequest(id=id))
            return {"success": True, "message": f"Part {id} deleted successfully"}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_parts_move(
        ctx: Context[Any, Any, Any],
        source_part_id: str,
        new_parent_part_id: str,
        dry_run: bool = True,
        confirm: bool = False,
        delete_original: bool = False,
        recreate_children: bool = False,
    ) -> dict[str, Any]:
        """Re-parent a DevRev part by recreating it under a new parent.

        The DevRev public API cannot change ``parent_part`` via ``parts.update``,
        so this tool performs a safe workaround: it creates a replacement part of
        the same type under ``new_parent_part_id`` (preserving name, description,
        owner IDs, and tag IDs), relinks work items, recreates links pointing at
        the part, and optionally deletes the original.

        This is a destructive, multi-step operation. It defaults to a dry run and
        will not mutate anything unless ``dry_run`` is False AND ``confirm`` is
        True. If the source part has child parts and ``recreate_children`` is
        False, execution is blocked before any mutation (children are reported
        under ``unsupported_children``) so nothing is silently dropped.

        Args:
            source_part_id: The part to move.
            new_parent_part_id: The new parent part the replacement is created under.
            dry_run: When True (default), only gather state and report the plan.
            confirm: Must be True (with dry_run False) to perform mutations.
            delete_original: When True, delete the original part(s) after all
                create/relink operations succeed. Defaults to False (left in place).
            recreate_children: When True, recursively recreate direct child parts
                under the moved part. When False (default), child parts block
                execution rather than being dropped.

        Returns:
            A structured dict with dry_run, source_part, new_parent_part,
            created_part, new_part_id, counts, planned_operations,
            completed_operations, skipped_operations, warnings,
            unsupported_children, blockers, and success.

        Raises:
            RuntimeError: If a DevRev API call fails.
        """
        validate_don_id(source_part_id, "part", "devrev_parts_move")
        validate_don_id(new_parent_part_id, "part", "devrev_parts_move")
        app = ctx.request_context.lifespan_context
        try:
            client = app.get_client()
            source_part = await client.parts.get(PartsGetRequest(id=source_part_id))
            new_parent_part = await client.parts.get(PartsGetRequest(id=new_parent_part_id))

            result = _MoveResult()
            plan = await _build_move_plan(
                client, source_part, recreate_children=recreate_children, result=result
            )
            _record_planned_operations(plan, new_parent_part_id, result)

            if result.unsupported_children:
                result.warnings.append(
                    "Source part has child parts. Set recreate_children=True to move them; "
                    "otherwise execution is blocked to avoid orphaning children."
                )

            has_blockers = bool(result.unsupported_children) or bool(result.blockers)

            response: dict[str, Any] = {
                "dry_run": dry_run,
                "source_part": serialize_model(source_part),
                "new_parent_part": serialize_model(new_parent_part),
                "created_part": None,
                "new_part_id": None,
                "counts": result.counts,
                "planned_operations": result.planned,
                "completed_operations": result.completed,
                "skipped_operations": result.skipped,
                "warnings": result.warnings,
                "unsupported_children": result.unsupported_children,
                "blockers": result.blockers,
            }

            if dry_run:
                response["success"] = True
                return response

            if not confirm:
                result.warnings.append("Mutation requires confirm=True. No changes were made.")
                response["success"] = False
                return response

            if has_blockers:
                result.warnings.append(
                    "Execution blocked by unsupported children or missing data. "
                    "No changes were made."
                )
                response["success"] = False
                return response

            created_root = await _execute_move(client, plan, new_parent_part_id, result)
            response["created_part"] = serialize_model(created_root)
            response["new_part_id"] = created_root.id

            if delete_original:
                for old_id in _collect_old_ids_postorder(plan):
                    await client.parts.delete(PartsDeleteRequest(id=old_id))
                    result.completed.append({"op": "delete_part", "part_id": old_id})
                    result.counts["parts_deleted"] += 1
            else:
                result.warnings.append(
                    f"Original part {source_part_id} left in place (delete_original=False)."
                )

            response["success"] = True
            return response
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
