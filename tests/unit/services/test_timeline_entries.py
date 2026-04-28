"""Unit tests for TimelineEntriesService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.timeline_entries import (
    TimelineEntriesCreateRequest,
    TimelineEntriesDeleteRequest,
    TimelineEntriesGetRequest,
    TimelineEntriesListRequest,
    TimelineEntriesUpdateRequest,
    TimelineEntry,
    TimelineEntryType,
    TimelineEntryVisibility,
)
from devrev.services.timeline_entries import TimelineEntriesService

from .conftest import create_mock_response


class TestTimelineEntriesService:
    """Tests for TimelineEntriesService."""

    def test_create_timeline_entry(
        self,
        mock_http_client: MagicMock,
        sample_timeline_entry_data: dict[str, Any],
    ) -> None:
        """Test creating a timeline entry."""
        mock_http_client.post.return_value = create_mock_response(
            {"timeline_entry": sample_timeline_entry_data}
        )

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesCreateRequest(
            object="don:core:issue:456",
            type=TimelineEntryType.COMMENT,
            body="Test comment",
        )
        result = service.create(request)

        assert isinstance(result, TimelineEntry)
        assert result.id == "don:core:timeline_entry:123"
        mock_http_client.post.assert_called_once()

    def test_get_timeline_entry(
        self,
        mock_http_client: MagicMock,
        sample_timeline_entry_data: dict[str, Any],
    ) -> None:
        """Test getting a timeline entry by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"timeline_entry": sample_timeline_entry_data}
        )

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesGetRequest(id="don:core:timeline_entry:123")
        result = service.get(request)

        assert isinstance(result, TimelineEntry)
        assert result.id == "don:core:timeline_entry:123"
        mock_http_client.post.assert_called_once()

    def test_list_timeline_entries(
        self,
        mock_http_client: MagicMock,
        sample_timeline_entry_data: dict[str, Any],
    ) -> None:
        """Test listing timeline entries."""
        mock_http_client.post.return_value = create_mock_response(
            {"timeline_entries": [sample_timeline_entry_data]}
        )

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesListRequest(object="don:core:issue:456")
        result = service.list(request)

        assert len(result) == 1
        assert isinstance(result[0], TimelineEntry)
        assert result[0].id == "don:core:timeline_entry:123"
        mock_http_client.post.assert_called_once()

    def test_list_timeline_entries_with_pagination(
        self,
        mock_http_client: MagicMock,
        sample_timeline_entry_data: dict[str, Any],
    ) -> None:
        """Test listing timeline entries with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"timeline_entries": [sample_timeline_entry_data]}
        )

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesListRequest(
            object="don:core:issue:456",
            limit=50,
            cursor="next-cursor",
        )
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_timeline_entry(
        self,
        mock_http_client: MagicMock,
        sample_timeline_entry_data: dict[str, Any],
    ) -> None:
        """Test updating a timeline entry."""
        updated_data = {**sample_timeline_entry_data, "body": "Updated comment"}
        mock_http_client.post.return_value = create_mock_response({"timeline_entry": updated_data})

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesUpdateRequest(
            id="don:core:timeline_entry:123",
            body="Updated comment",
        )
        result = service.update(request)

        assert isinstance(result, TimelineEntry)
        assert result.body == "Updated comment"
        mock_http_client.post.assert_called_once()

    def test_delete_timeline_entry(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a timeline entry."""
        mock_http_client.post.return_value = create_mock_response({})

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesDeleteRequest(id="don:core:timeline_entry:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_timeline_entries_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing timeline entries returns empty list."""
        mock_http_client.post.return_value = create_mock_response({"timeline_entries": []})

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesListRequest(object="don:core:issue:456")
        result = service.list(request)

        assert len(result) == 0
        mock_http_client.post.assert_called_once()

    def test_create_timeline_entry_with_internal_visibility(
        self,
        mock_http_client: MagicMock,
        sample_timeline_entry_data: dict[str, Any],
    ) -> None:
        """Internal visibility is forwarded to the timeline-entries.create payload."""
        mock_http_client.post.return_value = create_mock_response(
            {"timeline_entry": sample_timeline_entry_data}
        )

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesCreateRequest(
            object="don:core:issue:456",
            type=TimelineEntryType.COMMENT,
            body="Internal note",
            visibility=TimelineEntryVisibility.INTERNAL,
        )
        service.create(request)

        mock_http_client.post.assert_called_once()
        _, call_kwargs = mock_http_client.post.call_args
        payload = call_kwargs["data"]
        assert payload["visibility"] == "internal"
        assert payload["body"] == "Internal note"

    def test_create_timeline_entry_omits_visibility_when_unset(
        self,
        mock_http_client: MagicMock,
        sample_timeline_entry_data: dict[str, Any],
    ) -> None:
        """When visibility is unset, it is excluded from the payload (server default)."""
        mock_http_client.post.return_value = create_mock_response(
            {"timeline_entry": sample_timeline_entry_data}
        )

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesCreateRequest(
            object="don:core:issue:456",
            type=TimelineEntryType.COMMENT,
            body="External comment",
        )
        service.create(request)

        mock_http_client.post.assert_called_once()
        _, call_kwargs = mock_http_client.post.call_args
        payload = call_kwargs["data"]
        assert "visibility" not in payload
        assert "private_to" not in payload
        assert "body_type" not in payload

    def test_create_timeline_entry_with_private_visibility_and_recipients(
        self,
        mock_http_client: MagicMock,
        sample_timeline_entry_data: dict[str, Any],
    ) -> None:
        """Private visibility with private_to is forwarded as-is."""
        mock_http_client.post.return_value = create_mock_response(
            {"timeline_entry": sample_timeline_entry_data}
        )

        service = TimelineEntriesService(mock_http_client)
        request = TimelineEntriesCreateRequest(
            object="don:core:issue:456",
            type=TimelineEntryType.COMMENT,
            body="Private",
            visibility=TimelineEntryVisibility.PRIVATE,
            private_to=["don:identity:dvrv-us-1:devo/1:devu/2"],
        )
        service.create(request)

        _, call_kwargs = mock_http_client.post.call_args
        payload = call_kwargs["data"]
        assert payload["visibility"] == "private"
        assert payload["private_to"] == ["don:identity:dvrv-us-1:devo/1:devu/2"]
