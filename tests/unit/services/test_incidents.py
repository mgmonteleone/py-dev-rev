"""Unit tests for IncidentsService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.incidents import (
    Incident,
    IncidentGroupItem,
    IncidentSeverity,
    IncidentStage,
)
from devrev.services.incidents import IncidentsService

from .conftest import create_mock_response


class TestIncidentsService:
    """Tests for IncidentsService."""

    def test_create_incident(
        self,
        mock_http_client: MagicMock,
        sample_incident_data: dict[str, Any],
    ) -> None:
        """Test creating an incident."""
        mock_http_client.post.return_value = create_mock_response(
            {"incident": sample_incident_data}
        )

        service = IncidentsService(mock_http_client)
        result = service.create(
            title="Test Incident",
            body="Test incident description",
            severity=IncidentSeverity.SEV1,
        )

        assert isinstance(result, Incident)
        assert result.id == "don:core:incident:123"
        assert result.title == "Test Incident"
        assert result.severity == IncidentSeverity.SEV1
        mock_http_client.post.assert_called_once()

    def test_get_incident(
        self,
        mock_http_client: MagicMock,
        sample_incident_data: dict[str, Any],
    ) -> None:
        """Test getting an incident by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"incident": sample_incident_data}
        )

        service = IncidentsService(mock_http_client)
        result = service.get(id="don:core:incident:123")

        assert isinstance(result, Incident)
        assert result.id == "don:core:incident:123"
        assert result.title == "Test Incident"
        mock_http_client.post.assert_called_once()

    def test_list_incidents(
        self,
        mock_http_client: MagicMock,
        sample_incident_data: dict[str, Any],
    ) -> None:
        """Test listing incidents."""
        mock_http_client.post.return_value = create_mock_response(
            {"incidents": [sample_incident_data]}
        )

        service = IncidentsService(mock_http_client)
        result = service.list()

        assert len(result.incidents) == 1
        assert isinstance(result.incidents[0], Incident)
        assert result.incidents[0].id == "don:core:incident:123"
        mock_http_client.post.assert_called_once()

    def test_list_incidents_with_filters(
        self,
        mock_http_client: MagicMock,
        sample_incident_data: dict[str, Any],
    ) -> None:
        """Test listing incidents with stage and severity filters."""
        mock_http_client.post.return_value = create_mock_response(
            {"incidents": [sample_incident_data]}
        )

        service = IncidentsService(mock_http_client)
        result = service.list(
            stage=[IncidentStage.ACKNOWLEDGED, IncidentStage.IDENTIFIED],
            severity=[IncidentSeverity.SEV1, IncidentSeverity.SEV2],
            limit=50,
        )

        assert len(result.incidents) == 1
        assert result.incidents[0].stage == IncidentStage.ACKNOWLEDGED
        assert result.incidents[0].severity == IncidentSeverity.SEV1
        mock_http_client.post.assert_called_once()

    def test_list_incidents_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing incidents returns empty list."""
        mock_http_client.post.return_value = create_mock_response({"incidents": []})

        service = IncidentsService(mock_http_client)
        result = service.list()

        assert len(result.incidents) == 0
        mock_http_client.post.assert_called_once()

    def test_update_incident(
        self,
        mock_http_client: MagicMock,
        sample_incident_data: dict[str, Any],
    ) -> None:
        """Test updating an incident."""
        updated_data = {
            **sample_incident_data,
            "title": "Updated Incident",
            "stage": "resolved",
        }
        mock_http_client.post.return_value = create_mock_response({"incident": updated_data})

        service = IncidentsService(mock_http_client)
        result = service.update(
            id="don:core:incident:123",
            title="Updated Incident",
            stage=IncidentStage.RESOLVED,
        )

        assert isinstance(result, Incident)
        assert result.title == "Updated Incident"
        assert result.stage == IncidentStage.RESOLVED
        mock_http_client.post.assert_called_once()

    def test_delete_incident(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting an incident."""
        mock_http_client.post.return_value = create_mock_response({})

        service = IncidentsService(mock_http_client)
        result = service.delete(id="don:core:incident:123")

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_group_incidents(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test grouping incidents by field."""
        group_data = [
            {"key": "sev1", "count": 5},
            {"key": "sev2", "count": 3},
        ]
        mock_http_client.post.return_value = create_mock_response({"groups": group_data})

        service = IncidentsService(mock_http_client)
        result = service.group(group_by="severity", limit=10)

        assert len(result) == 2
        assert isinstance(result[0], IncidentGroupItem)
        assert result[0].key == "sev1"
        assert result[0].count == 5
        assert result[1].key == "sev2"
        assert result[1].count == 3
        mock_http_client.post.assert_called_once()
