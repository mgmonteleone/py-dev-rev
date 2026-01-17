"""Unit tests for UomsService.

Refs #92
"""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.uoms import Uom, UomAggregationType, UomMetricScope
from devrev.services.uoms import UomsService

from .conftest import create_mock_response


class TestUomsService:
    """Tests for UomsService."""

    def test_create_uom(
        self,
        mock_http_client: MagicMock,
        sample_uom_data: dict[str, Any],
    ) -> None:
        """Test creating a UOM."""
        mock_http_client.post.return_value = create_mock_response({"uom": sample_uom_data})

        service = UomsService(mock_http_client)
        result = service.create(
            name="Test UOM",
            aggregation_type=UomAggregationType.SUM,
            description="Test description",
            metric_scope=UomMetricScope.ORG,
        )

        assert isinstance(result, Uom)
        assert result.id == "don:core:uom:123"
        assert result.name == "Test UOM"
        assert result.description == "Test description"
        mock_http_client.post.assert_called_once()

    def test_create_uom_minimal(
        self,
        mock_http_client: MagicMock,
        sample_uom_data: dict[str, Any],
    ) -> None:
        """Test creating a UOM with minimal parameters."""
        minimal_data = {
            "id": "don:core:uom:456",
            "name": "Minimal UOM",
            "aggregation_type": "maximum",
            "is_enabled": True,
        }
        mock_http_client.post.return_value = create_mock_response({"uom": minimal_data})

        service = UomsService(mock_http_client)
        result = service.create(
            name="Minimal UOM",
            aggregation_type=UomAggregationType.MAXIMUM,
        )

        assert isinstance(result, Uom)
        assert result.id == "don:core:uom:456"
        assert result.name == "Minimal UOM"
        mock_http_client.post.assert_called_once()

    def test_get_uom(
        self,
        mock_http_client: MagicMock,
        sample_uom_data: dict[str, Any],
    ) -> None:
        """Test getting a UOM by ID."""
        mock_http_client.post.return_value = create_mock_response({"uom": sample_uom_data})

        service = UomsService(mock_http_client)
        result = service.get(id="don:core:uom:123")

        assert isinstance(result, Uom)
        assert result.id == "don:core:uom:123"
        assert result.name == "Test UOM"
        mock_http_client.post.assert_called_once()

    def test_list_uoms(
        self,
        mock_http_client: MagicMock,
        sample_uom_data: dict[str, Any],
    ) -> None:
        """Test listing UOMs."""
        mock_http_client.post.return_value = create_mock_response({"uoms": [sample_uom_data]})

        service = UomsService(mock_http_client)
        result = service.list()

        assert len(result.uoms) == 1
        assert isinstance(result.uoms[0], Uom)
        assert result.uoms[0].id == "don:core:uom:123"
        mock_http_client.post.assert_called_once()

    def test_list_uoms_with_pagination(
        self,
        mock_http_client: MagicMock,
        sample_uom_data: dict[str, Any],
    ) -> None:
        """Test listing UOMs with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"uoms": [sample_uom_data], "next_cursor": "next-page"}
        )

        service = UomsService(mock_http_client)
        result = service.list(cursor="current-cursor", limit=50)

        assert len(result.uoms) == 1
        assert result.next_cursor == "next-page"
        mock_http_client.post.assert_called_once()

    def test_list_uoms_with_filters(
        self,
        mock_http_client: MagicMock,
        sample_uom_data: dict[str, Any],
    ) -> None:
        """Test listing UOMs with filters."""
        mock_http_client.post.return_value = create_mock_response({"uoms": [sample_uom_data]})

        service = UomsService(mock_http_client)
        result = service.list(
            aggregation_type=[UomAggregationType.SUM, UomAggregationType.MAXIMUM],
            is_enabled=True,
        )

        assert len(result.uoms) == 1
        mock_http_client.post.assert_called_once()

    def test_list_uoms_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing UOMs returns empty list."""
        mock_http_client.post.return_value = create_mock_response({"uoms": []})

        service = UomsService(mock_http_client)
        result = service.list()

        assert len(result.uoms) == 0
        mock_http_client.post.assert_called_once()

    def test_update_uom(
        self,
        mock_http_client: MagicMock,
        sample_uom_data: dict[str, Any],
    ) -> None:
        """Test updating a UOM."""
        updated_data = {**sample_uom_data, "name": "Updated UOM"}
        mock_http_client.post.return_value = create_mock_response({"uom": updated_data})

        service = UomsService(mock_http_client)
        result = service.update(
            id="don:core:uom:123",
            name="Updated UOM",
        )

        assert isinstance(result, Uom)
        assert result.name == "Updated UOM"
        mock_http_client.post.assert_called_once()

    def test_update_uom_multiple_fields(
        self,
        mock_http_client: MagicMock,
        sample_uom_data: dict[str, Any],
    ) -> None:
        """Test updating multiple UOM fields."""
        updated_data = {
            **sample_uom_data,
            "name": "Updated UOM",
            "description": "Updated description",
            "is_enabled": False,
        }
        mock_http_client.post.return_value = create_mock_response({"uom": updated_data})

        service = UomsService(mock_http_client)
        result = service.update(
            id="don:core:uom:123",
            name="Updated UOM",
            description="Updated description",
            is_enabled=False,
        )

        assert isinstance(result, Uom)
        assert result.name == "Updated UOM"
        assert result.description == "Updated description"
        assert result.is_enabled is False
        mock_http_client.post.assert_called_once()

    def test_delete_uom(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a UOM."""
        mock_http_client.post.return_value = create_mock_response({})

        service = UomsService(mock_http_client)
        result = service.delete(id="don:core:uom:123")

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_count_uoms(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test counting UOMs."""
        mock_http_client.post.return_value = create_mock_response({"count": 42})

        service = UomsService(mock_http_client)
        result = service.count()

        assert result == 42
        mock_http_client.post.assert_called_once()

    def test_count_uoms_with_filters(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test counting UOMs with filters."""
        mock_http_client.post.return_value = create_mock_response({"count": 10})

        service = UomsService(mock_http_client)
        result = service.count(
            aggregation_type=[UomAggregationType.SUM],
            is_enabled=True,
        )

        assert result == 10
        mock_http_client.post.assert_called_once()

    def test_count_uoms_zero(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test counting UOMs returns zero."""
        mock_http_client.post.return_value = create_mock_response({"count": 0})

        service = UomsService(mock_http_client)
        result = service.count()

        assert result == 0
        mock_http_client.post.assert_called_once()
