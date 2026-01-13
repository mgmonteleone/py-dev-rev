"""Unit tests for CodeChangesService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.code_changes import (
    CodeChange,
    CodeChangesCreateRequest,
    CodeChangesDeleteRequest,
    CodeChangesGetRequest,
    CodeChangesListRequest,
    CodeChangesUpdateRequest,
)
from devrev.services.code_changes import CodeChangesService

from .conftest import create_mock_response


class TestCodeChangesService:
    """Tests for CodeChangesService."""

    def test_create_code_change(
        self,
        mock_http_client: MagicMock,
        sample_code_change_data: dict[str, Any],
    ) -> None:
        """Test creating a code change."""
        mock_http_client.post.return_value = create_mock_response(
            {"code_change": sample_code_change_data}
        )

        service = CodeChangesService(mock_http_client)
        request = CodeChangesCreateRequest(
            title="Test Code Change",
            description="Test description",
            repository="https://github.com/org/repo",
            branch="main",
        )
        result = service.create(request)

        assert isinstance(result, CodeChange)
        assert result.id == "don:core:code_change:123"
        assert result.title == "Test Code Change"
        mock_http_client.post.assert_called_once()

    def test_get_code_change(
        self,
        mock_http_client: MagicMock,
        sample_code_change_data: dict[str, Any],
    ) -> None:
        """Test getting a code change by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"code_change": sample_code_change_data}
        )

        service = CodeChangesService(mock_http_client)
        request = CodeChangesGetRequest(id="don:core:code_change:123")
        result = service.get(request)

        assert isinstance(result, CodeChange)
        assert result.id == "don:core:code_change:123"
        mock_http_client.post.assert_called_once()

    def test_list_code_changes(
        self,
        mock_http_client: MagicMock,
        sample_code_change_data: dict[str, Any],
    ) -> None:
        """Test listing code changes."""
        mock_http_client.post.return_value = create_mock_response(
            {"code_changes": [sample_code_change_data]}
        )

        service = CodeChangesService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], CodeChange)
        assert result[0].id == "don:core:code_change:123"
        mock_http_client.post.assert_called_once()

    def test_list_code_changes_with_request(
        self,
        mock_http_client: MagicMock,
        sample_code_change_data: dict[str, Any],
    ) -> None:
        """Test listing code changes with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"code_changes": [sample_code_change_data]}
        )

        service = CodeChangesService(mock_http_client)
        request = CodeChangesListRequest(limit=50, cursor="next-cursor")
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_code_change(
        self,
        mock_http_client: MagicMock,
        sample_code_change_data: dict[str, Any],
    ) -> None:
        """Test updating a code change."""
        updated_data = {**sample_code_change_data, "title": "Updated Title"}
        mock_http_client.post.return_value = create_mock_response(
            {"code_change": updated_data}
        )

        service = CodeChangesService(mock_http_client)
        request = CodeChangesUpdateRequest(
            id="don:core:code_change:123",
            title="Updated Title",
        )
        result = service.update(request)

        assert isinstance(result, CodeChange)
        assert result.title == "Updated Title"
        mock_http_client.post.assert_called_once()

    def test_delete_code_change(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a code change."""
        mock_http_client.post.return_value = create_mock_response({})

        service = CodeChangesService(mock_http_client)
        request = CodeChangesDeleteRequest(id="don:core:code_change:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_code_changes_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing code changes returns empty list."""
        mock_http_client.post.return_value = create_mock_response(
            {"code_changes": []}
        )

        service = CodeChangesService(mock_http_client)
        result = service.list()

        assert len(result) == 0
        mock_http_client.post.assert_called_once()

