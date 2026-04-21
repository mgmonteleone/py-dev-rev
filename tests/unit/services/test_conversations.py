"""Unit tests for ConversationsService."""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.models.base import DateFilter
from devrev.models.conversations import (
    Conversation,
    ConversationExportItem,
    ConversationsCreateRequest,
    ConversationsDeleteRequest,
    ConversationsExportRequest,
    ConversationsGetRequest,
    ConversationsListRequest,
    ConversationsUpdateRequest,
)
from devrev.services.conversations import (
    AsyncConversationsService,
    ConversationsService,
    _normalize_sort_by,
)

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
        assert isinstance(result[0], ConversationExportItem)
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


class TestNormalizeSortBy:
    """Tests for the _normalize_sort_by helper."""

    def test_returns_none_for_none(self) -> None:
        assert _normalize_sort_by(None) is None

    def test_returns_empty_list_for_empty_input(self) -> None:
        assert _normalize_sort_by([]) == []

    def test_adds_asc_default_for_bare_field_name(self) -> None:
        assert _normalize_sort_by(["modified_date"]) == ["modified_date:asc"]

    def test_preserves_explicit_direction(self) -> None:
        assert _normalize_sort_by(["modified_date:desc"]) == ["modified_date:desc"]

    def test_mixed_entries(self) -> None:
        assert _normalize_sort_by(["modified_date:desc", "created_date"]) == [
            "modified_date:desc",
            "created_date:asc",
        ]


class TestConversationsListRequestModel:
    """Tests for the extended ConversationsListRequest model."""

    def test_accepts_modified_date_and_sort_by(self) -> None:
        after = datetime(2024, 1, 1, tzinfo=UTC)
        request = ConversationsListRequest(
            modified_date=DateFilter(after=after),
            sort_by=["modified_date:desc"],
        )
        assert request.modified_date is not None
        assert request.modified_date.after == after
        assert request.sort_by == ["modified_date:desc"]

    def test_payload_serializes_datetime_as_iso_string(self) -> None:
        after = datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC)
        request = ConversationsListRequest(modified_date=DateFilter(after=after))
        payload = request.model_dump(exclude_none=True, by_alias=True, mode="json")
        assert isinstance(payload["modified_date"]["after"], str)
        assert payload["modified_date"]["after"].startswith("2024-01-15T10:00:00")


