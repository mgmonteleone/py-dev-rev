"""Unit tests for PartsService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.parts import (
    Part,
    PartsCreateRequest,
    PartsDeleteRequest,
    PartsGetRequest,
    PartsListRequest,
    PartsUpdateRequest,
    PartType,
)
from devrev.services.parts import PartsService

from .conftest import create_mock_response


class TestPartsService:
    """Tests for PartsService."""

    def test_create_part(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test creating a part."""
        mock_http_client.post.return_value = create_mock_response(
            {"part": sample_part_data}
        )

        service = PartsService(mock_http_client)
        request = PartsCreateRequest(
            name="Test Part",
            type=PartType.PRODUCT,
            description="Test part description",
        )
        result = service.create(request)

        assert isinstance(result, Part)
        assert result.id == "don:core:part:123"
        assert result.name == "Test Part"
        mock_http_client.post.assert_called_once()

    def test_get_part(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test getting a part by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"part": sample_part_data}
        )

        service = PartsService(mock_http_client)
        request = PartsGetRequest(id="don:core:part:123")
        result = service.get(request)

        assert isinstance(result, Part)
        assert result.id == "don:core:part:123"
        mock_http_client.post.assert_called_once()

    def test_list_parts(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing parts."""
        mock_http_client.post.return_value = create_mock_response(
            {"parts": [sample_part_data]}
        )

        service = PartsService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], Part)
        assert result[0].id == "don:core:part:123"
        mock_http_client.post.assert_called_once()

    def test_list_parts_with_request(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing parts with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"parts": [sample_part_data]}
        )

        service = PartsService(mock_http_client)
        request = PartsListRequest(limit=50)
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_part(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test updating a part."""
        updated_data = {**sample_part_data, "name": "Updated Part"}
        mock_http_client.post.return_value = create_mock_response(
            {"part": updated_data}
        )

        service = PartsService(mock_http_client)
        request = PartsUpdateRequest(
            id="don:core:part:123",
            name="Updated Part",
        )
        result = service.update(request)

        assert isinstance(result, Part)
        assert result.name == "Updated Part"
        mock_http_client.post.assert_called_once()

    def test_delete_part(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a part."""
        mock_http_client.post.return_value = create_mock_response({})

        service = PartsService(mock_http_client)
        request = PartsDeleteRequest(id="don:core:part:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_parts_multiple(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing multiple parts."""
        parts = [
            sample_part_data,
            {**sample_part_data, "id": "don:core:part:456", "name": "Part 2"},
        ]
        mock_http_client.post.return_value = create_mock_response(
            {"parts": parts}
        )

        service = PartsService(mock_http_client)
        result = service.list()

        assert len(result) == 2
        assert result[0].name == "Test Part"
        assert result[1].name == "Part 2"
        mock_http_client.post.assert_called_once()

