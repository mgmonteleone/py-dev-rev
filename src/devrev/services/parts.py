"""Parts service for DevRev SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING

from devrev.exceptions import DevRevError
from devrev.models.base import TagWithValue, UserSummary
from devrev.models.parts import (
    ParentPartFilter,
    Part,
    PartsCreateRequest,
    PartsCreateResponse,
    PartsDeleteRequest,
    PartsDeleteResponse,
    PartsGetRequest,
    PartsGetResponse,
    PartsListRequest,
    PartsListResponse,
    PartsMovePlan,
    PartsMoveRequest,
    PartsMoveResult,
    PartsUpdateRequest,
    PartsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService

if TYPE_CHECKING:
    from devrev.client import AsyncDevRevClient, DevRevClient

# Module-level type alias. Declared here so method-scoped annotations can refer
# to ``list[str]`` without colliding with the ``list`` method defined on
# :class:`PartsService` / :class:`AsyncPartsService`.
_StrList = list[str]

# Sentinel returned as ``new_part_id`` for a dry-run move: no part is created,
# so there is no real ID to report.
_DRY_RUN_NEW_PART_ID = ""


def _owned_by_ids(owned_by: list[UserSummary] | None) -> list[str]:
    """Map a part's ``owned_by`` UserSummary list to a list of owner IDs."""
    if not owned_by:
        return []
    return [owner.id for owner in owned_by]


def _tag_ids(tags: list[TagWithValue] | None) -> list[str]:
    """Map a part's ``tags`` to a list of tag ID strings for recreation.

    ``TagWithValue.tag`` is a full ``Tag`` object in responses but a tag ID
    string in requests; this normalizes both forms to the ID string.
    """
    if not tags:
        return []
    ids: list[str] = []
    for tag in tags:
        ids.append(tag.tag if isinstance(tag.tag, str) else tag.tag.id)
    return ids


