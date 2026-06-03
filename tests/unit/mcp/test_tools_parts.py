"""Unit tests for DevRev MCP parts tools."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from devrev.exceptions import DevRevError
from devrev.models.base import ObjectSummary, TagWithValue, UserSummary
from devrev.models.links import Link
from devrev.models.parts import Part, PartType
from devrev.models.tags import Tag
from devrev_mcp.tools.parts import (
    _collect_old_ids_postorder,
    _extract_object_id,
    _extract_owner_ids,
    _extract_tag_ids,
    _MovePlanNode,
    _replace_link_endpoint,
    devrev_parts_create,
    devrev_parts_delete,
    devrev_parts_get,
    devrev_parts_list,
    devrev_parts_move,
    devrev_parts_update,
)


def _make_mock_part(
    id: str = "PROD-1",
    name: str = "Test Product",
    type: str = "product",
) -> MagicMock:
    """Create a mock Part object for testing."""
    mock = MagicMock()
    mock.model_dump.return_value = {
        "id": id,
        "display_id": id,
        "name": name,
        "type": type,
        "description": "Test description",
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-02T00:00:00Z",
    }
    return mock


class TestPartsListTool:
    """Tests for devrev_parts_list tool."""

    @pytest.mark.asyncio
    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing parts when none exist."""
        response = MagicMock()
        response.parts = []
        response.next_cursor = None
        mock_client.parts.list.return_value = response

        result = await devrev_parts_list(mock_ctx)

        assert result["parts"] == []
        assert result["count"] == 0
        assert "next_cursor" not in result
        mock_client.parts.list.assert_called_once_with(limit=25, cursor=None)

    @pytest.mark.asyncio
    async def test_list_with_results(self, mock_ctx, mock_client):
        """Test listing parts with results."""
        mock_parts = [
            _make_mock_part(id="PROD-1", name="Product 1"),
            _make_mock_part(id="FEAT-1", name="Feature 1", type="feature"),
        ]
        response = MagicMock()
        response.parts = mock_parts
        response.next_cursor = None
        mock_client.parts.list.return_value = response

        result = await devrev_parts_list(mock_ctx)

        assert result["count"] == 2
        assert len(result["parts"]) == 2
        assert result["parts"][0]["name"] == "Product 1"
        assert result["parts"][1]["name"] == "Feature 1"
        assert "next_cursor" not in result

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing parts with pagination."""
        mock_parts = [_make_mock_part(id=f"PROD-{i}") for i in range(10)]
        response = MagicMock()
        response.parts = mock_parts
        response.next_cursor = "next-cursor-token"
        mock_client.parts.list.return_value = response

        result = await devrev_parts_list(mock_ctx, cursor="prev-cursor", limit=10)

        assert result["count"] == 10
        assert result["next_cursor"] == "next-cursor-token"
        mock_client.parts.list.assert_called_once_with(limit=10, cursor="prev-cursor")

    @pytest.mark.asyncio
    async def test_list_error(self, mock_ctx, mock_client):
        """Test error handling when listing parts fails."""
        mock_client.parts.list.side_effect = DevRevError("API error")

        with pytest.raises(RuntimeError, match="API error"):
            await devrev_parts_list(mock_ctx)


class TestPartsGetTool:
    """Tests for devrev_parts_get tool."""

    @pytest.mark.asyncio
    async def test_get_success(self, mock_ctx, mock_client):
        """Test successfully getting a part."""
        mock_part = _make_mock_part(id="PROD-123", name="My Product")
        mock_client.parts.get.return_value = mock_part

        result = await devrev_parts_get(mock_ctx, id="PROD-123")

        assert result["id"] == "PROD-123"
        assert result["name"] == "My Product"
        mock_client.parts.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent part."""
        mock_client.parts.get.side_effect = DevRevError("Part not found")

        with pytest.raises(RuntimeError, match="Part not found"):
            await devrev_parts_get(mock_ctx, id="PROD-999")