class TestListModifiedSince:
    """Tests for ConversationsService.list_modified_since."""

    def _make_conv(self, conv_id: str, modified: datetime | None) -> dict[str, Any]:
        return {
            "id": conv_id,
            "modified_date": modified.isoformat() if modified else None,
        }

    def test_forwards_modified_date_and_sort_by_in_payload(
        self, mock_http_client: MagicMock
    ) -> None:
        after = datetime(2024, 1, 1, tzinfo=UTC)
        mock_http_client.post.return_value = create_mock_response(
            {"conversations": [], "next_cursor": None}
        )

        service = ConversationsService(mock_http_client)
        service.list_modified_since(after)

        payload = mock_http_client.post.call_args[1]["data"]
        # Pydantic mode="json" serializes datetimes as JSON-safe ISO strings.
        assert isinstance(payload["modified_date"]["after"], str)
        assert payload["modified_date"]["after"].startswith("2024-01-01T00:00:00")
        assert payload["sort_by"] == ["modified_date:desc"]

    def test_respects_overall_limit(self, mock_http_client: MagicMock) -> None:
        after = datetime(2024, 1, 1, tzinfo=UTC)
        convs = [
            self._make_conv("a", after + timedelta(days=3)),
            self._make_conv("b", after + timedelta(days=2)),
            self._make_conv("c", after + timedelta(days=1)),
        ]
        mock_http_client.post.return_value = create_mock_response(
            {"conversations": convs, "next_cursor": "next"}
        )

        service = ConversationsService(mock_http_client)
        result = service.list_modified_since(after, limit=2)

        assert len(result) == 2
        assert [c.id for c in result] == ["a", "b"]
        # Single request; limit reached within first page, no follow-up call.
        assert mock_http_client.post.call_count == 1

    def test_paginates_via_cursor(self, mock_http_client: MagicMock) -> None:
        after = datetime(2024, 1, 1, tzinfo=UTC)
        page1 = {
            "conversations": [self._make_conv("a", after + timedelta(days=5))],
            "next_cursor": "cursor-2",
        }
        page2 = {
            "conversations": [self._make_conv("b", after + timedelta(days=4))],
            "next_cursor": None,
        }
        mock_http_client.post.side_effect = [
            create_mock_response(page1),
            create_mock_response(page2),
        ]

        service = ConversationsService(mock_http_client)
        result = service.list_modified_since(after)

        assert [c.id for c in result] == ["a", "b"]
        assert mock_http_client.post.call_count == 2
        second_payload = mock_http_client.post.call_args_list[1][1]["data"]
        assert second_payload["cursor"] == "cursor-2"

    def test_stops_when_cutoff_is_passed(self, mock_http_client: MagicMock) -> None:
        after = datetime(2024, 6, 1, tzinfo=UTC)
        convs = [
            self._make_conv("a", after + timedelta(days=1)),
            self._make_conv("b", after - timedelta(days=1)),  # before cutoff
            self._make_conv("c", after - timedelta(days=2)),
        ]
        mock_http_client.post.return_value = create_mock_response(
            {"conversations": convs, "next_cursor": "next"}
        )

        service = ConversationsService(mock_http_client)
        result = service.list_modified_since(after)

        assert [c.id for c in result] == ["a"]

    def test_page_size_capped_by_remaining_limit(self, mock_http_client: MagicMock) -> None:
        after = datetime(2024, 1, 1, tzinfo=UTC)
        mock_http_client.post.return_value = create_mock_response(
            {"conversations": [], "next_cursor": None}
        )

        service = ConversationsService(mock_http_client)
        service.list_modified_since(after, limit=3, page_size=10)

        payload = mock_http_client.post.call_args[1]["data"]
        assert payload["limit"] == 3


class TestAsyncListModifiedSince:
    """Tests for AsyncConversationsService.list_modified_since."""

    @pytest.mark.asyncio
    async def test_async_forwards_payload(self, mock_async_http_client: AsyncMock) -> None:
        after = datetime(2024, 1, 1, tzinfo=UTC)
        mock_async_http_client.post.return_value = create_mock_response(
            {"conversations": [], "next_cursor": None}
        )

        service = AsyncConversationsService(mock_async_http_client)
        await service.list_modified_since(after)

        payload = mock_async_http_client.post.call_args[1]["data"]
        assert isinstance(payload["modified_date"]["after"], str)
        assert payload["modified_date"]["after"].startswith("2024-01-01T00:00:00")
        assert payload["sort_by"] == ["modified_date:desc"]

    @pytest.mark.asyncio
    async def test_async_respects_limit_and_pagination(
        self, mock_async_http_client: AsyncMock
    ) -> None:
        after = datetime(2024, 1, 1, tzinfo=UTC)
        page1 = {
            "conversations": [
                {
                    "id": "a",
                    "modified_date": (after + timedelta(days=5)).isoformat(),
                },
            ],
            "next_cursor": "cursor-2",
        }
        page2 = {
            "conversations": [
                {
                    "id": "b",
                    "modified_date": (after + timedelta(days=4)).isoformat(),
                },
                {
                    "id": "c",
                    "modified_date": (after + timedelta(days=3)).isoformat(),
                },
            ],
            "next_cursor": None,
        }
        mock_async_http_client.post.side_effect = [
            create_mock_response(page1),
            create_mock_response(page2),
        ]

        service = AsyncConversationsService(mock_async_http_client)
        result = await service.list_modified_since(after, limit=2)

        assert [c.id for c in result] == ["a", "b"]
        assert mock_async_http_client.post.call_count == 2
