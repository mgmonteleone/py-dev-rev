"""Unit tests for DevRev MCP user tools (dev users and rev users)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev.models.dev_users import DevUserState
from devrev_mcp.tools.users import (
    devrev_dev_users_get,
    devrev_dev_users_list,
    devrev_rev_users_create,
    devrev_rev_users_get,
    devrev_rev_users_list,
)


def _make_mock_dev_user(data: dict | None = None) -> MagicMock:
    """Create a mock DevUser model with model_dump method.

    Args:
        data: Optional dict to return from model_dump.

    Returns:
        MagicMock with model_dump method.
    """
    mock = MagicMock()
    default_data = {
        "id": "DEVU-123",
        "display_name": "Test Dev User",
        "email": "dev@example.com",
        "state": "active",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


def _make_mock_rev_user(data: dict | None = None) -> MagicMock:
    """Create a mock RevUser model with model_dump method.

    Args:
        data: Optional dict to return from model_dump.

    Returns:
        MagicMock with model_dump method.
    """
    mock = MagicMock()
    default_data = {
        "id": "REVU-123",
        "display_name": "Test Rev User",
        "email": "customer@example.com",
        "rev_org": "ORG-123",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


class TestDevUsersListTool:
    """Tests for devrev_dev_users_list tool."""

    async def test_list_returns_paginated_response(self, mock_ctx, mock_client):
        """Test listing dev users returns paginated response."""
        # Arrange
        user1 = _make_mock_dev_user({"id": "DEVU-1", "email": "user1@example.com"})
        user2 = _make_mock_dev_user({"id": "DEVU-2", "email": "user2@example.com"})
        response = MagicMock()
        response.dev_users = [user1, user2]
        response.next_cursor = "cursor-123"
        mock_client.dev_users.list.return_value = response

        # Act
        result = await devrev_dev_users_list(mock_ctx, limit=10)

        # Assert
        assert result["count"] == 2
        assert len(result["dev_users"]) == 2
        assert result["next_cursor"] == "cursor-123"
        assert result["dev_users"][0]["id"] == "DEVU-1"
        mock_client.dev_users.list.assert_called_once_with(
            email=None,
            state=None,
            cursor=None,
            limit=10,
        )

    async def test_list_with_state_filter(self, mock_ctx, mock_client):
        """Test listing dev users with state filter converts to DevUserState enum."""
        # Arrange
        user = _make_mock_dev_user({"state": "active"})
        response = MagicMock()
        response.dev_users = [user]
        response.next_cursor = None
        mock_client.dev_users.list.return_value = response

        # Act
        await devrev_dev_users_list(mock_ctx, state=["ACTIVE", "DEACTIVATED"])

        # Assert
        mock_client.dev_users.list.assert_called_once()
        call_args = mock_client.dev_users.list.call_args
        # Verify state was converted to DevUserState enums
        assert call_args.kwargs["state"] == [DevUserState.ACTIVE, DevUserState.DEACTIVATED]

    async def test_list_with_email_filter(self, mock_ctx, mock_client):
        """Test listing dev users with email filter."""
        # Arrange
        response = MagicMock()
        response.dev_users = []
        response.next_cursor = None
        mock_client.dev_users.list.return_value = response

        # Act
        await devrev_dev_users_list(mock_ctx, email=["test@example.com"])

        # Assert
        mock_client.dev_users.list.assert_called_once_with(
            email=["test@example.com"],
            state=None,
            cursor=None,
            limit=25,
        )

    async def test_list_error(self, mock_ctx, mock_client):
        """Test error handling in dev users list."""
        # Arrange
        mock_client.dev_users.list.side_effect = NotFoundError("Not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_dev_users_list(mock_ctx)


class TestDevUsersGetTool:
    """Tests for devrev_dev_users_get tool."""

    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting a dev user by ID."""
        # Arrange
        user = _make_mock_dev_user({"id": "DEVU-123", "email": "dev@example.com"})
        mock_client.dev_users.get.return_value = user

        # Act
        result = await devrev_dev_users_get(mock_ctx, id="DEVU-123")

        # Assert
        assert result["id"] == "DEVU-123"
        assert result["email"] == "dev@example.com"
        mock_client.dev_users.get.assert_called_once_with("DEVU-123")

    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent dev user."""
        # Arrange
        mock_client.dev_users.get.side_effect = NotFoundError("User not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_dev_users_get(mock_ctx, id="invalid")


class TestRevUsersListTool:
    """Tests for devrev_rev_users_list tool."""

    async def test_list_returns_paginated_response(self, mock_ctx, mock_client):
        """Test listing rev users returns paginated response."""
        # Arrange
        user1 = _make_mock_rev_user({"id": "REVU-1", "email": "customer1@example.com"})
        user2 = _make_mock_rev_user({"id": "REVU-2", "email": "customer2@example.com"})
        response = MagicMock()
        response.rev_users = [user1, user2]
        response.next_cursor = "cursor-456"
        mock_client.rev_users.list.return_value = response

        # Act
        result = await devrev_rev_users_list(mock_ctx, cursor="prev-cursor", limit=50)

        # Assert
        assert result["count"] == 2
        assert len(result["rev_users"]) == 2
        assert result["next_cursor"] == "cursor-456"
        assert result["rev_users"][0]["id"] == "REVU-1"
        assert result["rev_users"][1]["id"] == "REVU-2"
        mock_client.rev_users.list.assert_called_once_with(
            email=None,
            rev_org=None,
            cursor="prev-cursor",
            limit=50,
        )

    async def test_list_with_rev_org_filter(self, mock_ctx, mock_client):
        """Test listing rev users with rev_org filter."""
        # Arrange
        user = _make_mock_rev_user({"rev_org": "ORG-123"})
        response = MagicMock()
        response.rev_users = [user]
        response.next_cursor = None
        mock_client.rev_users.list.return_value = response

        # Act
        await devrev_rev_users_list(mock_ctx, rev_org=["ORG-123"], email=["test@example.com"])

        # Assert
        mock_client.rev_users.list.assert_called_once_with(
            email=["test@example.com"],
            rev_org=["ORG-123"],
            cursor=None,
            limit=25,
        )

    async def test_list_error(self, mock_ctx, mock_client):
        """Test error handling in rev users list."""
        # Arrange
        mock_client.rev_users.list.side_effect = NotFoundError("Not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_rev_users_list(mock_ctx)


class TestRevUsersGetTool:
    """Tests for devrev_rev_users_get tool."""

    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting a rev user by ID."""
        # Arrange
        user = _make_mock_rev_user({"id": "REVU-123", "email": "customer@example.com"})
        mock_client.rev_users.get.return_value = user

        # Act
        result = await devrev_rev_users_get(mock_ctx, id="REVU-123")

        # Assert
        assert result["id"] == "REVU-123"
        assert result["email"] == "customer@example.com"
        mock_client.rev_users.get.assert_called_once_with("REVU-123")

    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent rev user."""
        # Arrange
        mock_client.rev_users.get.side_effect = NotFoundError("User not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_rev_users_get(mock_ctx, id="invalid")


class TestRevUsersCreateTool:
    """Tests for devrev_rev_users_create tool."""

    async def test_create_with_required_fields(self, mock_ctx, mock_client):
        """Test creating a rev user with only required fields."""
        # Arrange
        user = _make_mock_rev_user({"id": "REVU-NEW", "rev_org": "ORG-123"})
        mock_client.rev_users.create.return_value = user

        # Act
        result = await devrev_rev_users_create(mock_ctx, rev_org="ORG-123")

        # Assert
        assert result["id"] == "REVU-NEW"
        assert result["rev_org"] == "ORG-123"
        mock_client.rev_users.create.assert_called_once_with(
            rev_org="ORG-123",
            display_name=None,
            email=None,
            phone_numbers=None,
            external_ref=None,
        )

    async def test_create_with_all_fields(self, mock_ctx, mock_client):
        """Test creating a rev user with all fields."""
        # Arrange
        user = _make_mock_rev_user(
            {
                "id": "REVU-FULL",
                "rev_org": "ORG-123",
                "display_name": "John Doe",
                "email": "john@example.com",
                "phone_numbers": ["+1234567890"],
                "external_ref": "ext-456",
            }
        )
        mock_client.rev_users.create.return_value = user

        # Act
        result = await devrev_rev_users_create(
            mock_ctx,
            rev_org="ORG-123",
            display_name="John Doe",
            email="john@example.com",
            phone_numbers=["+1234567890"],
            external_ref="ext-456",
        )

        # Assert
        assert result["id"] == "REVU-FULL"
        assert result["display_name"] == "John Doe"
        assert result["email"] == "john@example.com"
        mock_client.rev_users.create.assert_called_once_with(
            rev_org="ORG-123",
            display_name="John Doe",
            email="john@example.com",
            phone_numbers=["+1234567890"],
            external_ref="ext-456",
        )

    async def test_create_validation_error(self, mock_ctx, mock_client):
        """Test validation error during rev user creation."""
        # Arrange
        mock_client.rev_users.create.side_effect = ValidationError(
            "Validation failed",
            status_code=400,
            field_errors={"rev_org": "required"},
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Validation error"):
            await devrev_rev_users_create(mock_ctx, rev_org="")