class TestPartsCreateTool:
    """Tests for devrev_parts_create tool."""

    @pytest.mark.asyncio
    async def test_create_success(self, mock_ctx, mock_client):
        """Test successfully creating a part."""
        mock_part = _make_mock_part(id="PROD-456", name="New Product")
        mock_client.parts.create.return_value = mock_part

        result = await devrev_parts_create(
            mock_ctx,
            name="New Product",
            type="product",
            description="A new product",
        )

        assert result["id"] == "PROD-456"
        assert result["name"] == "New Product"
        mock_client.parts.create.assert_called_once()
        call_args = mock_client.parts.create.call_args[0][0]
        assert call_args.type == PartType.PRODUCT

    @pytest.mark.asyncio
    async def test_create_with_uppercase_type_string(self, mock_ctx, mock_client):
        """Test creating a part with an uppercase type string."""
        mock_part = _make_mock_part(id="FEAT-789", name="New Feature", type="feature")
        mock_client.parts.create.return_value = mock_part

        result = await devrev_parts_create(
            mock_ctx,
            name="New Feature",
            type="FEATURE",
            parent_part=["don:core:dvrv-us-1:devo/1:part/1"],
        )

        assert result["id"] == "FEAT-789"
        call_args = mock_client.parts.create.call_args[0][0]
        assert call_args.type == PartType.FEATURE

    @pytest.mark.asyncio
    async def test_create_with_owned_by(self, mock_ctx, mock_client):
        """Test creating a part with owned_by parameter."""
        mock_part = _make_mock_part(id="PROD-100", name="Owned Product")
        mock_client.parts.create.return_value = mock_part

        result = await devrev_parts_create(
            mock_ctx,
            name="Owned Product",
            type="product",
            owned_by=["DEVU-4", "don:identity:dvrv-us-1:devo/1:devu/5"],
        )

        assert result["id"] == "PROD-100"
        call_args = mock_client.parts.create.call_args[0][0]
        assert call_args.owned_by == ["DEVU-4", "don:identity:dvrv-us-1:devo/1:devu/5"]

    @pytest.mark.asyncio
    async def test_create_with_parent_part(self, mock_ctx, mock_client):
        """Test creating a feature with parent_part parameter."""
        mock_part = _make_mock_part(id="FEAT-200", name="Child Feature", type="feature")
        mock_client.parts.create.return_value = mock_part

        result = await devrev_parts_create(
            mock_ctx,
            name="Child Feature",
            type="feature",
            parent_part=["don:core:dvrv-us-1:devo/1:part/1"],
            owned_by=["DEVU-4"],
        )

        assert result["id"] == "FEAT-200"
        call_args = mock_client.parts.create.call_args[0][0]
        assert call_args.parent_part == ["don:core:dvrv-us-1:devo/1:part/1"]
        assert call_args.type == PartType.FEATURE

    @pytest.mark.asyncio
    async def test_create_with_tags(self, mock_ctx, mock_client):
        """Test creating a part with tags parameter."""
        mock_part = _make_mock_part(id="CAP-300", name="Tagged Capability", type="capability")
        mock_client.parts.create.return_value = mock_part

        result = await devrev_parts_create(
            mock_ctx,
            name="Tagged Capability",
            type="capability",
            parent_part=["don:core:dvrv-us-1:devo/1:part/1"],
            tags=["tag-1", "tag-2"],
        )

        assert result["id"] == "CAP-300"
        call_args = mock_client.parts.create.call_args[0][0]
        assert call_args.tags == ["tag-1", "tag-2"]

    @pytest.mark.asyncio
    async def test_create_with_all_optional_params(self, mock_ctx, mock_client):
        """Test creating a part with all optional parameters."""
        mock_part = _make_mock_part(id="ENH-400", name="Full Enhancement", type="enhancement")
        mock_client.parts.create.return_value = mock_part

        result = await devrev_parts_create(
            mock_ctx,
            name="Full Enhancement",
            type="enhancement",
            description="A complete enhancement",
            owned_by=["DEVU-1"],
            parent_part=["FEAT-100"],
            tags=["enhancement-tag"],
        )

        assert result["id"] == "ENH-400"
        call_args = mock_client.parts.create.call_args[0][0]
        assert call_args.name == "Full Enhancement"
        assert call_args.type == PartType.ENHANCEMENT
        assert call_args.description == "A complete enhancement"
        assert call_args.owned_by == ["DEVU-1"]
        assert call_args.parent_part == ["FEAT-100"]
        assert call_args.tags == ["enhancement-tag"]

    @pytest.mark.asyncio
    async def test_create_with_invalid_type(self, mock_ctx, mock_client):
        """Test that an invalid type value raises RuntimeError. (#185)"""
        with pytest.raises(RuntimeError, match="Invalid part type"):
            await devrev_parts_create(
                mock_ctx,
                name="Bad Part",
                type="invalid",
            )

    @pytest.mark.asyncio
    async def test_create_capability_without_parent_part_raises(self, mock_ctx, mock_client):
        """Test that creating a CAPABILITY without parent_part raises RuntimeError. (#184)"""
        with pytest.raises(
            RuntimeError, match="parent_part is required when creating a CAPABILITY"
        ):
            await devrev_parts_create(
                mock_ctx,
                name="Orphan Capability",
                type="capability",
            )

    @pytest.mark.asyncio
    async def test_create_feature_without_parent_part_raises(self, mock_ctx, mock_client):
        """Test that creating a FEATURE without parent_part raises RuntimeError. (#184)"""
        with pytest.raises(RuntimeError, match="parent_part is required when creating a FEATURE"):
            await devrev_parts_create(
                mock_ctx,
                name="Orphan Feature",
                type="feature",
            )

    @pytest.mark.asyncio
    async def test_create_enhancement_without_parent_part_raises(self, mock_ctx, mock_client):
        """Test that creating an ENHANCEMENT without parent_part raises RuntimeError. (#184)"""
        with pytest.raises(
            RuntimeError, match="parent_part is required when creating a ENHANCEMENT"
        ):
            await devrev_parts_create(
                mock_ctx,
                name="Orphan Enhancement",
                type="enhancement",
            )

    @pytest.mark.asyncio
    async def test_create_product_without_parent_part_succeeds(self, mock_ctx, mock_client):
        """Test that creating a PRODUCT without parent_part succeeds. (#184)"""
        mock_part = _make_mock_part(id="PROD-999", name="Standalone Product")
        mock_client.parts.create.return_value = mock_part

        result = await devrev_parts_create(
            mock_ctx,
            name="Standalone Product",
            type="product",
        )

        assert result["id"] == "PROD-999"
        call_args = mock_client.parts.create.call_args[0][0]
        assert call_args.parent_part is None