class PartsService(BaseService):
    """Service for managing DevRev Parts."""

    def create(self, request: PartsCreateRequest) -> Part:
        """Create a new part."""
        response = self._post("/parts.create", request, PartsCreateResponse)
        return response.part

    def get(self, request: PartsGetRequest) -> Part:
        """Get a part by ID."""
        response = self._post("/parts.get", request, PartsGetResponse)
        return response.part

    def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        parent_part: ParentPartFilter | None = None,
    ) -> PartsListResponse:
        """List parts.

        Args:
            limit: Maximum number of results to return (1-100).
            cursor: Pagination cursor from previous response.
            parent_part: Hierarchy filter to return parts under given parents
                (e.g. ``ParentPartFilter(parts=[parent_id], level=1)`` for the
                direct children of ``parent_id``).

        Returns:
            PartsListResponse with parts and next_cursor for pagination.
        """
        request = PartsListRequest(limit=limit, cursor=cursor, parent_part=parent_part)
        return self._post("/parts.list", request, PartsListResponse)

    def update(self, request: PartsUpdateRequest) -> Part:
        """Update a part."""
        response = self._post("/parts.update", request, PartsUpdateResponse)
        return response.part

    def delete(self, request: PartsDeleteRequest) -> None:
        """Delete a part."""
        self._post("/parts.delete", request, PartsDeleteResponse)

    def _list_child_part_ids(self, source_id: str) -> _StrList:
        """Return the IDs of the direct child parts of ``source_id``.

        Pages through ``parts.list`` with a ``parent_part`` hierarchy filter
        (level 1). The source part itself is excluded from the result.
        """
        child_ids: _StrList = []
        cursor: str | None = None
        while True:
            page = self.list(
                cursor=cursor,
                parent_part=ParentPartFilter(parts=[source_id], level=1),
            )
            for part in page.parts:
                if part.id != source_id:
                    child_ids.append(part.id)
            if not page.next_cursor:
                break
            cursor = page.next_cursor
        return child_ids

    def _collect_descendant_ids(self, source_id: str) -> set[str]:
        """Return the IDs of every descendant of ``source_id`` (whole subtree).

        Performs a bounded breadth-first walk over the part hierarchy using the
        existing ``_list_child_part_ids`` (level-1) lookup at each node. A
        ``visited`` set guards against re-processing a node, so a malformed
        hierarchy that contains a cycle cannot cause an infinite loop. The
        source itself is never included in the returned set.
        """
        descendants: set[str] = set()
        visited: set[str] = {source_id}
        frontier: _StrList = [source_id]
        while frontier:
            current = frontier.pop()
            for child_id in self._list_child_part_ids(current):
                if child_id in visited:
                    continue
                visited.add(child_id)
                descendants.add(child_id)
                frontier.append(child_id)
        return descendants

    def _validate_move_target(self, source: Part, request: PartsMoveRequest) -> None:
        """Reject self-moves and cycles before any mutation occurs.

        A move whose ``new_parent_part`` is the source itself (self-move) or a
        descendant of the source (cycle) would, under the recreate-and-relink
        workaround, create the replacement part under the soon-to-be-deleted
        source and then delete it -- destroying the new part (data loss). This
        guard runs read-only lookups only and raises before create/relink/delete.
        """
        if request.new_parent_part == source.id:
            raise DevRevError(
                f"Cannot move part {source.id!r} under itself "
                f"(new_parent_part == id): a self-move would orphan and delete "
                "the recreated part."
            )
        if request.new_parent_part in self._collect_descendant_ids(source.id):
            raise DevRevError(
                f"Cannot move part {source.id!r} under its own descendant "
                f"{request.new_parent_part!r}: this would create a cycle and "
                "destroy the recreated part when the source is deleted."
            )

    def _list_applies_to_work_ids(self, source_id: str) -> _StrList:
        """Return the IDs of all work items that apply to ``source_id``.

        Uses the works service (via the parent client) and paginates fully.
        """
        works = self._require_parent_client().works
        work_ids: _StrList = []
        cursor: str | None = None
        while True:
            page = works.list(applies_to_part=[source_id], cursor=cursor)
            work_ids.extend(work.id for work in page.works)
            if not page.next_cursor:
                break
            cursor = page.next_cursor
        return work_ids

    def _require_parent_client(self) -> DevRevClient:
        """Return the parent client, raising if it was not provided."""
        if not self._parent_client:
            raise DevRevError(
                "move requires a parent client reference. "
                "Ensure the parts service is accessed via DevRevClient.parts."
            )
        return self._parent_client

    def _compute_move_plan(self, source: Part, request: PartsMoveRequest) -> PartsMovePlan:
        """Compute the plan describing what moving ``source`` would do."""
        return PartsMovePlan(
            source_part_id=source.id,
            source_part_type=source.type.value if source.type else None,
            new_parent_part=request.new_parent_part,
            work_items_to_relink=self._list_applies_to_work_ids(source.id),
            child_parts_to_reparent=self._list_child_part_ids(source.id),
            will_delete_source=not request.dry_run,
        )

    def move(self, request: PartsMoveRequest) -> PartsMoveResult:
        """Move (re-parent) a part under a new parent part.

        The DevRev REST API does not allow changing ``parent_part`` on
        ``parts.update`` -- only ``parts.create`` accepts it. This method
        therefore implements a recreate-and-relink workaround: it creates a new
        part of the same type under ``new_parent_part`` (preserving name,
        description, owners and tags), relinks every work item that applied to
        the source onto the new part, re-parents the source's direct children,
        and finally deletes the original source part.

        Order of operations for a real move: create the new part first, relink
        work items and re-parent children to the new part, then delete the
        source last. If any relink or re-parent fails, the source part is left
        intact (not deleted) so nothing is orphaned and the error is surfaced.

        Before any mutation (and before computing the plan), the request is
        validated against self-moves and cycles: ``new_parent_part`` may not be
        the source itself nor any descendant of the source. Both checks run
        read-only lookups only and apply to dry runs as well, since such a
        request is invalid regardless of ``dry_run``.

        Args:
            request: The move request (source id, new parent id, dry_run flag).

        Returns:
            A fully-populated :class:`PartsMoveResult`. For a dry run,
            ``new_part_id`` is an empty-string sentinel, ``source_deleted`` is
            False, and ``plan`` describes what would happen with no mutations.

        Raises:
            DevRevError: If no parent client is available; if ``new_parent_part``
                is the source itself (self-move) or one of its descendants
                (cycle); or if a relink or re-parent fails (the source is not
                deleted in that case).
        """
        source = self.get(PartsGetRequest(id=request.id))
        self._validate_move_target(source, request)
        plan = self._compute_move_plan(source, request)

        if request.dry_run:
            return PartsMoveResult(
                new_part_id=_DRY_RUN_NEW_PART_ID,
                source_part_id=source.id,
                relinked_work_items=[],
                reparented_children=[],
                source_deleted=False,
                dry_run=True,
                plan=plan,
            )

        if source.type is None:
            raise DevRevError(
                f"Cannot move part {source.id!r}: its type is unknown, "
                "so the replacement part cannot be created with the same type."
            )

        new_part = self.create(
            PartsCreateRequest(
                name=source.name,
                type=source.type,
                description=source.description,
                owned_by=_owned_by_ids(source.owned_by) or None,
                parent_part=[request.new_parent_part],
                tags=_tag_ids(source.tags) or None,
            )
        )

        works = self._require_parent_client().works
        relinked: _StrList = []
        for work_id in plan.work_items_to_relink:
            works.update(work_id, applies_to_part=new_part.id)
            relinked.append(work_id)

        reparented: _StrList = []
        for child_id in plan.child_parts_to_reparent:
            self.move(PartsMoveRequest(id=child_id, new_parent_part=new_part.id, dry_run=False))
            reparented.append(child_id)

        self.delete(PartsDeleteRequest(id=source.id))

        return PartsMoveResult(
            new_part_id=new_part.id,
            source_part_id=source.id,
            relinked_work_items=relinked,
            reparented_children=reparented,
            source_deleted=True,
            dry_run=False,
            plan=plan,
        )


