"""Unit tests for DevRev MCP tags tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev_mcp.tools.tags import (
    devrev_tags_create,
    devrev_tags_delete,
    devrev_tags_get,
    devrev_tags_list,
    devrev_tags_update,
)


def _make_mock_tag(tag_id: str = "TAG-123", name: str = "Test Tag") -> MagicMock:
    """Create a mock tag object."""
    tag = MagicMock()
    tag.model_dump.return_value = {
        "id": tag_id,
        "name": name,
        "created_date": "2026-01-01T00:00:00Z",
    }
    return tag


class TestTagsListTool:
    """Tests for devrev_tags_list tool."""

    @pytest.mark.asyncio
    async def test_list_empty(self, mock_ctx: MagicMock) -> None:
        """Test listing tags when none exist."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_client.tags.list.return_value = []

        result = await devrev_tags_list(mock_ctx)

        assert result["count"] == 0
        assert result["tags"] == []
        mock_client.tags.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_with_results(self, mock_ctx: MagicMock) -> None:
        """Test listing tags with results."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        tag1 = _make_mock_tag("TAG-1", "Tag One")
        tag2 = _make_mock_tag("TAG-2", "Tag Two")
        mock_client.tags.list.return_value = [tag1, tag2]

        result = await devrev_tags_list(mock_ctx)

        assert result["count"] == 2
        assert len(result["tags"]) == 2
        assert result["tags"][0]["id"] == "TAG-1"
        assert result["tags"][1]["id"] == "TAG-2"

    @pytest.mark.asyncio
    async def test_list_error(self, mock_ctx: MagicMock) -> None:
        """Test listing tags with API error."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_client.tags.list.side_effect = NotFoundError("Not found", status_code=404)

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_tags_list(mock_ctx)


class TestTagsGetTool:
    """Tests for devrev_tags_get tool."""

    @pytest.mark.asyncio
    async def test_get_success(self, mock_ctx: MagicMock) -> None:
        """Test getting a tag successfully."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_tag = _make_mock_tag()
        mock_client.tags.get.return_value = mock_tag

        result = await devrev_tags_get(mock_ctx, id="TAG-123")

        assert result["id"] == "TAG-123"
        assert result["name"] == "Test Tag"
        mock_client.tags.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_ctx: MagicMock) -> None:
        """Test getting a non-existent tag."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_client.tags.get.side_effect = NotFoundError("Not found", status_code=404)

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_tags_get(mock_ctx, id="TAG-999")


class TestTagsCreateTool:
    """Tests for devrev_tags_create tool."""

    @pytest.mark.asyncio
    async def test_create_success(self, mock_ctx: MagicMock) -> None:
        """Test creating a tag successfully."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_tag = _make_mock_tag()
        mock_client.tags.create.return_value = mock_tag

        result = await devrev_tags_create(mock_ctx, name="Test Tag", description="A test tag")

        assert result["id"] == "TAG-123"
        assert result["name"] == "Test Tag"
        mock_client.tags.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_validation_error(self, mock_ctx: MagicMock) -> None:
        """Test creating a tag with validation error."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_client.tags.create.side_effect = ValidationError("Invalid name", status_code=400)

        with pytest.raises(RuntimeError, match="Invalid name"):
            await devrev_tags_create(mock_ctx, name="")


class TestTagsUpdateTool:
    """Tests for devrev_tags_update tool."""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_ctx: MagicMock) -> None:
        """Test updating a tag successfully."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_tag = _make_mock_tag()
        mock_client.tags.update.return_value = mock_tag

        result = await devrev_tags_update(mock_ctx, id="TAG-123", name="Updated Tag")

        assert result["id"] == "TAG-123"
        mock_client.tags.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_error(self, mock_ctx: MagicMock) -> None:
        """Test updating a tag with error."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_client.tags.update.side_effect = NotFoundError("Not found", status_code=404)

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_tags_update(mock_ctx, id="TAG-999", name="Updated")


class TestTagsDeleteTool:
    """Tests for devrev_tags_delete tool."""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_ctx: MagicMock) -> None:
        """Test deleting a tag successfully."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_client.tags.delete.return_value = None

        result = await devrev_tags_delete(mock_ctx, id="TAG-123")

        assert result["deleted"] is True
        assert result["id"] == "TAG-123"
        mock_client.tags.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_ctx: MagicMock) -> None:
        """Test deleting a non-existent tag."""
        mock_client = mock_ctx.request_context.lifespan_context.get_client()
        mock_client.tags.delete.side_effect = NotFoundError("Not found", status_code=404)

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_tags_delete(mock_ctx, id="TAG-999")
