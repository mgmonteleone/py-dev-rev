"""Unit tests for DevRev MCP conversation tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev_mcp.tools.conversations import (
    devrev_conversations_create,
    devrev_conversations_delete,
    devrev_conversations_export,
    devrev_conversations_get,
    devrev_conversations_list,
    devrev_conversations_update,
)


def _make_mock_conversation(data: dict | None = None) -> MagicMock:
    """Create a mock Conversation model with model_dump method.

    Args:
        data: Optional dict to return from model_dump.

    Returns:
        MagicMock with model_dump method.
    """
    mock = MagicMock()
    default_data = {
        "id": "don:core:dvrv-us-1:devo/1:conversation/123",
        "display_id": "CONV-123",
        "title": "Test Conversation",
        "description": "Test description",
        "stage": "open",
        "created_date": "2026-01-01T00:00:00Z",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


class TestConversationsListTool:
    """Tests for devrev_conversations_list tool."""

    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing conversations with empty results."""
        # Arrange
        mock_client.conversations.list.return_value = []

        # Act
        result = await devrev_conversations_list(mock_ctx)

        # Assert
        assert result["count"] == 0
        assert result["conversations"] == []
        mock_client.conversations.list.assert_called_once()

    async def test_list_with_results(self, mock_ctx, mock_client):
        """Test listing conversations with results."""
        # Arrange
        conv1 = _make_mock_conversation({"id": "CONV-1", "title": "Conversation 1"})
        conv2 = _make_mock_conversation({"id": "CONV-2", "title": "Conversation 2"})
        mock_client.conversations.list.return_value = [conv1, conv2]

        # Act
        result = await devrev_conversations_list(mock_ctx)

        # Assert
        assert result["count"] == 2
        assert len(result["conversations"]) == 2
        assert result["conversations"][0]["id"] == "CONV-1"
        assert result["conversations"][1]["id"] == "CONV-2"

    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing conversations with pagination parameters."""
        # Arrange
        conv = _make_mock_conversation()
        mock_client.conversations.list.return_value = [conv]

        # Act
        result = await devrev_conversations_list(mock_ctx, cursor="cursor-123", limit=10)

        # Assert
        assert result["count"] == 1
        mock_client.conversations.list.assert_called_once()

    async def test_list_error(self, mock_ctx, mock_client):
        """Test listing conversations with error."""
        # Arrange
        mock_client.conversations.list.side_effect = NotFoundError("Not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_conversations_list(mock_ctx)


class TestConversationsGetTool:
    """Tests for devrev_conversations_get tool."""

    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting a conversation successfully."""
        # Arrange
        conv = _make_mock_conversation()
        mock_client.conversations.get.return_value = conv

        # Act
        result = await devrev_conversations_get(mock_ctx, id="CONV-123")

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:conversation/123"
        assert result["title"] == "Test Conversation"
        mock_client.conversations.get.assert_called_once()

    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent conversation."""
        # Arrange
        mock_client.conversations.get.side_effect = NotFoundError(
            "Conversation not found", status_code=404
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Conversation not found"):
            await devrev_conversations_get(mock_ctx, id="CONV-999")


class TestConversationsCreateTool:
    """Tests for devrev_conversations_create tool."""

    async def test_create_minimal(self, mock_ctx, mock_client):
        """Test creating a conversation with minimal parameters."""
        # Arrange
        conv = _make_mock_conversation()
        mock_client.conversations.create.return_value = conv

        # Act
        result = await devrev_conversations_create(mock_ctx)

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:conversation/123"
        mock_client.conversations.create.assert_called_once()

    async def test_create_full(self, mock_ctx, mock_client):
        """Test creating a conversation with all parameters."""
        # Arrange
        conv = _make_mock_conversation(
            {"title": "New Conversation", "description": "New description"}
        )
        mock_client.conversations.create.return_value = conv

        # Act
        result = await devrev_conversations_create(
            mock_ctx, type="support", title="New Conversation", description="New description"
        )

        # Assert
        assert result["title"] == "New Conversation"
        assert result["description"] == "New description"
        mock_client.conversations.create.assert_called_once()

    async def test_create_validation_error(self, mock_ctx, mock_client):
        """Test creating a conversation with validation error."""
        # Arrange
        mock_client.conversations.create.side_effect = ValidationError(
            "Invalid type", status_code=400
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Invalid type"):
            await devrev_conversations_create(mock_ctx, type="invalid")


class TestConversationsUpdateTool:
    """Tests for devrev_conversations_update tool."""

    async def test_update_success(self, mock_ctx, mock_client):
        """Test updating a conversation successfully."""
        # Arrange
        conv = _make_mock_conversation(
            {"title": "Updated Title", "description": "Updated description"}
        )
        mock_client.conversations.update.return_value = conv

        # Act
        result = await devrev_conversations_update(
            mock_ctx, id="CONV-123", title="Updated Title", description="Updated description"
        )

        # Assert
        assert result["title"] == "Updated Title"
        assert result["description"] == "Updated description"
        mock_client.conversations.update.assert_called_once()

    async def test_update_error(self, mock_ctx, mock_client):
        """Test updating a conversation with error."""
        # Arrange
        mock_client.conversations.update.side_effect = NotFoundError(
            "Conversation not found", status_code=404
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Conversation not found"):
            await devrev_conversations_update(mock_ctx, id="CONV-999", title="New Title")


class TestConversationsDeleteTool:
    """Tests for devrev_conversations_delete tool."""

    async def test_delete_success(self, mock_ctx, mock_client):
        """Test deleting a conversation successfully."""
        # Arrange
        mock_client.conversations.delete.return_value = None

        # Act
        result = await devrev_conversations_delete(mock_ctx, id="CONV-123")

        # Assert
        assert result["deleted"] is True
        assert result["id"] == "CONV-123"
        mock_client.conversations.delete.assert_called_once()

    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test deleting a non-existent conversation."""
        # Arrange
        mock_client.conversations.delete.side_effect = NotFoundError(
            "Conversation not found", status_code=404
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Conversation not found"):
            await devrev_conversations_delete(mock_ctx, id="CONV-999")


class TestConversationsExportTool:
    """Tests for devrev_conversations_export tool."""

    async def test_export_success_with_pagination(self, mock_ctx, mock_client):
        """Test exporting conversations with pagination."""
        # Arrange
        conv1 = _make_mock_conversation({"id": "CONV-1"})
        conv2 = _make_mock_conversation({"id": "CONV-2"})
        response = MagicMock()
        response.conversations = [conv1, conv2]
        response.next_cursor = "next-cursor-123"
        mock_client.conversations.export.return_value = response

        # Act
        result = await devrev_conversations_export(mock_ctx, cursor="cursor-123", limit=10)

        # Assert
        assert result["count"] == 2
        assert len(result["conversations"]) == 2
        assert result["next_cursor"] == "next-cursor-123"
        mock_client.conversations.export.assert_called_once()

    async def test_export_empty(self, mock_ctx, mock_client):
        """Test exporting conversations with empty results."""
        # Arrange
        response = MagicMock()
        response.conversations = []
        response.next_cursor = None
        mock_client.conversations.export.return_value = response

        # Act
        result = await devrev_conversations_export(mock_ctx)

        # Assert
        assert result["count"] == 0
        assert result["conversations"] == []
        assert "next_cursor" not in result

    async def test_export_error(self, mock_ctx, mock_client):
        """Test exporting conversations with error."""
        # Arrange
        mock_client.conversations.export.side_effect = NotFoundError(
            "Export endpoint not available (beta API only)", status_code=404
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Export endpoint not available"):
            await devrev_conversations_export(mock_ctx)
