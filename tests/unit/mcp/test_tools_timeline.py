"""Unit tests for DevRev MCP timeline tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError
from devrev_mcp.tools.timeline import (
    devrev_timeline_create,
    devrev_timeline_delete,
    devrev_timeline_get,
    devrev_timeline_list,
    devrev_timeline_update,
)


def _make_mock_timeline_entry(data: dict | None = None) -> MagicMock:
    """Create a mock TimelineEntry model with model_dump method.

    Args:
        data: Optional dict to return from model_dump.

    Returns:
        MagicMock with model_dump method.
    """
    mock = MagicMock()
    default_data = {
        "id": "don:core:dvrv-us-1:devo/1:timeline_entry/123",
        "type": "timeline_comment",
        "body": "Test comment",
        "object": "don:core:dvrv-us-1:devo/1:ticket/456",
        "created_by": {"id": "user-1", "display_name": "Test User"},
        "created_date": "2026-01-01T00:00:00Z",
        "modified_date": "2026-01-01T00:00:00Z",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


class TestTimelineListTool:
    """Tests for devrev_timeline_list tool."""

    async def test_timeline_list_success(self, mock_ctx, mock_client):
        """Test listing timeline entries successfully."""
        # Arrange
        entry1 = _make_mock_timeline_entry({"id": "entry-1", "body": "First comment"})
        entry2 = _make_mock_timeline_entry({"id": "entry-2", "body": "Second comment"})
        mock_client.timeline_entries.list.return_value = [entry1, entry2]

        # Act
        result = await devrev_timeline_list(mock_ctx, object_id="don:core:ticket:123")

        # Assert
        assert result["count"] == 2
        assert len(result["timeline_entries"]) == 2
        assert result["timeline_entries"][0]["id"] == "entry-1"
        assert result["timeline_entries"][1]["id"] == "entry-2"
        mock_client.timeline_entries.list.assert_called_once()

    async def test_timeline_list_empty(self, mock_ctx, mock_client):
        """Test listing timeline entries with empty results."""
        # Arrange
        mock_client.timeline_entries.list.return_value = []

        # Act
        result = await devrev_timeline_list(mock_ctx, object_id="don:core:ticket:123")

        # Assert
        assert result["count"] == 0
        assert result["timeline_entries"] == []
        mock_client.timeline_entries.list.assert_called_once()

    async def test_timeline_list_with_cursor(self, mock_ctx, mock_client):
        """Test listing timeline entries with pagination."""
        # Arrange
        entry = _make_mock_timeline_entry()
        mock_client.timeline_entries.list.return_value = [entry]

        # Act
        result = await devrev_timeline_list(
            mock_ctx, object_id="don:core:ticket:123", cursor="cursor-123", limit=10
        )

        # Assert
        assert result["count"] == 1
        mock_client.timeline_entries.list.assert_called_once()


class TestTimelineGetTool:
    """Tests for devrev_timeline_get tool."""

    async def test_timeline_get_success(self, mock_ctx, mock_client):
        """Test getting a timeline entry successfully."""
        # Arrange
        entry = _make_mock_timeline_entry()
        mock_client.timeline_entries.get.return_value = entry

        # Act
        result = await devrev_timeline_get(mock_ctx, id="entry-123")

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:timeline_entry/123"
        assert result["body"] == "Test comment"
        mock_client.timeline_entries.get.assert_called_once()

    async def test_timeline_get_error(self, mock_ctx, mock_client):
        """Test getting a non-existent timeline entry."""
        # Arrange
        mock_client.timeline_entries.get.side_effect = NotFoundError(
            "Timeline entry not found", status_code=404
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Timeline entry not found"):
            await devrev_timeline_get(mock_ctx, id="entry-999")


class TestTimelineCreateTool:
    """Tests for devrev_timeline_create tool."""

    async def test_timeline_create_success(self, mock_ctx, mock_client):
        """Test creating a timeline entry with default type."""
        # Arrange
        entry = _make_mock_timeline_entry()
        mock_client.timeline_entries.create.return_value = entry

        # Act
        result = await devrev_timeline_create(mock_ctx, object_id="don:core:ticket:123")

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:timeline_entry/123"
        mock_client.timeline_entries.create.assert_called_once()

    async def test_timeline_create_with_body(self, mock_ctx, mock_client):
        """Test creating a timeline entry with body."""
        # Arrange
        entry = _make_mock_timeline_entry({"body": "Custom comment"})
        mock_client.timeline_entries.create.return_value = entry

        # Act
        result = await devrev_timeline_create(
            mock_ctx,
            object_id="don:core:ticket:123",
            type="timeline_comment",
            body="Custom comment",
        )

        # Assert
        assert result["body"] == "Custom comment"
        mock_client.timeline_entries.create.assert_called_once()

    async def test_timeline_create_change_event_type(self, mock_ctx, mock_client):
        """Test creating a timeline entry with change_event type."""
        # Arrange
        entry = _make_mock_timeline_entry({"type": "timeline_change_event"})
        mock_client.timeline_entries.create.return_value = entry

        # Act
        result = await devrev_timeline_create(
            mock_ctx, object_id="don:core:ticket:123", type="timeline_change_event"
        )

        # Assert
        assert result["type"] == "timeline_change_event"
        mock_client.timeline_entries.create.assert_called_once()

    async def test_timeline_create_invalid_type(self, mock_ctx, mock_client):
        """Test creating a timeline entry with invalid type."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid timeline entry type"):
            await devrev_timeline_create(
                mock_ctx, object_id="don:core:ticket:123", type="invalid_type"
            )


class TestTimelineUpdateTool:
    """Tests for devrev_timeline_update tool."""

    async def test_timeline_update_success(self, mock_ctx, mock_client):
        """Test updating a timeline entry successfully."""
        # Arrange
        entry = _make_mock_timeline_entry({"body": "Updated comment"})
        mock_client.timeline_entries.update.return_value = entry

        # Act
        result = await devrev_timeline_update(mock_ctx, id="entry-123", body="Updated comment")

        # Assert
        assert result["body"] == "Updated comment"
        mock_client.timeline_entries.update.assert_called_once()


class TestTimelineDeleteTool:
    """Tests for devrev_timeline_delete tool."""

    async def test_timeline_delete_success(self, mock_ctx, mock_client):
        """Test deleting a timeline entry successfully."""
        # Arrange
        mock_client.timeline_entries.delete.return_value = None

        # Act
        result = await devrev_timeline_delete(mock_ctx, id="entry-123")

        # Assert
        assert result["deleted"] is True
        assert result["id"] == "entry-123"
        mock_client.timeline_entries.delete.assert_called_once()
