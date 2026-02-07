"""Unit tests for DevRev MCP incidents tools (beta API)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev.models.incidents import IncidentSeverity, IncidentStage
from devrev_mcp.tools.incidents import (
    devrev_incidents_create,
    devrev_incidents_delete,
    devrev_incidents_get,
    devrev_incidents_group,
    devrev_incidents_list,
    devrev_incidents_update,
)


def _make_mock_incident(overrides: dict | None = None) -> MagicMock:
    """Create a mock Incident object with model_dump method.

    Args:
        overrides: Optional dict to override default field values.

    Returns:
        MagicMock configured to behave like an Incident model.
    """
    defaults = {
        "id": "INC-123",
        "display_id": "INC-123",
        "title": "Test Incident",
        "body": "Test incident description",
        "severity": "sev1",
        "stage": "open",
        "owned_by": ["user-1"],
        "applies_to_parts": ["part-1"],
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
    }
    if overrides:
        defaults.update(overrides)

    mock = MagicMock()
    mock.model_dump.return_value = defaults
    return mock


def _make_mock_group_item(overrides: dict | None = None) -> MagicMock:
    """Create a mock IncidentGroupItem object.

    Args:
        overrides: Optional dict to override default field values.

    Returns:
        MagicMock configured to behave like an IncidentGroupItem model.
    """
    defaults = {
        "key": "sev1",
        "count": 5,
    }
    if overrides:
        defaults.update(overrides)

    mock = MagicMock()
    mock.model_dump.return_value = defaults
    return mock


class TestIncidentsListTool:
    """Tests for devrev_incidents_list tool."""

    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing incidents with empty results."""
        # Arrange
        response = MagicMock()
        response.incidents = []
        response.next_cursor = None
        mock_client.incidents.list = AsyncMock(return_value=response)

        # Act
        result = await devrev_incidents_list(mock_ctx)

        # Assert
        assert result["count"] == 0
        assert result["incidents"] == []
        assert "next_cursor" not in result
        mock_client.incidents.list.assert_called_once_with(
            cursor=None,
            limit=25,
            stage=None,
            severity=None,
        )

    async def test_list_with_results(self, mock_ctx, mock_client):
        """Test listing incidents with results."""
        # Arrange
        incidents = [
            _make_mock_incident({"id": "INC-1", "title": "Incident 1"}),
            _make_mock_incident({"id": "INC-2", "title": "Incident 2"}),
        ]
        response = MagicMock()
        response.incidents = incidents
        response.next_cursor = None
        mock_client.incidents.list = AsyncMock(return_value=response)

        # Act
        result = await devrev_incidents_list(mock_ctx)

        # Assert
        assert result["count"] == 2
        assert len(result["incidents"]) == 2
        assert result["incidents"][0]["id"] == "INC-1"
        assert result["incidents"][1]["id"] == "INC-2"

    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing incidents with pagination."""
        # Arrange
        incidents = [_make_mock_incident({"id": f"INC-{i}"}) for i in range(10)]
        response = MagicMock()
        response.incidents = incidents
        response.next_cursor = "next-page-token"
        mock_client.incidents.list = AsyncMock(return_value=response)

        # Act
        result = await devrev_incidents_list(mock_ctx, cursor="current-cursor", limit=10)

        # Assert
        assert result["count"] == 10
        assert result["next_cursor"] == "next-page-token"
        mock_client.incidents.list.assert_called_once_with(
            cursor="current-cursor",
            limit=10,
            stage=None,
            severity=None,
        )

    async def test_list_with_filters(self, mock_ctx, mock_client):
        """Test listing incidents with stage and severity filters."""
        # Arrange
        response = MagicMock()
        response.incidents = []
        response.next_cursor = None
        mock_client.incidents.list = AsyncMock(return_value=response)

        # Act
        result = await devrev_incidents_list(
            mock_ctx,
            stage=["acknowledged", "resolved"],
            severity=["sev0", "sev1"],
        )

        # Assert
        assert result["count"] == 0
        mock_client.incidents.list.assert_called_once_with(
            cursor=None,
            limit=25,
            stage=[IncidentStage.ACKNOWLEDGED, IncidentStage.RESOLVED],
            severity=[IncidentSeverity.SEV0, IncidentSeverity.SEV1],
        )

    async def test_list_error(self, mock_ctx, mock_client):
        """Test listing incidents with API error."""
        # Arrange
        mock_client.incidents.list = AsyncMock(side_effect=ValidationError("Invalid filter"))

        # Act & Assert
        with pytest.raises(RuntimeError, match="Invalid filter"):
            await devrev_incidents_list(mock_ctx)


class TestIncidentsGetTool:
    """Tests for devrev_incidents_get tool."""

    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting an incident by ID."""
        # Arrange
        incident = _make_mock_incident({"id": "INC-123", "title": "Test Incident"})
        mock_client.incidents.get = AsyncMock(return_value=incident)

        # Act
        result = await devrev_incidents_get(mock_ctx, id="INC-123")

        # Assert
        assert result["id"] == "INC-123"
        assert result["title"] == "Test Incident"
        mock_client.incidents.get.assert_called_once_with("INC-123")

    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent incident."""
        # Arrange
        mock_client.incidents.get = AsyncMock(side_effect=NotFoundError("Incident not found"))

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_incidents_get(mock_ctx, id="nonexistent")


class TestIncidentsCreateTool:
    """Tests for devrev_incidents_create tool."""

    async def test_create_minimal(self, mock_ctx, mock_client):
        """Test creating an incident with minimal fields."""
        # Arrange
        incident = _make_mock_incident({"id": "INC-NEW", "title": "New Incident"})
        mock_client.incidents.create = AsyncMock(return_value=incident)

        # Act
        result = await devrev_incidents_create(mock_ctx, title="New Incident")

        # Assert
        assert result["id"] == "INC-NEW"
        assert result["title"] == "New Incident"
        mock_client.incidents.create.assert_called_once_with(
            title="New Incident",
            body=None,
            severity=None,
            owned_by=None,
            applies_to_parts=None,
        )

    async def test_create_full_with_severity(self, mock_ctx, mock_client):
        """Test creating an incident with all fields including severity."""
        # Arrange
        incident = _make_mock_incident(
            {
                "id": "INC-FULL",
                "title": "Critical Incident",
                "severity": "sev1",
            }
        )
        mock_client.incidents.create = AsyncMock(return_value=incident)

        # Act
        result = await devrev_incidents_create(
            mock_ctx,
            title="Critical Incident",
            body="This is critical",
            severity="sev1",
            owned_by=["user-1", "user-2"],
            applies_to_parts=["part-1"],
        )

        # Assert
        assert result["id"] == "INC-FULL"
        assert result["title"] == "Critical Incident"
        mock_client.incidents.create.assert_called_once_with(
            title="Critical Incident",
            body="This is critical",
            severity=IncidentSeverity.SEV1,
            owned_by=["user-1", "user-2"],
            applies_to_parts=["part-1"],
        )

    async def test_create_error(self, mock_ctx, mock_client):
        """Test creating an incident with validation error."""
        # Arrange
        mock_client.incidents.create = AsyncMock(side_effect=ValidationError("Title required"))

        # Act & Assert
        with pytest.raises(RuntimeError, match="Title required"):
            await devrev_incidents_create(mock_ctx, title="")


class TestIncidentsUpdateTool:
    """Tests for devrev_incidents_update tool."""

    async def test_update_success_with_stage_severity(self, mock_ctx, mock_client):
        """Test updating an incident with stage and severity."""
        # Arrange
        incident = _make_mock_incident(
            {
                "id": "INC-123",
                "title": "Updated Incident",
                "stage": "resolved",
                "severity": "sev2",
            }
        )
        mock_client.incidents.update = AsyncMock(return_value=incident)

        # Act
        result = await devrev_incidents_update(
            mock_ctx,
            id="INC-123",
            title="Updated Incident",
            stage="resolved",
            severity="sev2",
        )

        # Assert
        assert result["id"] == "INC-123"
        assert result["title"] == "Updated Incident"
        mock_client.incidents.update.assert_called_once_with(
            "INC-123",
            title="Updated Incident",
            body=None,
            stage=IncidentStage.RESOLVED,
            severity=IncidentSeverity.SEV2,
        )

    async def test_update_error(self, mock_ctx, mock_client):
        """Test updating an incident with error."""
        # Arrange
        mock_client.incidents.update = AsyncMock(side_effect=NotFoundError("Incident not found"))

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_incidents_update(mock_ctx, id="nonexistent", title="New Title")


class TestIncidentsDeleteTool:
    """Tests for devrev_incidents_delete tool."""

    async def test_delete_success(self, mock_ctx, mock_client):
        """Test deleting an incident."""
        # Arrange
        mock_client.incidents.delete = AsyncMock(return_value=None)

        # Act
        result = await devrev_incidents_delete(mock_ctx, id="INC-123")

        # Assert
        assert result["deleted"] is True
        assert result["id"] == "INC-123"
        mock_client.incidents.delete.assert_called_once_with("INC-123")

    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test deleting a non-existent incident."""
        # Arrange
        mock_client.incidents.delete = AsyncMock(side_effect=NotFoundError("Incident not found"))

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_incidents_delete(mock_ctx, id="nonexistent")


