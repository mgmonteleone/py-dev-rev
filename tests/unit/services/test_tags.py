"""Unit tests for TagsService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.tags import (
    Tag,
    TagsCreateRequest,
    TagsDeleteRequest,
    TagsGetRequest,
    TagsListRequest,
    TagsUpdateRequest,
)
from devrev.services.tags import TagsService

from .conftest import create_mock_response


class TestTagsService:
    """Tests for TagsService."""

    def test_create_tag(
        self,
        mock_http_client: MagicMock,
        sample_tag_data: dict[str, Any],
    ) -> None:
        """Test creating a tag."""
        mock_http_client.post.return_value = create_mock_response(
            {"tag": sample_tag_data}
        )

        service = TagsService(mock_http_client)
        request = TagsCreateRequest(
            name="test-tag",
            description="A test tag",
        )
        result = service.create(request)

        assert isinstance(result, Tag)
        assert result.id == "don:core:tag:123"
        assert result.name == "test-tag"
        mock_http_client.post.assert_called_once()

    def test_get_tag(
        self,
        mock_http_client: MagicMock,
        sample_tag_data: dict[str, Any],
    ) -> None:
        """Test getting a tag by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"tag": sample_tag_data}
        )

        service = TagsService(mock_http_client)
        request = TagsGetRequest(id="don:core:tag:123")
        result = service.get(request)

        assert isinstance(result, Tag)
        assert result.id == "don:core:tag:123"
        mock_http_client.post.assert_called_once()

    def test_list_tags(
        self,
        mock_http_client: MagicMock,
        sample_tag_data: dict[str, Any],
    ) -> None:
        """Test listing tags."""
        mock_http_client.post.return_value = create_mock_response(
            {"tags": [sample_tag_data]}
        )

        service = TagsService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], Tag)
        assert result[0].id == "don:core:tag:123"
        mock_http_client.post.assert_called_once()

    def test_list_tags_with_request(
        self,
        mock_http_client: MagicMock,
        sample_tag_data: dict[str, Any],
    ) -> None:
        """Test listing tags with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"tags": [sample_tag_data]}
        )

        service = TagsService(mock_http_client)
        request = TagsListRequest(limit=50, cursor="next-cursor")
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_tag(
        self,
        mock_http_client: MagicMock,
        sample_tag_data: dict[str, Any],
    ) -> None:
        """Test updating a tag."""
        updated_data = {**sample_tag_data, "name": "updated-tag"}
        mock_http_client.post.return_value = create_mock_response(
            {"tag": updated_data}
        )

        service = TagsService(mock_http_client)
        request = TagsUpdateRequest(
            id="don:core:tag:123",
            name="updated-tag",
        )
        result = service.update(request)

        assert isinstance(result, Tag)
        assert result.name == "updated-tag"
        mock_http_client.post.assert_called_once()

    def test_delete_tag(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a tag."""
        mock_http_client.post.return_value = create_mock_response({})

        service = TagsService(mock_http_client)
        request = TagsDeleteRequest(id="don:core:tag:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_tags_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing tags returns empty list."""
        mock_http_client.post.return_value = create_mock_response(
            {"tags": []}
        )

        service = TagsService(mock_http_client)
        result = service.list()

        assert len(result) == 0
        mock_http_client.post.assert_called_once()

