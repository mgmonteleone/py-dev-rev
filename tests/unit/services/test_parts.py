"""Unit tests for PartsService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.parts import (
    Part,
    PartsCreateRequest,
    PartsDeleteRequest,
    PartsGetRequest,
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
        mock_http_client.post.return_value = create_mock_response({"part": sample_part_data})

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
        mock_http_client.post.return_value = create_mock_response({"part": sample_part_data})

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
        mock_http_client.post.return_value = create_mock_response({"parts": [sample_part_data]})

        service = PartsService(mock_http_client)
        result = service.list()

        assert len(result.parts) == 1
        assert isinstance(result.parts[0], Part)
        assert result.parts[0].id == "don:core:part:123"
        mock_http_client.post.assert_called_once()

    def test_list_parts_with_request(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing parts with pagination."""
        mock_http_client.post.return_value = create_mock_response({"parts": [sample_part_data]})

        service = PartsService(mock_http_client)
        result = service.list(limit=50)

        assert len(result.parts) == 1
        mock_http_client.post.assert_called_once()

    def test_update_part(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test updating a part."""
        updated_data = {**sample_part_data, "name": "Updated Part"}
        mock_http_client.post.return_value = create_mock_response({"part": updated_data})

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
        mock_http_client.post.return_value = create_mock_response({"parts": parts})

        service = PartsService(mock_http_client)
        result = service.list()

        assert len(result.parts) == 2
        assert result.parts[0].name == "Test Part"
        assert result.parts[1].name == "Part 2"
        mock_http_client.post.assert_called_once()

    def test_list_parts_with_parent_part_filter(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test listing parts filtered by parent part hierarchy."""
        mock_http_client.post.return_value = create_mock_response({"parts": [sample_part_data]})

        service = PartsService(mock_http_client)
        result = service.list(
            parent_part_parts=["PROD-12345"],
            parent_part_level=2,
        )

        assert len(result.parts) == 1
        mock_http_client.post.assert_called_once()
        sent = mock_http_client.post.call_args.kwargs["data"]
        assert sent["parent_part"] == {"parts": ["PROD-12345"], "level": 2}

    def test_list_parts_parent_part_filter_omitted_when_unset(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test that parent_part is not sent when no parent filter is provided."""
        mock_http_client.post.return_value = create_mock_response({"parts": [sample_part_data]})

        service = PartsService(mock_http_client)
        service.list(limit=10)

        sent = mock_http_client.post.call_args.kwargs["data"]
        assert "parent_part" not in sent

    def test_part_preserves_artifacts_and_tags(
        self,
        mock_http_client: MagicMock,
        sample_part_data: dict[str, Any],
    ) -> None:
        """Test that artifacts, tags, and owners are preserved on the Part model."""
        enriched = {
            **sample_part_data,
            "owned_by": [{"id": "don:identity:user:789", "display_name": "Owner"}],
            "artifacts": [{"id": "ARTIFACT-1", "file_name": "spec.pdf"}],
            "tags": [{"tag": {"id": "TAG-1", "name": "priority"}, "value": "high"}],
        }
        mock_http_client.post.return_value = create_mock_response({"part": enriched})

        service = PartsService(mock_http_client)
        result = service.get(PartsGetRequest(id="don:core:part:123"))

        assert result.artifacts is not None
        assert result.artifacts[0].id == "ARTIFACT-1"
        assert result.tags is not None
        assert result.tags[0].value == "high"
        assert result.owned_by is not None
        assert result.owned_by[0].id == "don:identity:user:789"
