"""Unit tests for PartsService."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.exceptions import DevRevError
from devrev.models.parts import (
    ParentPartFilter,
    Part,
    PartsCreateRequest,
    PartsDeleteRequest,
    PartsGetRequest,
    PartsListResponse,
    PartsMoveRequest,
    PartsMoveResult,
    PartsUpdateRequest,
    PartType,
)
from devrev.services.parts import AsyncPartsService, PartsService

from .conftest import create_mock_response


class TestPartsService:
    """Tests for PartsService."""

    def test_create_part(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test creating a part."""
        mock_http_client.post.return_value = create_mock_response({"part": sample_part_data})

        service = PartsService(mock_http_client)
        request = PartsCreateRequest(
            name="Test Part",
            type=PartType.PRODUCT,
            description="Test part description",
        )
        result = service.create(request)

        assert isinstance(result, Part)
        assert result.id == "don:core:part:123"
        assert result.name == "Test Part"
        mock_http_client.post.assert_called_once()

    def test_get_part(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test getting a part by ID."""
        mock_http_client.post.return_value = create_mock_response({"part": sample_part_data})

        service = PartsService(mock_http_client)
        request = PartsGetRequest(id="don:core:part:123")
        result = service.get(request)

        assert isinstance(result, Part)
        assert result.id == "don:core:part:123"
        mock_http_client.post.assert_called_once()

    def test_list_parts(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing parts."""
        mock_http_client.post.return_value = create_mock_response({"parts": [sample_part_data]})

        service = PartsService(mock_http_client)
        result = service.list()

        assert len(result.parts) == 1
        assert isinstance(result.parts[0], Part)
        assert result.parts[0].id == "don:core:part:123"
        mock_http_client.post.assert_called_once()

    def test_list_parts_with_request(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing parts with pagination."""
        mock_http_client.post.return_value = create_mock_response({"parts": [sample_part_data]})

        service = PartsService(mock_http_client)
        result = service.list(limit=50)

        assert len(result.parts) == 1
        mock_http_client.post.assert_called_once()

    def test_update_part(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test updating a part."""
        updated_data = {**sample_part_data, "name": "Updated Part"}
        mock_http_client.post.return_value = create_mock_response({"part": updated_data})

        service = PartsService(mock_http_client)
        request = PartsUpdateRequest(
            id="don:core:part:123",
            name="Updated Part",
        )
        result = service.update(request)

        assert isinstance(result, Part)
        assert result.name == "Updated Part"
        mock_http_client.post.assert_called_once()

    def test_delete_part(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a part."""
        mock_http_client.post.return_value = create_mock_response({})

        service = PartsService(mock_http_client)
        request = PartsDeleteRequest(id="don:core:part:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_parts_multiple(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing multiple parts."""
        parts = [
            sample_part_data,
            {**sample_part_data, "id": "don:core:part:456", "name": "Part 2"},
        ]
        mock_http_client.post.return_value = create_mock_response({"parts": parts})

        service = PartsService(mock_http_client)
        result = service.list()

        assert len(result.parts) == 2
        assert result.parts[0].name == "Test Part"
        assert result.parts[1].name == "Part 2"
        mock_http_client.post.assert_called_once()

    def test_list_parts_with_parent_part_filter(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing parts with a parent_part hierarchy filter is sent."""
        mock_http_client.post.return_value = create_mock_response({"parts": [sample_part_data]})

        service = PartsService(mock_http_client)
        service.list(parent_part=ParentPartFilter(parts=["don:core:part:parent"], level=1))

        call_data = mock_http_client.post.call_args.kwargs["data"]
        assert call_data["parent_part"] == {"parts": ["don:core:part:parent"], "level": 1}


def _make_part(
    part_id: str,
    *,
    name: str = "Source Part",
    type_: PartType = PartType.CAPABILITY,
    owners: list[str] | None = None,
    tags: list[str] | None = None,
) -> Part:
    """Build a Part with owners/tags for move tests."""
    return Part.model_validate(
        {
            "id": part_id,
            "name": name,
            "type": type_.value,
            "description": "desc",
            "owned_by": [{"id": uid} for uid in (owners or [])],
            "tags": [{"tag": {"id": tid, "name": tid}} for tid in (tags or [])],
        }
    )


class TestPartsServiceMove:
    """Tests for the recreate-and-relink PartsService.move operation."""

    def _service_with_works(self, mock_http_client: MagicMock) -> tuple[PartsService, MagicMock]:
        """Build a PartsService whose parent client exposes a mock works service."""
        works = MagicMock()
        works.list.return_value = MagicMock(works=[], next_cursor=None)
        parent = MagicMock()
        parent.works = works
        service = PartsService(mock_http_client, parent_client=parent)
        return service, works

    def test_dry_run_mutates_nothing(self, mock_http_client: MagicMock) -> None:
        """Dry run computes a plan and performs zero mutations."""
        service, works = self._service_with_works(mock_http_client)
        source = _make_part("don:core:part:src")
        service.get = MagicMock(return_value=source)  # type: ignore[method-assign]
        service.create = MagicMock()  # type: ignore[method-assign]
        service.delete = MagicMock()  # type: ignore[method-assign]
        # One relinkable work item, one child, returned by the lookups.
        works.list.return_value = MagicMock(
            works=[MagicMock(id="don:core:work:1")], next_cursor=None
        )
        service.list = MagicMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate(
                {"parts": [{"id": "don:core:part:child", "name": "c", "type": "feature"}]}
            )
        )

        result = service.move(
            PartsMoveRequest(
                id="don:core:part:src", new_parent_part="don:core:part:newp", dry_run=True
            )
        )

        assert isinstance(result, PartsMoveResult)
        assert result.dry_run is True
        assert result.new_part_id == ""
        assert result.source_deleted is False
        assert result.plan.work_items_to_relink == ["don:core:work:1"]
        assert result.plan.child_parts_to_reparent == ["don:core:part:child"]
        assert result.plan.will_delete_source is False
        # No mutating calls happened.
        service.create.assert_not_called()
        service.delete.assert_not_called()
        works.update.assert_not_called()

    def test_real_move_create_relink_delete_order(self, mock_http_client: MagicMock) -> None:
        """Real move creates first, relinks, then deletes the source last."""
        service, works = self._service_with_works(mock_http_client)
        source = _make_part("don:core:part:src", owners=["DEVU-1"], tags=["TAG-1"])
        new_part = _make_part("don:core:part:new", name="Source Part")

        # Track ordering across create / works.update / delete.
        order: list[str] = []
        service.get = MagicMock(return_value=source)  # type: ignore[method-assign]

        def _create(req: PartsCreateRequest) -> Part:
            order.append("create")
            return new_part

        def _delete(req: PartsDeleteRequest) -> None:
            order.append("delete")

        def _update(work_id: str, *, applies_to_part: str) -> None:
            order.append(f"relink:{work_id}->{applies_to_part}")

        service.create = MagicMock(side_effect=_create)  # type: ignore[method-assign]
        service.delete = MagicMock(side_effect=_delete)  # type: ignore[method-assign]
        works.update.side_effect = _update
        works.list.return_value = MagicMock(
            works=[MagicMock(id="don:core:work:1")], next_cursor=None
        )
        # No children.
        service.list = MagicMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate({"parts": []})
        )

        result = service.move(
            PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
        )

        assert order == ["create", "relink:don:core:work:1->don:core:part:new", "delete"]
        assert result.new_part_id == "don:core:part:new"
        assert result.relinked_work_items == ["don:core:work:1"]
        assert result.source_deleted is True
        assert result.dry_run is False
        service.delete.assert_called_once_with(PartsDeleteRequest(id="don:core:part:src"))

    def test_relink_failure_aborts_before_delete(self, mock_http_client: MagicMock) -> None:
        """If a relink fails, the source is NOT deleted and the error surfaces."""
        service, works = self._service_with_works(mock_http_client)
        source = _make_part("don:core:part:src")
        new_part = _make_part("don:core:part:new")
        service.get = MagicMock(return_value=source)  # type: ignore[method-assign]
        service.create = MagicMock(return_value=new_part)  # type: ignore[method-assign]
        service.delete = MagicMock()  # type: ignore[method-assign]
        works.list.return_value = MagicMock(
            works=[MagicMock(id="don:core:work:1")], next_cursor=None
        )
        works.update.side_effect = DevRevError("relink boom")
        service.list = MagicMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate({"parts": []})
        )

        with pytest.raises(DevRevError, match="relink boom"):
            service.move(
                PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
            )

        service.create.assert_called_once()
        service.delete.assert_not_called()  # source left intact, nothing orphaned

    def test_owned_by_and_tags_preserved(self, mock_http_client: MagicMock) -> None:
        """The recreated part preserves owner IDs, tag IDs, name and type."""
        service, works = self._service_with_works(mock_http_client)
        source = _make_part(
            "don:core:part:src",
            name="My Cap",
            type_=PartType.CAPABILITY,
            owners=["DEVU-1", "DEVU-2"],
            tags=["TAG-1", "TAG-2"],
        )
        new_part = _make_part("don:core:part:new")
        service.get = MagicMock(return_value=source)  # type: ignore[method-assign]
        service.create = MagicMock(return_value=new_part)  # type: ignore[method-assign]
        service.delete = MagicMock()  # type: ignore[method-assign]
        service.list = MagicMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate({"parts": []})
        )

        service.move(PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp"))

        created_req = service.create.call_args.args[0]
        assert isinstance(created_req, PartsCreateRequest)
        assert created_req.name == "My Cap"
        assert created_req.type == PartType.CAPABILITY
        assert created_req.owned_by == ["DEVU-1", "DEVU-2"]
        assert created_req.tags == ["TAG-1", "TAG-2"]
        assert created_req.parent_part == ["don:core:part:newp"]

    def test_children_reparented_under_new_part(self, mock_http_client: MagicMock) -> None:
        """Each direct child is moved under the newly created part."""
        service, works = self._service_with_works(mock_http_client)
        source = _make_part("don:core:part:src")
        new_part = _make_part("don:core:part:new")
        child_new = _make_part("don:core:part:child-new")
        # get(src) then get(child) during recursion.
        service.get = MagicMock(side_effect=[source, _make_part("don:core:part:child")])  # type: ignore[method-assign]
        service.create = MagicMock(side_effect=[new_part, child_new])  # type: ignore[method-assign]
        service.delete = MagicMock()  # type: ignore[method-assign]

        # First list call (children of src) returns one child; subsequent calls
        # (children of that child) return none.
        def _list(**kwargs: Any) -> PartsListResponse:
            parent = kwargs.get("parent_part")
            if parent is not None and parent.parts == ["don:core:part:src"]:
                return PartsListResponse.model_validate(
                    {"parts": [{"id": "don:core:part:child", "name": "c", "type": "feature"}]}
                )
            return PartsListResponse.model_validate({"parts": []})

        service.list = MagicMock(side_effect=_list)  # type: ignore[method-assign]

        result = service.move(
            PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
        )

        assert result.reparented_children == ["don:core:part:child"]
        # The child was re-created under the new part id.
        child_create_req = service.create.call_args_list[1].args[0]
        assert child_create_req.parent_part == ["don:core:part:new"]
        # Both source and child deleted (child deleted during its own move).
        assert service.delete.call_count == 2

    def test_move_without_parent_client_raises(self, mock_http_client: MagicMock) -> None:
        """move requires a parent client to reach the works service."""
        service = PartsService(mock_http_client)
        service.get = MagicMock(return_value=_make_part("don:core:part:src"))  # type: ignore[method-assign]

        with pytest.raises(DevRevError, match="requires a parent client"):
            service.move(
                PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
            )

    def test_work_and_child_pagination(self, mock_http_client: MagicMock) -> None:
        """Work-item and child lookups page through every cursor."""
        service, works = self._service_with_works(mock_http_client)
        source = _make_part("don:core:part:src")
        service.get = MagicMock(return_value=source)  # type: ignore[method-assign]
        service.create = MagicMock(return_value=_make_part("don:core:part:new"))  # type: ignore[method-assign]
        service.delete = MagicMock()  # type: ignore[method-assign]
        # Two pages of work items for the source; none for the recursive child moves.
        source_work_pages = iter(
            [
                MagicMock(works=[MagicMock(id="don:core:work:1")], next_cursor="c1"),
                MagicMock(works=[MagicMock(id="don:core:work:2")], next_cursor=None),
            ]
        )

        def _works_list(*, applies_to_part: list[str], cursor: str | None = None) -> MagicMock:
            if applies_to_part == ["don:core:part:src"]:
                return next(source_work_pages)
            return MagicMock(works=[], next_cursor=None)

        works.list.side_effect = _works_list
        works.update.return_value = None
        # Two pages of children, then empty pages for each child's own move.
        service.list = MagicMock(  # type: ignore[method-assign]
            side_effect=[
                PartsListResponse.model_validate(
                    {
                        "parts": [{"id": "don:core:part:c1", "name": "c1", "type": "feature"}],
                        "next_cursor": "p1",
                    }
                ),
                PartsListResponse.model_validate(
                    {"parts": [{"id": "don:core:part:c2", "name": "c2", "type": "feature"}]}
                ),
                # children of c1 (during its move): empty
                PartsListResponse.model_validate({"parts": []}),
                # children of c2 (during its move): empty
                PartsListResponse.model_validate({"parts": []}),
            ]
        )
        # get is called again for each child move.
        service.get.side_effect = [
            source,
            _make_part("don:core:part:c1"),
            _make_part("don:core:part:c2"),
        ]

        result = service.move(
            PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
        )

        assert result.relinked_work_items == ["don:core:work:1", "don:core:work:2"]
        assert result.reparented_children == ["don:core:part:c1", "don:core:part:c2"]

    def test_move_unknown_type_raises(self, mock_http_client: MagicMock) -> None:
        """A source part with unknown type cannot be recreated -> error."""
        service, works = self._service_with_works(mock_http_client)
        typeless = Part.model_validate({"id": "don:core:part:src", "name": "x"})
        service.get = MagicMock(return_value=typeless)  # type: ignore[method-assign]
        service.create = MagicMock()  # type: ignore[method-assign]
        service.delete = MagicMock()  # type: ignore[method-assign]
        service.list = MagicMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate({"parts": []})
        )

        with pytest.raises(DevRevError, match="type is unknown"):
            service.move(
                PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
            )
        service.create.assert_not_called()


class TestAsyncPartsServiceMove:
    """Async parity tests for AsyncPartsService.move."""

    def _service_with_works(
        self, mock_async_http_client: AsyncMock
    ) -> tuple[AsyncPartsService, MagicMock]:
        works = MagicMock()
        works.list = AsyncMock(return_value=MagicMock(works=[], next_cursor=None))
        works.update = AsyncMock()
        parent = MagicMock()
        parent.works = works
        service = AsyncPartsService(mock_async_http_client, parent_client=parent)
        return service, works

    @pytest.mark.asyncio
    async def test_async_dry_run_mutates_nothing(self, mock_async_http_client: AsyncMock) -> None:
        """Async dry run computes a plan and performs zero mutations."""
        service, works = self._service_with_works(mock_async_http_client)
        service.get = AsyncMock(return_value=_make_part("don:core:part:src"))  # type: ignore[method-assign]
        service.create = AsyncMock()  # type: ignore[method-assign]
        service.delete = AsyncMock()  # type: ignore[method-assign]
        works.list = AsyncMock(
            return_value=MagicMock(works=[MagicMock(id="don:core:work:1")], next_cursor=None)
        )
        service.list = AsyncMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate({"parts": []})
        )

        result = await service.move(
            PartsMoveRequest(
                id="don:core:part:src", new_parent_part="don:core:part:newp", dry_run=True
            )
        )

        assert result.dry_run is True
        assert result.new_part_id == ""
        assert result.source_deleted is False
        assert result.plan.work_items_to_relink == ["don:core:work:1"]
        service.create.assert_not_called()
        service.delete.assert_not_called()
        works.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_real_move_order_and_preservation(
        self, mock_async_http_client: AsyncMock
    ) -> None:
        """Async real move: create+relink+delete order and owner/tag preservation."""
        service, works = self._service_with_works(mock_async_http_client)
        source = _make_part("don:core:part:src", owners=["DEVU-1"], tags=["TAG-1"])
        new_part = _make_part("don:core:part:new")
        order: list[str] = []
        service.get = AsyncMock(return_value=source)  # type: ignore[method-assign]

        async def _create(req: PartsCreateRequest) -> Part:
            order.append("create")
            return new_part

        async def _delete(req: PartsDeleteRequest) -> None:
            order.append("delete")

        async def _update(work_id: str, *, applies_to_part: str) -> None:
            order.append("relink")

        service.create = AsyncMock(side_effect=_create)  # type: ignore[method-assign]
        service.delete = AsyncMock(side_effect=_delete)  # type: ignore[method-assign]
        works.update = AsyncMock(side_effect=_update)
        works.list = AsyncMock(
            return_value=MagicMock(works=[MagicMock(id="don:core:work:1")], next_cursor=None)
        )
        service.list = AsyncMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate({"parts": []})
        )

        result = await service.move(
            PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
        )

        assert order == ["create", "relink", "delete"]
        assert result.source_deleted is True
        created_req = service.create.call_args.args[0]
        assert created_req.owned_by == ["DEVU-1"]
        assert created_req.tags == ["TAG-1"]
        assert created_req.parent_part == ["don:core:part:newp"]

    @pytest.mark.asyncio
    async def test_async_relink_failure_aborts_before_delete(
        self, mock_async_http_client: AsyncMock
    ) -> None:
        """Async relink failure leaves the source intact."""
        service, works = self._service_with_works(mock_async_http_client)
        service.get = AsyncMock(return_value=_make_part("don:core:part:src"))  # type: ignore[method-assign]
        service.create = AsyncMock(return_value=_make_part("don:core:part:new"))  # type: ignore[method-assign]
        service.delete = AsyncMock()  # type: ignore[method-assign]
        works.list = AsyncMock(
            return_value=MagicMock(works=[MagicMock(id="don:core:work:1")], next_cursor=None)
        )
        works.update = AsyncMock(side_effect=DevRevError("relink boom"))
        service.list = AsyncMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate({"parts": []})
        )

        with pytest.raises(DevRevError, match="relink boom"):
            await service.move(
                PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
            )

        service.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_move_unknown_type_raises(self, mock_async_http_client: AsyncMock) -> None:
        """Async move with unknown source type raises before creating."""
        service, works = self._service_with_works(mock_async_http_client)
        service.get = AsyncMock(  # type: ignore[method-assign]
            return_value=Part.model_validate({"id": "don:core:part:src", "name": "x"})
        )
        service.create = AsyncMock()  # type: ignore[method-assign]
        service.list = AsyncMock(  # type: ignore[method-assign]
            return_value=PartsListResponse.model_validate({"parts": []})
        )

        with pytest.raises(DevRevError, match="type is unknown"):
            await service.move(
                PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
            )
        service.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_async_move_without_parent_client_raises(
        self, mock_async_http_client: AsyncMock
    ) -> None:
        """Async move requires a parent client to reach works."""
        service = AsyncPartsService(mock_async_http_client)
        service.get = AsyncMock(return_value=_make_part("don:core:part:src"))  # type: ignore[method-assign]

        with pytest.raises(DevRevError, match="requires a parent client"):
            await service.move(
                PartsMoveRequest(id="don:core:part:src", new_parent_part="don:core:part:newp")
            )
