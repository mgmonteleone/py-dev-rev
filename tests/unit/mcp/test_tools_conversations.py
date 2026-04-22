"""Unit tests for DevRev MCP conversation tools."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev.models.base import DateFilter
from devrev.models.conversations import ConversationsListRequest
from devrev_mcp.tools.conversations import (
    devrev_conversations_create,
    devrev_conversations_delete,
    devrev_conversations_export,
    devrev_conversations_get,
    devrev_conversations_list,
    devrev_conversations_list_modified_since,
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


class TestConversationsListDateFilterAndSort:
    """Tests for modified_date_*/sort_by handling on devrev_conversations_list."""

    @staticmethod
    def _call_request(mock_client) -> ConversationsListRequest:
        """Return the ConversationsListRequest passed to the SDK list mock."""
        args, kwargs = mock_client.conversations.list.call_args
        if args:
            return args[0]
        return kwargs["request"]

    async def test_list_forwards_modified_date_after(self, mock_ctx, mock_client):
        """modified_date_after (with trailing Z) builds a DateFilter.after."""
        mock_client.conversations.list.return_value = []

        await devrev_conversations_list(mock_ctx, modified_date_after="2025-01-01T00:00:00Z")

        request = self._call_request(mock_client)
        assert isinstance(request.modified_date, DateFilter)
        assert request.modified_date.after == datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
        assert request.modified_date.before is None

    async def test_list_forwards_modified_date_before(self, mock_ctx, mock_client):
        """modified_date_before (no trailing Z) builds a DateFilter.before."""
        mock_client.conversations.list.return_value = []

        await devrev_conversations_list(mock_ctx, modified_date_before="2025-02-01T12:30:00+00:00")

        request = self._call_request(mock_client)
        assert isinstance(request.modified_date, DateFilter)
        assert request.modified_date.after is None
        assert request.modified_date.before == datetime(2025, 2, 1, 12, 30, 0, tzinfo=UTC)

    async def test_list_forwards_both_bounds(self, mock_ctx, mock_client):
        """Both modified_date bounds produce a single DateFilter with both set."""
        mock_client.conversations.list.return_value = []

        await devrev_conversations_list(
            mock_ctx,
            modified_date_after="2025-01-01T00:00:00Z",
            modified_date_before="2025-02-01T00:00:00Z",
        )

        request = self._call_request(mock_client)
        assert request.modified_date is not None
        assert request.modified_date.after is not None
        assert request.modified_date.before is not None

    async def test_list_without_dates_sets_no_filter(self, mock_ctx, mock_client):
        """Omitting both date params leaves modified_date unset."""
        mock_client.conversations.list.return_value = []

        await devrev_conversations_list(mock_ctx)

        request = self._call_request(mock_client)
        assert request.modified_date is None

    async def test_list_invalid_modified_date_after_raises(self, mock_ctx, mock_client):
        """Malformed modified_date_after raises RuntimeError without calling SDK."""
        with pytest.raises(RuntimeError, match="Invalid modified_date_after"):
            await devrev_conversations_list(mock_ctx, modified_date_after="not-a-date")
        mock_client.conversations.list.assert_not_called()

    async def test_list_invalid_modified_date_before_raises(self, mock_ctx, mock_client):
        """Malformed modified_date_before raises RuntimeError without calling SDK."""
        with pytest.raises(RuntimeError, match="Invalid modified_date_before"):
            await devrev_conversations_list(mock_ctx, modified_date_before="bogus")
        mock_client.conversations.list.assert_not_called()

    async def test_list_forwards_sort_by(self, mock_ctx, mock_client):
        """sort_by is forwarded to the SDK untouched (SDK normalizes it)."""
        mock_client.conversations.list.return_value = []

        await devrev_conversations_list(mock_ctx, sort_by=["-modified_date"])

        request = self._call_request(mock_client)
        assert request.sort_by == ["-modified_date"]

    async def test_list_sort_by_none_is_none(self, mock_ctx, mock_client):
        """Omitting sort_by leaves it as None on the request."""
        mock_client.conversations.list.return_value = []

        await devrev_conversations_list(mock_ctx)

        request = self._call_request(mock_client)
        assert request.sort_by is None


class TestConversationsListModifiedSinceTool:
    """Tests for devrev_conversations_list_modified_since tool."""

    async def test_parses_after_and_forwards(self, mock_ctx, mock_client):
        """A valid ISO ``after`` is parsed and forwarded with optional limit."""
        conv = _make_mock_conversation()
        mock_client.conversations.list_modified_since.return_value = [conv]

        result = await devrev_conversations_list_modified_since(
            mock_ctx, after="2025-01-01T00:00:00Z", limit=5
        )

        assert result["count"] == 1
        assert len(result["conversations"]) == 1
        kwargs = mock_client.conversations.list_modified_since.call_args.kwargs
        assert kwargs["after"] == datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
        assert kwargs["limit"] == 5

    async def test_defaults_limit_to_none(self, mock_ctx, mock_client):
        """Calling without an explicit limit forwards ``limit=None``."""
        mock_client.conversations.list_modified_since.return_value = []

        result = await devrev_conversations_list_modified_since(
            mock_ctx, after="2025-03-01T00:00:00Z"
        )

        assert result["count"] == 0
        assert result["conversations"] == []
        kwargs = mock_client.conversations.list_modified_since.call_args.kwargs
        assert kwargs["limit"] is None

    async def test_invalid_after_raises_without_sdk_call(self, mock_ctx, mock_client):
        """An unparseable ``after`` raises RuntimeError before any SDK call."""
        with pytest.raises(RuntimeError, match="Invalid after"):
            await devrev_conversations_list_modified_since(mock_ctx, after="nope")
        mock_client.conversations.list_modified_since.assert_not_called()

    async def test_sdk_error_is_wrapped(self, mock_ctx, mock_client):
        """DevRevError from the SDK becomes a RuntimeError."""
        mock_client.conversations.list_modified_since.side_effect = NotFoundError(
            "not found", status_code=404
        )

        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_conversations_list_modified_since(mock_ctx, after="2025-01-01T00:00:00Z")