class TestPartsUpdateTool:
    """Tests for devrev_parts_update tool."""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_ctx, mock_client):
        """Test successfully updating a part."""
        mock_part = _make_mock_part(id="PROD-123", name="Updated Product")
        mock_client.parts.update.return_value = mock_part

        result = await devrev_parts_update(mock_ctx, id="PROD-123", name="Updated Product")

        assert result["name"] == "Updated Product"
        mock_client.parts.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_error(self, mock_ctx, mock_client):
        """Test error handling when updating a part fails."""
        mock_client.parts.update.side_effect = DevRevError("Update failed")

        with pytest.raises(RuntimeError, match="Update failed"):
            await devrev_parts_update(mock_ctx, id="PROD-123", name="New Name")


class TestPartsDeleteTool:
    """Tests for devrev_parts_delete tool."""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_ctx, mock_client):
        """Test successfully deleting a part."""
        mock_client.parts.delete.return_value = None

        result = await devrev_parts_delete(mock_ctx, id="PROD-123")

        assert result["success"] is True
        assert "PROD-123" in result["message"]
        mock_client.parts.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test deleting a non-existent part."""
        mock_client.parts.delete.side_effect = DevRevError("Part not found")

        with pytest.raises(RuntimeError, match="Part not found"):
            await devrev_parts_delete(mock_ctx, id="PROD-999")


# ---------------------------------------------------------------------------
# Helpers used by the part-move workaround.
# ---------------------------------------------------------------------------

SRC_ID = "don:core:dvrv-us-1:devo/1:part/1"
NEW_PARENT_ID = "don:core:dvrv-us-1:devo/1:part/2"


def _real_part(
    id: str = SRC_ID,
    name: str = "Source Part",
    type: PartType | None = PartType.FEATURE,
    owners: list[UserSummary] | None = None,
    tags: list[TagWithValue] | None = None,
) -> Part:
    """Build a real Part model for move tests."""
    return Part(id=id, name=name, type=type, owned_by=owners, tags=tags)


def _list_resp(items: list, attr: str, next_cursor: str | None = None) -> SimpleNamespace:
    """Build a paginated list response stub exposing ``attr`` and next_cursor."""
    return SimpleNamespace(**{attr: items, "next_cursor": next_cursor})


def _mock_work(id: str = "don:core:dvrv-us-1:devo/1:work/1") -> MagicMock:
    work = MagicMock()
    work.id = id
    return work


def _mock_link(
    id: str = "don:core:dvrv-us-1:devo/1:link/1",
    link_type: str = "is_related_to",
    source: str = SRC_ID,
    target: str = "don:core:dvrv-us-1:devo/1:ticket/9",
) -> MagicMock:
    link = MagicMock()
    link.id = id
    link.link_type = link_type
    link.source = source
    link.target = target
    return link


class TestPartsMoveHelpers:
    """Tests for the pure helpers backing devrev_parts_move."""

    def test_extract_owner_ids_returns_ids(self):
        part = _real_part(owners=[UserSummary(id="DEVU-1"), UserSummary(id="DEVU-2")])
        assert _extract_owner_ids(part) == ["DEVU-1", "DEVU-2"]

    def test_extract_owner_ids_empty_when_unset(self):
        assert _extract_owner_ids(_real_part(owners=None)) == []

    def test_extract_tag_ids_handles_tag_objects_and_strings(self):
        part = _real_part(
            tags=[
                TagWithValue(tag=Tag(id="tag-1", name="Alpha")),
                TagWithValue(tag="tag-2"),
            ]
        )
        assert _extract_tag_ids(part) == ["tag-1", "tag-2"]

    def test_extract_tag_ids_empty_when_unset(self):
        assert _extract_tag_ids(_real_part(tags=None)) == []

    def test_extract_object_id_variants(self):
        assert _extract_object_id("part/1") == "part/1"
        assert _extract_object_id(ObjectSummary(id="part/2")) == "part/2"
        assert _extract_object_id({"id": "part/3"}) == "part/3"
        assert _extract_object_id({"no_id": "x"}) is None

    def test_replace_link_endpoint_source_match(self):
        link = Link(id="l1", link_type="is_related_to", source="part/1", target="ticket/9")
        assert _replace_link_endpoint(link, "part/1", "part/2") == ("part/2", "ticket/9")

    def test_replace_link_endpoint_target_match(self):
        link = Link(id="l1", link_type="is_related_to", source="ticket/9", target="part/1")
        assert _replace_link_endpoint(link, "part/1", "part/2") == ("ticket/9", "part/2")

    def test_replace_link_endpoint_no_match_returns_none(self):
        link = Link(id="l1", link_type="is_related_to", source="a", target="b")
        assert _replace_link_endpoint(link, "part/1", "part/2") is None

    def test_collect_old_ids_postorder(self):
        child = _MovePlanNode(_real_part(id="c1"), works=[], links=[], children=[])
        root = _MovePlanNode(_real_part(id="r1"), works=[], links=[], children=[child])
        assert _collect_old_ids_postorder(root) == ["c1", "r1"]


def _configure_no_dependents(mock_client) -> None:
    """Configure a source part with no children, works, or links."""
    mock_client.parts.get.side_effect = [_real_part(), _real_part(id=NEW_PARENT_ID, name="Parent")]
    mock_client.parts.list.return_value = _list_resp([], "parts")
    mock_client.works.list.return_value = _list_resp([], "works")
    mock_client.links.list.return_value = []


class TestPartsMoveTool:
    """Tests for the devrev_parts_move tool."""

    @pytest.mark.asyncio
    async def test_dry_run_does_not_mutate(self, mock_ctx, mock_client):
        """Dry run gathers a plan and performs no mutations."""
        _configure_no_dependents(mock_client)

        result = await devrev_parts_move(
            mock_ctx, source_part_id=SRC_ID, new_parent_part_id=NEW_PARENT_ID
        )

        assert result["dry_run"] is True
        assert result["success"] is True
        assert any(op["op"] == "create_part" for op in result["planned_operations"])
        assert result["completed_operations"] == []
        mock_client.parts.create.assert_not_called()
        mock_client.works.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_confirmation_required_for_mutation(self, mock_ctx, mock_client):
        """With dry_run False but confirm False, nothing is mutated."""
        _configure_no_dependents(mock_client)

        result = await devrev_parts_move(
            mock_ctx, source_part_id=SRC_ID, new_parent_part_id=NEW_PARENT_ID, dry_run=False
        )

        assert result["success"] is False
        assert any("confirm=True" in w for w in result["warnings"])
        mock_client.parts.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_successful_move_creates_part(self, mock_ctx, mock_client):
        """A confirmed move with no dependents creates the replacement part."""
        _configure_no_dependents(mock_client)
        created = _real_part(id="don:core:dvrv-us-1:devo/1:part/100", name="Source Part")
        mock_client.parts.create.return_value = created

        result = await devrev_parts_move(
            mock_ctx,
            source_part_id=SRC_ID,
            new_parent_part_id=NEW_PARENT_ID,
            dry_run=False,
            confirm=True,
        )

        assert result["success"] is True
        assert result["new_part_id"] == "don:core:dvrv-us-1:devo/1:part/100"
        assert result["created_part"]["id"] == "don:core:dvrv-us-1:devo/1:part/100"
        mock_client.parts.create.assert_called_once()
        create_req = mock_client.parts.create.call_args[0][0]
        assert create_req.parent_part == [NEW_PARENT_ID]
        assert create_req.type == PartType.FEATURE
        mock_client.parts.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_move_relinks_work_items(self, mock_ctx, mock_client):
        """Work items applying to the source are relinked to the new part."""
        _configure_no_dependents(mock_client)
        mock_client.works.list.return_value = _list_resp([_mock_work(id="w1")], "works")
        created = _real_part(id="don:core:dvrv-us-1:devo/1:part/100")
        mock_client.parts.create.return_value = created

        result = await devrev_parts_move(
            mock_ctx,
            source_part_id=SRC_ID,
            new_parent_part_id=NEW_PARENT_ID,
            dry_run=False,
            confirm=True,
        )

        assert result["success"] is True
        assert result["counts"]["works_relinked"] == 1
        mock_client.works.update.assert_called_once_with(
            "w1", applies_to_part="don:core:dvrv-us-1:devo/1:part/100"
        )

    @pytest.mark.asyncio
    async def test_move_recreates_links_before_delete(self, mock_ctx, mock_client):
        """Links are recreated against the new part, then the old link deleted."""
        _configure_no_dependents(mock_client)
        mock_client.links.list.return_value = [_mock_link(id="lnk1")]
        created = _real_part(id="don:core:dvrv-us-1:devo/1:part/100")
        mock_client.parts.create.return_value = created

        result = await devrev_parts_move(
            mock_ctx,
            source_part_id=SRC_ID,
            new_parent_part_id=NEW_PARENT_ID,
            dry_run=False,
            confirm=True,
        )

        assert result["success"] is True
        assert result["counts"]["links_recreated"] == 1
        mock_client.links.create.assert_called_once()
        create_req = mock_client.links.create.call_args[0][0]
        assert create_req.source == "don:core:dvrv-us-1:devo/1:part/100"
        assert create_req.target == "don:core:dvrv-us-1:devo/1:ticket/9"
        mock_client.links.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_children_block_execution(self, mock_ctx, mock_client):
        """Child parts block a confirmed move when recreate_children is False."""
        mock_client.parts.get.side_effect = [
            _real_part(),
            _real_part(id=NEW_PARENT_ID, name="Parent"),
        ]
        child = _real_part(id="don:core:dvrv-us-1:devo/1:part/3", name="Child")
        mock_client.parts.list.return_value = _list_resp([child], "parts")
        mock_client.works.list.return_value = _list_resp([], "works")
        mock_client.links.list.return_value = []

        result = await devrev_parts_move(
            mock_ctx,
            source_part_id=SRC_ID,
            new_parent_part_id=NEW_PARENT_ID,
            dry_run=False,
            confirm=True,
        )

        assert result["success"] is False
        assert "don:core:dvrv-us-1:devo/1:part/3" in result["unsupported_children"]
        mock_client.parts.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_recreate_children_moves_subtree(self, mock_ctx, mock_client):
        """recreate_children recursively recreates direct children."""
        mock_client.parts.get.side_effect = [
            _real_part(),
            _real_part(id=NEW_PARENT_ID, name="Parent"),
        ]
        child = _real_part(id="don:core:dvrv-us-1:devo/1:part/3", name="Child")

        def parts_list_side(**kwargs):
            parent = kwargs["parent_part_parts"][0]
            if parent == SRC_ID:
                return _list_resp([child], "parts")
            return _list_resp([], "parts")

        mock_client.parts.list.side_effect = parts_list_side
        mock_client.works.list.return_value = _list_resp([], "works")
        mock_client.links.list.return_value = []
        mock_client.parts.create.side_effect = [
            _real_part(id="don:core:dvrv-us-1:devo/1:part/100"),
            _real_part(id="don:core:dvrv-us-1:devo/1:part/101"),
        ]

        result = await devrev_parts_move(
            mock_ctx,
            source_part_id=SRC_ID,
            new_parent_part_id=NEW_PARENT_ID,
            dry_run=False,
            confirm=True,
            recreate_children=True,
        )

        assert result["success"] is True
        assert result["counts"]["parts_created"] == 2
        assert mock_client.parts.create.call_count == 2

    @pytest.mark.asyncio
    async def test_delete_original_when_requested(self, mock_ctx, mock_client):
        """delete_original removes the source part after a successful move."""
        _configure_no_dependents(mock_client)
        mock_client.parts.create.return_value = _real_part(id="don:core:dvrv-us-1:devo/1:part/100")

        result = await devrev_parts_move(
            mock_ctx,
            source_part_id=SRC_ID,
            new_parent_part_id=NEW_PARENT_ID,
            dry_run=False,
            confirm=True,
            delete_original=True,
        )

        assert result["success"] is True
        assert result["counts"]["parts_deleted"] == 1
        mock_client.parts.delete.assert_called_once()
        delete_req = mock_client.parts.delete.call_args[0][0]
        assert delete_req.id == SRC_ID

    @pytest.mark.asyncio
    async def test_move_api_error_raises_runtime_error(self, mock_ctx, mock_client):
        """A DevRevError from the API surfaces as RuntimeError."""
        mock_client.parts.get.side_effect = DevRevError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            await devrev_parts_move(
                mock_ctx, source_part_id=SRC_ID, new_parent_part_id=NEW_PARENT_ID
            )