class TestIncidentsGroupTool:
    """Tests for devrev_incidents_group tool."""

    async def test_group_success(self, mock_ctx, mock_client):
        """Test grouping incidents."""
        # Arrange
        groups = [
            _make_mock_group_item({"key": "sev1", "count": 5}),
            _make_mock_group_item({"key": "sev2", "count": 3}),
        ]
        mock_client.incidents.group = AsyncMock(return_value=groups)

        # Act
        result = await devrev_incidents_group(mock_ctx, group_by="severity", limit=10)

        # Assert
        assert result["count"] == 2
        assert len(result["groups"]) == 2
        assert result["groups"][0]["key"] == "sev1"
        assert result["groups"][0]["count"] == 5
        assert result["groups"][1]["key"] == "sev2"
        assert result["groups"][1]["count"] == 3
        mock_client.incidents.group.assert_called_once_with(group_by="severity", limit=10)

    async def test_group_error(self, mock_ctx, mock_client):
        """Test grouping incidents with error."""
        # Arrange
        mock_client.incidents.group = AsyncMock(side_effect=ValidationError("Invalid group_by"))

        # Act & Assert
        with pytest.raises(RuntimeError, match="Invalid group_by"):
            await devrev_incidents_group(mock_ctx, group_by="invalid_field")
