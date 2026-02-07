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
    async def test_create_with_type_enum(self, mock_ctx, mock_client):
        """Test creating a part with different type."""
        mock_part = _make_mock_part(id="FEAT-789", name="New Feature", type="feature")
        mock_client.parts.create.return_value = mock_part

        result = await devrev_parts_create(mock_ctx, name="New Feature", type="FEATURE")

        assert result["id"] == "FEAT-789"
        call_args = mock_client.parts.create.call_args[0][0]
        assert call_args.type == PartType.FEATURE


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
