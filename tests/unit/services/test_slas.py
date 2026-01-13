"""Unit tests for SlasService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.slas import (
    Sla,
    SlasCreateRequest,
    SlasGetRequest,
    SlasListRequest,
    SlaTrackerStatus,
    SlasTransitionRequest,
    SlasUpdateRequest,
)
from devrev.services.slas import SlasService

from .conftest import create_mock_response


class TestSlasService:
    """Tests for SlasService."""

    def test_create_sla(
        self,
        mock_http_client: MagicMock,
        sample_sla_data: dict[str, Any],
    ) -> None:
        """Test creating an SLA."""
        mock_http_client.post.return_value = create_mock_response(
            {"sla": sample_sla_data}
        )

        service = SlasService(mock_http_client)
        request = SlasCreateRequest(
            name="Test SLA",
            description="Test SLA description",
            target_time=120,
        )
        result = service.create(request)

        assert isinstance(result, Sla)
        assert result.id == "don:core:sla:123"
        assert result.name == "Test SLA"
        mock_http_client.post.assert_called_once()

    def test_get_sla(
        self,
        mock_http_client: MagicMock,
        sample_sla_data: dict[str, Any],
    ) -> None:
        """Test getting an SLA by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"sla": sample_sla_data}
        )

        service = SlasService(mock_http_client)
        request = SlasGetRequest(id="don:core:sla:123")
        result = service.get(request)

        assert isinstance(result, Sla)
        assert result.id == "don:core:sla:123"
        mock_http_client.post.assert_called_once()

    def test_list_slas(
        self,
        mock_http_client: MagicMock,
        sample_sla_data: dict[str, Any],
    ) -> None:
        """Test listing SLAs."""
        mock_http_client.post.return_value = create_mock_response(
            {"slas": [sample_sla_data]}
        )

        service = SlasService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], Sla)
        assert result[0].id == "don:core:sla:123"
        mock_http_client.post.assert_called_once()

    def test_list_slas_with_request(
        self,
        mock_http_client: MagicMock,
        sample_sla_data: dict[str, Any],
    ) -> None:
        """Test listing SLAs with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"slas": [sample_sla_data]}
        )

        service = SlasService(mock_http_client)
        request = SlasListRequest(limit=50, cursor="next-cursor")
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_sla(
        self,
        mock_http_client: MagicMock,
        sample_sla_data: dict[str, Any],
    ) -> None:
        """Test updating an SLA."""
        updated_data = {**sample_sla_data, "name": "Updated SLA"}
        mock_http_client.post.return_value = create_mock_response(
            {"sla": updated_data}
        )

        service = SlasService(mock_http_client)
        request = SlasUpdateRequest(
            id="don:core:sla:123",
            name="Updated SLA",
        )
        result = service.update(request)

        assert isinstance(result, Sla)
        assert result.name == "Updated SLA"
        mock_http_client.post.assert_called_once()

    def test_transition_sla(
        self,
        mock_http_client: MagicMock,
        sample_sla_data: dict[str, Any],
    ) -> None:
        """Test transitioning an SLA status."""
        transitioned_data = {**sample_sla_data, "status": "paused"}
        mock_http_client.post.return_value = create_mock_response(
            {"sla": transitioned_data}
        )

        service = SlasService(mock_http_client)
        request = SlasTransitionRequest(
            id="don:core:sla:123",
            status=SlaTrackerStatus.PAUSED,
        )
        result = service.transition(request)

        assert isinstance(result, Sla)
        assert result.status == "paused"
        mock_http_client.post.assert_called_once()

    def test_list_slas_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing SLAs returns empty list."""
        mock_http_client.post.return_value = create_mock_response(
            {"slas": []}
        )

        service = SlasService(mock_http_client)
        result = service.list()

        assert len(result) == 0
        mock_http_client.post.assert_called_once()

