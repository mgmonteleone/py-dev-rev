"""Unit tests for DevRev MCP link tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev_mcp.tools.links import (
    devrev_links_create,
    devrev_links_delete,
    devrev_links_get,
    devrev_links_list,
)


def _make_mock_link(data: dict | None = None) -> MagicMock:
    """Create a mock Link model with model_dump method.

    Args:
        data: Optional dict to return from model_dump.

    Returns:
        MagicMock with model_dump method.
    """
    mock = MagicMock()
    default_data = {
        "id": "don:core:dvrv-us-1:devo/1:link/123",
        "link_type": "is_related_to",
        "source": "don:core:dvrv-us-1:devo/1:ticket/1",
        "target": "don:core:dvrv-us-1:devo/1:ticket/2",
        "created_date": "2026-01-01T00:00:00Z",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


class TestLinksListTool:
    """Tests for devrev_links_list tool."""

    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing links with empty results."""
        # Arrange
        mock_client.links.list.return_value = []

        # Act
        result = await devrev_links_list(mock_ctx)

        # Assert
        assert result["count"] == 0
        assert result["links"] == []
        mock_client.links.list.assert_called_once()

    async def test_list_success(self, mock_ctx, mock_client):
        """Test listing links with results."""
        # Arrange
        link1 = _make_mock_link({"id": "link-1", "link_type": "is_related_to"})
        link2 = _make_mock_link({"id": "link-2", "link_type": "is_blocked_by"})
        mock_client.links.list.return_value = [link1, link2]

        # Act
        result = await devrev_links_list(mock_ctx)

        # Assert
        assert result["count"] == 2
        assert len(result["links"]) == 2
        assert result["links"][0]["id"] == "link-1"
        assert result["links"][1]["id"] == "link-2"

    async def test_list_with_object_filter(self, mock_ctx, mock_client):
        """Test listing links filtered by object ID."""
        # Arrange
        link = _make_mock_link()
        mock_client.links.list.return_value = [link]

        # Act
        result = await devrev_links_list(mock_ctx, object_id="don:core:dvrv-us-1:devo/1:ticket/123")

        # Assert
        assert result["count"] == 1
        mock_client.links.list.assert_called_once()

    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing links with pagination parameters."""
        # Arrange
        link = _make_mock_link()
        mock_client.links.list.return_value = [link]

        # Act
        result = await devrev_links_list(mock_ctx, cursor="cursor-123", limit=10)

        # Assert
        assert result["count"] == 1
        mock_client.links.list.assert_called_once()

    async def test_list_error(self, mock_ctx, mock_client):
        """Test listing links with error."""
        # Arrange
        mock_client.links.list.side_effect = NotFoundError("Not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_links_list(mock_ctx)


class TestLinksGetTool:
    """Tests for devrev_links_get tool."""

    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting a link successfully."""
        # Arrange
        link = _make_mock_link()
        mock_client.links.get.return_value = link

        # Act
        result = await devrev_links_get(mock_ctx, id="link-123")

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:link/123"
        assert result["link_type"] == "is_related_to"
        mock_client.links.get.assert_called_once()

    async def test_get_error(self, mock_ctx, mock_client):
        """Test getting a non-existent link."""
        # Arrange
        mock_client.links.get.side_effect = NotFoundError("Link not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Link not found"):
            await devrev_links_get(mock_ctx, id="link-999")


class TestLinksCreateTool:
    """Tests for devrev_links_create tool."""

    async def test_create_success(self, mock_ctx, mock_client):
        """Test creating a link successfully."""
        # Arrange
        link = _make_mock_link()
        mock_client.links.create.return_value = link

        # Act
        result = await devrev_links_create(
            mock_ctx,
            link_type="is_related_to",
            source="don:core:dvrv-us-1:devo/1:ticket/1",
            target="don:core:dvrv-us-1:devo/1:ticket/2",
        )

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:link/123"
        assert result["link_type"] == "is_related_to"
        mock_client.links.create.assert_called_once()

    async def test_create_with_enum_type(self, mock_ctx, mock_client):
        """Test creating a link with enum link type."""
        # Arrange
        link = _make_mock_link({"link_type": "is_blocked_by"})
        mock_client.links.create.return_value = link

        # Act
        result = await devrev_links_create(
            mock_ctx,
            link_type="is_blocked_by",
            source="don:core:dvrv-us-1:devo/1:ticket/1",
            target="don:core:dvrv-us-1:devo/1:ticket/2",
        )

        # Assert
        assert result["link_type"] == "is_blocked_by"
        mock_client.links.create.assert_called_once()

    async def test_create_with_custom_type(self, mock_ctx, mock_client):
        """Test creating a link with custom link type."""
        # Arrange
        link = _make_mock_link({"link_type": "custom_link_type"})
        mock_client.links.create.return_value = link

        # Act
        result = await devrev_links_create(
            mock_ctx,
            link_type="custom_link_type",
            source="don:core:dvrv-us-1:devo/1:ticket/1",
            target="don:core:dvrv-us-1:devo/1:ticket/2",
        )

        # Assert
        assert result["link_type"] == "custom_link_type"
        mock_client.links.create.assert_called_once()

    async def test_create_validation_error(self, mock_ctx, mock_client):
        """Test creating a link with validation error."""
        # Arrange
        mock_client.links.create.side_effect = ValidationError(
            "Invalid source or target", status_code=400
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Invalid source or target"):
            await devrev_links_create(
                mock_ctx,
                link_type="is_related_to",
                source="invalid",
                target="invalid",
            )


class TestLinksDeleteTool:
    """Tests for devrev_links_delete tool."""

    async def test_delete_success(self, mock_ctx, mock_client):
        """Test deleting a link successfully."""
        # Arrange
        mock_client.links.delete.return_value = None

        # Act
        result = await devrev_links_delete(mock_ctx, id="link-123")

        # Assert
        assert result["deleted"] is True
        assert result["id"] == "link-123"
        mock_client.links.delete.assert_called_once()

    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test deleting a non-existent link."""
        # Arrange
        mock_client.links.delete.side_effect = NotFoundError("Link not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Link not found"):
            await devrev_links_delete(mock_ctx, id="link-999")
