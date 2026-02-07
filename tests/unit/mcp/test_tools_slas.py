"""Unit tests for DevRev MCP SLA tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev_mcp.tools.slas import (
    devrev_slas_create,
    devrev_slas_get,
    devrev_slas_list,
    devrev_slas_transition,
    devrev_slas_update,
)


def _make_mock_sla(data: dict | None = None) -> MagicMock:
    """Create a mock SLA model with model_dump method.

    Args:
        data: Optional dict to return from model_dump.

    Returns:
        MagicMock with model_dump method.
    """
    mock = MagicMock()
    default_data = {
        "id": "don:core:dvrv-us-1:devo/1:sla/123",
        "name": "Standard SLA",
        "description": "Standard response time SLA",
        "status": "published",
        "target_time": 120,
        "created_date": "2026-01-01T00:00:00Z",
        "modified_date": "2026-01-01T00:00:00Z",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


class TestSlasListTool:
    """Tests for devrev_slas_list tool."""

    async def test_slas_list_success(self, mock_ctx, mock_client):
        """Test listing SLAs with results."""
        # Arrange
        sla = _make_mock_sla()
        mock_client.slas.list.return_value = [sla]

        # Act
        result = await devrev_slas_list(mock_ctx)

        # Assert
        assert result["count"] == 1
        assert len(result["slas"]) == 1
        assert result["slas"][0]["id"] == "don:core:dvrv-us-1:devo/1:sla/123"
        assert result["slas"][0]["name"] == "Standard SLA"
        mock_client.slas.list.assert_called_once()

    async def test_slas_list_empty(self, mock_ctx, mock_client):
        """Test listing SLAs with empty results."""
        # Arrange
        mock_client.slas.list.return_value = []

        # Act
        result = await devrev_slas_list(mock_ctx)

        # Assert
        assert result["count"] == 0
        assert result["slas"] == []
        mock_client.slas.list.assert_called_once()

    async def test_slas_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing SLAs with pagination parameters."""
        # Arrange
        sla1 = _make_mock_sla({"id": "SLA-1", "name": "SLA 1"})
        sla2 = _make_mock_sla({"id": "SLA-2", "name": "SLA 2"})
        mock_client.slas.list.return_value = [sla1, sla2]

        # Act
        result = await devrev_slas_list(mock_ctx, cursor="cursor-123", limit=10)

        # Assert
        assert result["count"] == 2
        assert len(result["slas"]) == 2
        mock_client.slas.list.assert_called_once()

    async def test_slas_list_error(self, mock_ctx, mock_client):
        """Test listing SLAs with error."""
        # Arrange
        mock_client.slas.list.side_effect = NotFoundError("Not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_slas_list(mock_ctx)


class TestSlasGetTool:
    """Tests for devrev_slas_get tool."""

    async def test_slas_get_success(self, mock_ctx, mock_client):
        """Test getting an SLA successfully."""
        # Arrange
        sla = _make_mock_sla()
        mock_client.slas.get.return_value = sla

        # Act
        result = await devrev_slas_get(mock_ctx, id="SLA-123")

        # Assert
        assert result["id"] == "don:core:dvrv-us-1:devo/1:sla/123"
        assert result["name"] == "Standard SLA"
        assert result["target_time"] == 120
        mock_client.slas.get.assert_called_once()

    async def test_slas_get_error(self, mock_ctx, mock_client):
        """Test getting a non-existent SLA."""
        # Arrange
        mock_client.slas.get.side_effect = NotFoundError("SLA not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="SLA not found"):
            await devrev_slas_get(mock_ctx, id="SLA-999")


class TestSlasCreateTool:
    """Tests for devrev_slas_create tool."""

    async def test_slas_create_success(self, mock_ctx, mock_client):
        """Test creating an SLA with minimal parameters."""
        # Arrange
        sla = _make_mock_sla({"name": "New SLA"})
        mock_client.slas.create.return_value = sla

        # Act
        result = await devrev_slas_create(mock_ctx, name="New SLA")

        # Assert
        assert result["name"] == "New SLA"
        mock_client.slas.create.assert_called_once()

    async def test_slas_create_with_target_time(self, mock_ctx, mock_client):
        """Test creating an SLA with all parameters."""
        # Arrange
        sla = _make_mock_sla(
            {"name": "Premium SLA", "description": "Premium support", "target_time": 60}
        )
        mock_client.slas.create.return_value = sla

        # Act
        result = await devrev_slas_create(
            mock_ctx, name="Premium SLA", description="Premium support", target_time=60
        )

        # Assert
        assert result["name"] == "Premium SLA"
        assert result["description"] == "Premium support"
        assert result["target_time"] == 60
        mock_client.slas.create.assert_called_once()

    async def test_slas_create_validation_error(self, mock_ctx, mock_client):
        """Test creating an SLA with validation error."""
        # Arrange
        mock_client.slas.create.side_effect = ValidationError("Invalid name", status_code=400)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Invalid name"):
            await devrev_slas_create(mock_ctx, name="")


class TestSlasUpdateTool:
    """Tests for devrev_slas_update tool."""

    async def test_slas_update_success(self, mock_ctx, mock_client):
        """Test updating an SLA successfully."""
        # Arrange
        sla = _make_mock_sla({"name": "Updated SLA", "description": "Updated description"})
        mock_client.slas.update.return_value = sla

        # Act
        result = await devrev_slas_update(
            mock_ctx, id="SLA-123", name="Updated SLA", description="Updated description"
        )

        # Assert
        assert result["name"] == "Updated SLA"
        assert result["description"] == "Updated description"
        mock_client.slas.update.assert_called_once()

    async def test_slas_update_error(self, mock_ctx, mock_client):
        """Test updating an SLA with error."""
        # Arrange
        mock_client.slas.update.side_effect = NotFoundError("SLA not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="SLA not found"):
            await devrev_slas_update(mock_ctx, id="SLA-999", name="New Name")


class TestSlasTransitionTool:
    """Tests for devrev_slas_transition tool."""

    async def test_slas_transition_with_sla_status(self, mock_ctx, mock_client):
        """Test transitioning an SLA with SlaStatus enum value."""
        # Arrange
        sla = _make_mock_sla({"status": "published"})
        mock_client.slas.transition.return_value = sla

        # Act
        result = await devrev_slas_transition(mock_ctx, id="SLA-123", status="published")

        # Assert
        assert result["status"] == "published"
        mock_client.slas.transition.assert_called_once()

    async def test_slas_transition_with_tracker_status(self, mock_ctx, mock_client):
        """Test transitioning an SLA with SlaTrackerStatus enum value."""
        # Arrange
        sla = _make_mock_sla({"status": "active"})
        mock_client.slas.transition.return_value = sla

        # Act
        result = await devrev_slas_transition(mock_ctx, id="SLA-123", status="active")

        # Assert
        assert result["status"] == "active"
        mock_client.slas.transition.assert_called_once()

    async def test_slas_transition_with_raw_string(self, mock_ctx, mock_client):
        """Test transitioning an SLA with raw string status."""
        # Arrange
        sla = _make_mock_sla({"status": "custom_status"})
        mock_client.slas.transition.return_value = sla

        # Act
        result = await devrev_slas_transition(mock_ctx, id="SLA-123", status="custom_status")

        # Assert
        assert result["status"] == "custom_status"
        mock_client.slas.transition.assert_called_once()

    async def test_slas_transition_error(self, mock_ctx, mock_client):
        """Test transitioning an SLA with error."""
        # Arrange
        mock_client.slas.transition.side_effect = ValidationError(
            "Invalid status transition", status_code=400
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Invalid status transition"):
            await devrev_slas_transition(mock_ctx, id="SLA-123", status="invalid")
