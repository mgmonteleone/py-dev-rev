"""Unit tests for BrandsService.

Refs #92
"""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.brands import Brand
from devrev.services.brands import BrandsService

from .conftest import create_mock_response


class TestBrandsService:
    """Tests for BrandsService."""

    def test_create_brand(
        self,
        mock_http_client: MagicMock,
        sample_brand_data: dict[str, Any],
    ) -> None:
        """Test creating a brand."""
        mock_http_client.post.return_value = create_mock_response({"brand": sample_brand_data})

        service = BrandsService(mock_http_client)
        result = service.create(
            name="Test Brand",
            description="Test brand description",
            logo_url="https://example.com/logo.png",
        )

        assert isinstance(result, Brand)
        assert result.id == "don:core:brand:123"
        assert result.name == "Test Brand"
        assert result.description == "Test brand description"
        assert result.logo_url == "https://example.com/logo.png"
        mock_http_client.post.assert_called_once()

    def test_get_brand(
        self,
        mock_http_client: MagicMock,
        sample_brand_data: dict[str, Any],
    ) -> None:
        """Test getting a brand by ID."""
        mock_http_client.post.return_value = create_mock_response({"brand": sample_brand_data})

        service = BrandsService(mock_http_client)
        result = service.get(id="don:core:brand:123")

        assert isinstance(result, Brand)
        assert result.id == "don:core:brand:123"
        assert result.name == "Test Brand"
        mock_http_client.post.assert_called_once()

    def test_list_brands(
        self,
        mock_http_client: MagicMock,
        sample_brand_data: dict[str, Any],
    ) -> None:
        """Test listing brands."""
        mock_http_client.post.return_value = create_mock_response({"brands": [sample_brand_data]})

        service = BrandsService(mock_http_client)
        result = service.list()

        assert len(result.brands) == 1
        assert isinstance(result.brands[0], Brand)
        assert result.brands[0].id == "don:core:brand:123"
        mock_http_client.post.assert_called_once()

    def test_list_brands_with_pagination(
        self,
        mock_http_client: MagicMock,
        sample_brand_data: dict[str, Any],
    ) -> None:
        """Test listing brands with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"brands": [sample_brand_data], "next_cursor": "next-page"}
        )

        service = BrandsService(mock_http_client)
        result = service.list(cursor="current-cursor", limit=50)

        assert len(result.brands) == 1
        assert result.next_cursor == "next-page"
        mock_http_client.post.assert_called_once()

    def test_list_brands_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing brands returns empty list."""
        mock_http_client.post.return_value = create_mock_response({"brands": []})

        service = BrandsService(mock_http_client)
        result = service.list()

        assert len(result.brands) == 0
        mock_http_client.post.assert_called_once()

    def test_update_brand(
        self,
        mock_http_client: MagicMock,
        sample_brand_data: dict[str, Any],
    ) -> None:
        """Test updating a brand."""
        updated_data = {**sample_brand_data, "name": "Updated Brand"}
        mock_http_client.post.return_value = create_mock_response({"brand": updated_data})

        service = BrandsService(mock_http_client)
        result = service.update(
            id="don:core:brand:123",
            name="Updated Brand",
        )

        assert isinstance(result, Brand)
        assert result.name == "Updated Brand"
        mock_http_client.post.assert_called_once()

    def test_delete_brand(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a brand."""
        mock_http_client.post.return_value = create_mock_response({})

        service = BrandsService(mock_http_client)
        result = service.delete(id="don:core:brand:123")

        assert result is None
        mock_http_client.post.assert_called_once()
