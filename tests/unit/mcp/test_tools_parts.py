"""Unit tests for DevRev MCP parts tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import DevRevError
from devrev.models.parts import PartType
from devrev_mcp.tools.parts import (
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


def _make_mock_move_result(
    new_part_id: str = "don:core:dvrv-us-1:devo/1:part/new",
    source_part_id: str = "don:core:dvrv-us-1:devo/1:part/src",
    dry_run: bool = False,
    source_deleted: bool = True,
) -> MagicMock:
    """Create a mock PartsMoveResult object for testing."""
    mock = MagicMock()
    mock.model_dump.return_value = {
        "new_part_id": new_part_id,
        "source_part_id": source_part_id,
        "relinked_work_items": ["don:core:dvrv-us-1:devo/1:issue/1"],
        "reparented_children": ["don:core:dvrv-us-1:devo/1:part/child"],
        "source_deleted": source_deleted,
        "dry_run": dry_run,
        "plan": {
            "source_part_id": source_part_id,
            "source_part_type": "capability",
            "new_parent_part": "don:core:dvrv-us-1:devo/1:part/parent",
            "work_items_to_relink": ["don:core:dvrv-us-1:devo/1:issue/1"],
            "child_parts_to_reparent": ["don:core:dvrv-us-1:devo/1:part/child"],
            "will_delete_source": source_deleted,
        },
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


class TestPartsMoveTool:
    """Tests for devrev_parts_move tool. (CSS-846)"""

    @pytest.mark.asyncio
    async def test_move_real_run_builds_request_and_returns_result(self, mock_ctx, mock_client):
        """Test that a real move builds a correct request and returns the result."""
        mock_result = _make_mock_move_result(dry_run=False, source_deleted=True)
        mock_client.parts.move.return_value = mock_result

        result = await devrev_parts_move(
            mock_ctx,
            id="FEAT-1",
            new_parent_part="CAP-2",
        )

        assert result["new_part_id"] == "don:core:dvrv-us-1:devo/1:part/new"
        assert result["source_deleted"] is True
        assert result["dry_run"] is False
        assert result["plan"]["will_delete_source"] is True
        mock_client.parts.move.assert_called_once()
        request = mock_client.parts.move.call_args[0][0]
        assert request.id == "FEAT-1"
        assert request.new_parent_part == "CAP-2"
        assert request.dry_run is False

    @pytest.mark.asyncio
    async def test_move_dry_run_builds_request_and_returns_plan(self, mock_ctx, mock_client):
        """Test that a dry run builds a request with dry_run=True and returns the plan."""
        mock_result = _make_mock_move_result(dry_run=True, source_deleted=False)
        mock_client.parts.move.return_value = mock_result

        result = await devrev_parts_move(
            mock_ctx,
            id="FEAT-1",
            new_parent_part="CAP-2",
            dry_run=True,
        )

        assert result["dry_run"] is True
        assert result["source_deleted"] is False
        assert result["plan"]["work_items_to_relink"] == ["don:core:dvrv-us-1:devo/1:issue/1"]
        assert result["plan"]["child_parts_to_reparent"] == ["don:core:dvrv-us-1:devo/1:part/child"]
        mock_client.parts.move.assert_called_once()
        request = mock_client.parts.move.call_args[0][0]
        assert request.id == "FEAT-1"
        assert request.new_parent_part == "CAP-2"
        assert request.dry_run is True

    @pytest.mark.asyncio
    async def test_move_invalid_source_don_id_raises(self, mock_ctx, mock_client):
        """Test that a non-part DON ID for the source raises RuntimeError."""
        with pytest.raises(RuntimeError, match="expects an part ID"):
            await devrev_parts_move(
                mock_ctx,
                id="don:core:dvrv-us-1:devo/1:account/1",
                new_parent_part="don:core:dvrv-us-1:devo/1:part/2",
            )
        mock_client.parts.move.assert_not_called()

    @pytest.mark.asyncio
    async def test_move_invalid_parent_don_id_raises(self, mock_ctx, mock_client):
        """Test that a non-part DON ID for the new parent raises RuntimeError."""
        with pytest.raises(RuntimeError, match="expects an part ID"):
            await devrev_parts_move(
                mock_ctx,
                id="don:core:dvrv-us-1:devo/1:part/1",
                new_parent_part="don:core:dvrv-us-1:devo/1:account/2",
            )
        mock_client.parts.move.assert_not_called()

    @pytest.mark.asyncio
    async def test_move_error(self, mock_ctx, mock_client):
        """Test error handling when the move API call fails."""
        mock_client.parts.move.side_effect = DevRevError("Move failed")

        with pytest.raises(RuntimeError, match="Move failed"):
            await devrev_parts_move(mock_ctx, id="FEAT-1", new_parent_part="CAP-2")


class TestPartsMoveGating:
    """Tests that devrev_parts_move is gated on enable_destructive_tools. (CSS-846)"""

    def test_move_registered_with_destructive_siblings(self):
        """devrev_parts_move lives in the destructive block with create/update/delete.

        The destructive tools are only defined when ``enable_destructive_tools``
        is True (the default). Importing devrev_parts_move alongside the other
        destructive parts tools proves it is defined inside the same
        ``if _config.enable_destructive_tools:`` block rather than registered
        unconditionally.
        """
        from devrev_mcp.tools import parts

        for name in (
            "devrev_parts_create",
            "devrev_parts_update",
            "devrev_parts_delete",
            "devrev_parts_move",
        ):
            assert hasattr(parts, name)