class AsyncPartsService(AsyncBaseService):
    """Async service for managing DevRev Parts."""

    async def create(self, request: PartsCreateRequest) -> Part:
        """Create a new part."""
        response = await self._post("/parts.create", request, PartsCreateResponse)
        return response.part

    async def get(self, request: PartsGetRequest) -> Part:
        """Get a part by ID."""
        response = await self._post("/parts.get", request, PartsGetResponse)
        return response.part

    async def list(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        parent_part: ParentPartFilter | None = None,
    ) -> PartsListResponse:
        """List parts.

        Args:
            limit: Maximum number of results to return (1-100).
            cursor: Pagination cursor from previous response.
            parent_part: Hierarchy filter to return parts under given parents
                (e.g. ``ParentPartFilter(parts=[parent_id], level=1)`` for the
                direct children of ``parent_id``).

        Returns:
            PartsListResponse with parts and next_cursor for pagination.
        """
        request = PartsListRequest(limit=limit, cursor=cursor, parent_part=parent_part)
        return await self._post("/parts.list", request, PartsListResponse)

    async def update(self, request: PartsUpdateRequest) -> Part:
        """Update a part."""
        response = await self._post("/parts.update", request, PartsUpdateResponse)
        return response.part

    async def delete(self, request: PartsDeleteRequest) -> None:
        """Delete a part."""
        await self._post("/parts.delete", request, PartsDeleteResponse)

    async def _list_child_part_ids(self, source_id: str) -> _StrList:
        """Return the IDs of the direct child parts of ``source_id``.

        Pages through ``parts.list`` with a ``parent_part`` hierarchy filter
        (level 1). The source part itself is excluded from the result.
        """
        child_ids: _StrList = []
        cursor: str | None = None
        while True:
            page = await self.list(
                cursor=cursor,
                parent_part=ParentPartFilter(parts=[source_id], level=1),
            )
            for part in page.parts:
                if part.id != source_id:
                    child_ids.append(part.id)
            if not page.next_cursor:
                break
            cursor = page.next_cursor
        return child_ids

    async def _collect_descendant_ids(self, source_id: str) -> set[str]:
        """Return the IDs of every descendant of ``source_id`` (whole subtree).

        Performs a bounded breadth-first walk over the part hierarchy using the
        existing ``_list_child_part_ids`` (level-1) lookup at each node. A
        ``visited`` set guards against re-processing a node, so a malformed
        hierarchy that contains a cycle cannot cause an infinite loop. The
        source itself is never included in the returned set.
        """
        descendants: set[str] = set()
        visited: set[str] = {source_id}
        frontier: _StrList = [source_id]
        while frontier:
            current = frontier.pop()
            for child_id in await self._list_child_part_ids(current):
                if child_id in visited:
                    continue
                visited.add(child_id)
                descendants.add(child_id)
                frontier.append(child_id)
        return descendants

    async def _validate_move_target(self, source: Part, request: PartsMoveRequest) -> None:
        """Reject self-moves and cycles before any mutation occurs.

        A move whose ``new_parent_part`` is the source itself (self-move) or a
        descendant of the source (cycle) would, under the recreate-and-relink
        workaround, create the replacement part under the soon-to-be-deleted
        source and then delete it -- destroying the new part (data loss). This
        guard runs read-only lookups only and raises before create/relink/delete.
        """
        if request.new_parent_part == source.id:
            raise DevRevError(
                f"Cannot move part {source.id!r} under itself "
                f"(new_parent_part == id): a self-move would orphan and delete "
                "the recreated part."
            )
        if request.new_parent_part in await self._collect_descendant_ids(source.id):
            raise DevRevError(
                f"Cannot move part {source.id!r} under its own descendant "
                f"{request.new_parent_part!r}: this would create a cycle and "
                "destroy the recreated part when the source is deleted."
            )

    async def _list_applies_to_work_ids(self, source_id: str) -> _StrList:
        """Return the IDs of all work items that apply to ``source_id``.

        Uses the works service (via the parent client) and paginates fully.
        """
        works = self._require_parent_client().works
        work_ids: _StrList = []
        cursor: str | None = None
        while True:
            page = await works.list(applies_to_part=[source_id], cursor=cursor)
            work_ids.extend(work.id for work in page.works)
            if not page.next_cursor:
                break
            cursor = page.next_cursor
        return work_ids

    def _require_parent_client(self) -> AsyncDevRevClient:
        """Return the parent client, raising if it was not provided."""
        if not self._parent_client:
            raise DevRevError(
                "move requires a parent client reference. "
                "Ensure the parts service is accessed via AsyncDevRevClient.parts."
            )
        return self._parent_client

    async def _compute_move_plan(self, source: Part, request: PartsMoveRequest) -> PartsMovePlan:
        """Compute the plan describing what moving ``source`` would do."""
        return PartsMovePlan(
            source_part_id=source.id,
            source_part_type=source.type.value if source.type else None,
            new_parent_part=request.new_parent_part,
            work_items_to_relink=await self._list_applies_to_work_ids(source.id),
            child_parts_to_reparent=await self._list_child_part_ids(source.id),
            will_delete_source=not request.dry_run,
        )

    async def move(self, request: PartsMoveRequest) -> PartsMoveResult:
        """Move (re-parent) a part under a new parent part.

        The DevRev REST API does not allow changing ``parent_part`` on
        ``parts.update`` -- only ``parts.create`` accepts it. This method
        therefore implements a recreate-and-relink workaround: it creates a new
        part of the same type under ``new_parent_part`` (preserving name,
        description, owners and tags), relinks every work item that applied to
        the source onto the new part, re-parents the source's direct children,
        and finally deletes the original source part.

        Order of operations for a real move: create the new part first, relink
        work items and re-parent children to the new part, then delete the
        source last. If any relink or re-parent fails, the source part is left
        intact (not deleted) so nothing is orphaned and the error is surfaced.

        Before any mutation (and before computing the plan), the request is
        validated against self-moves and cycles: ``new_parent_part`` may not be
        the source itself nor any descendant of the source. Both checks run
        read-only lookups only and apply to dry runs as well, since such a
        request is invalid regardless of ``dry_run``.

        Args:
            request: The move request (source id, new parent id, dry_run flag).

        Returns:
            A fully-populated :class:`PartsMoveResult`. For a dry run,
            ``new_part_id`` is an empty-string sentinel, ``source_deleted`` is
            False, and ``plan`` describes what would happen with no mutations.

        Raises:
            DevRevError: If no parent client is available; if ``new_parent_part``
                is the source itself (self-move) or one of its descendants
                (cycle); or if a relink or re-parent fails (the source is not
                deleted in that case).
        """
        source = await self.get(PartsGetRequest(id=request.id))
        await self._validate_move_target(source, request)
        plan = await self._compute_move_plan(source, request)

        if request.dry_run:
            return PartsMoveResult(
                new_part_id=_DRY_RUN_NEW_PART_ID,
                source_part_id=source.id,
                relinked_work_items=[],
                reparented_children=[],
                source_deleted=False,
                dry_run=True,
                plan=plan,
            )

        if source.type is None:
            raise DevRevError(
                f"Cannot move part {source.id!r}: its type is unknown, "
                "so the replacement part cannot be created with the same type."
            )

        new_part = await self.create(
            PartsCreateRequest(
                name=source.name,
                type=source.type,
                description=source.description,
                owned_by=_owned_by_ids(source.owned_by) or None,
                parent_part=[request.new_parent_part],
                tags=_tag_ids(source.tags) or None,
            )
        )

        works = self._require_parent_client().works
        relinked: _StrList = []
        for work_id in plan.work_items_to_relink:
            await works.update(work_id, applies_to_part=new_part.id)
            relinked.append(work_id)

        reparented: _StrList = []
        for child_id in plan.child_parts_to_reparent:
            await self.move(
                PartsMoveRequest(id=child_id, new_parent_part=new_part.id, dry_run=False)
            )
            reparented.append(child_id)

        await self.delete(PartsDeleteRequest(id=source.id))

        return PartsMoveResult(
            new_part_id=new_part.id,
            source_part_id=source.id,
            relinked_work_items=relinked,
            reparented_children=reparented,
            source_deleted=True,
            dry_run=False,
            plan=plan,
        )
