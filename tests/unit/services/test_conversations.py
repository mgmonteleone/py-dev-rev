"""Unit tests for ConversationsService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.conversations import (
    Conversation,
    ConversationsCreateRequest,
    ConversationsDeleteRequest,
    ConversationsExportRequest,
    ConversationsGetRequest,
    ConversationsListRequest,
    ConversationsUpdateRequest,
)
from devrev.services.conversations import ConversationsService

from .conftest import create_mock_response


class TestConversationsService:
    """Tests for ConversationsService."""

    def test_create_conversation(
        self,
        mock_http_client: MagicMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test creating a conversation."""
        mock_http_client.post.return_value = create_mock_response(
            {"conversation": sample_conversation_data}
        )

        service = ConversationsService(mock_http_client)
        request = ConversationsCreateRequest(
            type="support",
            title="Test Conversation",
            description="Test description",
        )
        result = service.create(request)

        assert isinstance(result, Conversation)
        assert result.id == "don:core:conversation:123"
        assert result.title == "Test Conversation"
        mock_http_client.post.assert_called_once()

    def test_get_conversation(
        self,
        mock_http_client: MagicMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test getting a conversation by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"conversation": sample_conversation_data}
        )

        service = ConversationsService(mock_http_client)
        request = ConversationsGetRequest(id="don:core:conversation:123")
        result = service.get(request)

        assert isinstance(result, Conversation)
        assert result.id == "don:core:conversation:123"
        mock_http_client.post.assert_called_once()

    def test_list_conversations(
        self,
        mock_http_client: MagicMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test listing conversations."""
        mock_http_client.post.return_value = create_mock_response(
            {"conversations": [sample_conversation_data]}
        )

        service = ConversationsService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], Conversation)
        assert result[0].id == "don:core:conversation:123"
        mock_http_client.post.assert_called_once()

    def test_list_conversations_with_request(
        self,
        mock_http_client: MagicMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test listing conversations with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"conversations": [sample_conversation_data]}
        )

        service = ConversationsService(mock_http_client)
        request = ConversationsListRequest(limit=50)
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_conversation(
        self,
        mock_http_client: MagicMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test updating a conversation."""
        updated_data = {**sample_conversation_data, "title": "Updated Title"}
        mock_http_client.post.return_value = create_mock_response({"conversation": updated_data})

        service = ConversationsService(mock_http_client)
        request = ConversationsUpdateRequest(
            id="don:core:conversation:123",
            title="Updated Title",
        )
        result = service.update(request)

        assert isinstance(result, Conversation)
        assert result.title == "Updated Title"
        mock_http_client.post.assert_called_once()

    def test_delete_conversation(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a conversation."""
        mock_http_client.post.return_value = create_mock_response({})

        service = ConversationsService(mock_http_client)
        request = ConversationsDeleteRequest(id="don:core:conversation:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_export_conversations(
        self,
        mock_http_client: MagicMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test exporting conversations."""
        mock_http_client.post.return_value = create_mock_response(
            {"conversations": [sample_conversation_data]}
        )

        service = ConversationsService(mock_http_client)
        result = service.export()

        assert len(result) == 1
        assert isinstance(result[0], Conversation)
        mock_http_client.post.assert_called_once()

    def test_export_conversations_with_request(
        self,
        mock_http_client: MagicMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test exporting conversations with cursor."""
        mock_http_client.post.return_value = create_mock_response(
            {"conversations": [sample_conversation_data]}
        )

        service = ConversationsService(mock_http_client)
        request = ConversationsExportRequest(cursor="next-cursor")
        result = service.export(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()
