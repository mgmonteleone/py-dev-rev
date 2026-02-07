"""Unit tests for DevRev MCP account tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev_mcp.tools.accounts import (
    devrev_accounts_create,
    devrev_accounts_delete,
    devrev_accounts_get,
    devrev_accounts_list,
    devrev_accounts_merge,
    devrev_accounts_update,
)


def _make_mock_account(data: dict | None = None) -> MagicMock:
    """Create a mock Account model with model_dump method.

    Args:
        data: Optional dict to return from model_dump.

    Returns:
        MagicMock with model_dump method.
    """
    mock = MagicMock()
    default_data = {
        "id": "ACC-123",
        "display_name": "Test Account",
        "created_date": "2026-01-01T00:00:00Z",
    }
    if data:
        default_data.update(data)
    mock.model_dump.return_value = default_data
    return mock


class TestAccountsListTool:
    """Tests for devrev_accounts_list tool."""

    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing accounts with empty results."""
        # Arrange
        response = MagicMock()
        response.accounts = []
        response.next_cursor = None
        mock_client.accounts.list.return_value = response

        # Act
        result = await devrev_accounts_list(mock_ctx)

        # Assert
        assert result["count"] == 0
        assert result["accounts"] == []
        assert "next_cursor" not in result
        mock_client.accounts.list.assert_called_once_with(
            display_name=None,
            domains=None,
            owned_by=None,
            cursor=None,
            limit=25,
        )

    async def test_list_with_results(self, mock_ctx, mock_client):
        """Test listing accounts with results."""
        # Arrange
        account1 = _make_mock_account({"id": "ACC-1", "display_name": "Account 1"})
        account2 = _make_mock_account({"id": "ACC-2", "display_name": "Account 2"})
        response = MagicMock()
        response.accounts = [account1, account2]
        response.next_cursor = None
        mock_client.accounts.list.return_value = response

        # Act
        result = await devrev_accounts_list(mock_ctx)

        # Assert
        assert result["count"] == 2
        assert len(result["accounts"]) == 2
        assert result["accounts"][0]["id"] == "ACC-1"
        assert result["accounts"][1]["id"] == "ACC-2"

    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing accounts with pagination cursor."""
        # Arrange
        account = _make_mock_account()
        response = MagicMock()
        response.accounts = [account]
        response.next_cursor = "cursor-123"
        mock_client.accounts.list.return_value = response

        # Act
        result = await devrev_accounts_list(mock_ctx, cursor="prev-cursor", limit=10)

        # Assert
        assert result["count"] == 1
        assert result["next_cursor"] == "cursor-123"
        mock_client.accounts.list.assert_called_once_with(
            display_name=None,
            domains=None,
            owned_by=None,
            cursor="prev-cursor",
            limit=10,
        )

    async def test_list_with_filters(self, mock_ctx, mock_client):
        """Test listing accounts with filters."""
        # Arrange
        response = MagicMock()
        response.accounts = []
        response.next_cursor = None
        mock_client.accounts.list.return_value = response

        # Act
        await devrev_accounts_list(
            mock_ctx,
            display_name=["Test Account"],
            domains=["example.com"],
            owned_by=["user-1"],
        )

        # Assert
        mock_client.accounts.list.assert_called_once_with(
            display_name=["Test Account"],
            domains=["example.com"],
            owned_by=["user-1"],
            cursor=None,
            limit=25,
        )

    async def test_list_clamps_page_size(self, mock_ctx, mock_client):
        """Test that page size is clamped to max 100."""
        # Arrange
        response = MagicMock()
        response.accounts = []
        response.next_cursor = None
        mock_client.accounts.list.return_value = response

        # Act
        await devrev_accounts_list(mock_ctx, limit=500)

        # Assert
        mock_client.accounts.list.assert_called_once()
        call_args = mock_client.accounts.list.call_args
        assert call_args.kwargs["limit"] == 100

    async def test_list_error(self, mock_ctx, mock_client):
        """Test error handling in list."""
        # Arrange
        mock_client.accounts.list.side_effect = NotFoundError("Not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_accounts_list(mock_ctx)


class TestAccountsGetTool:
    """Tests for devrev_accounts_get tool."""

    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting an account by ID."""
        # Arrange
        account = _make_mock_account({"id": "ACC-123", "display_name": "Test Account"})
        mock_client.accounts.get.return_value = account

        # Act
        result = await devrev_accounts_get(mock_ctx, id="ACC-123")

        # Assert
        assert result["id"] == "ACC-123"
        assert result["display_name"] == "Test Account"
        mock_client.accounts.get.assert_called_once_with("ACC-123")

    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent account."""
        # Arrange
        mock_client.accounts.get.side_effect = NotFoundError("Account not found", status_code=404)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_accounts_get(mock_ctx, id="invalid")


class TestAccountsCreateTool:
    """Tests for devrev_accounts_create tool."""

    async def test_create_minimal(self, mock_ctx, mock_client):
        """Test creating an account with minimal fields."""
        # Arrange
        account = _make_mock_account({"id": "ACC-NEW", "display_name": "New Account"})
        mock_client.accounts.create.return_value = account

        # Act
        result = await devrev_accounts_create(mock_ctx, display_name="New Account")

        # Assert
        assert result["id"] == "ACC-NEW"
        assert result["display_name"] == "New Account"
        mock_client.accounts.create.assert_called_once_with(
            display_name="New Account",
            description=None,
            domains=None,
            external_refs=None,
            owned_by=None,
            tier=None,
        )

    async def test_create_full(self, mock_ctx, mock_client):
        """Test creating an account with all fields."""
        # Arrange
        account = _make_mock_account(
            {
                "id": "ACC-FULL",
                "display_name": "Full Account",
                "description": "Test description",
                "domains": ["example.com"],
                "tier": "enterprise",
            }
        )
        mock_client.accounts.create.return_value = account

        # Act
        result = await devrev_accounts_create(
            mock_ctx,
            display_name="Full Account",
            description="Test description",
            domains=["example.com"],
            external_refs=["ext-123"],
            owned_by=["user-1"],
            tier="enterprise",
        )

        # Assert
        assert result["id"] == "ACC-FULL"
        mock_client.accounts.create.assert_called_once_with(
            display_name="Full Account",
            description="Test description",
            domains=["example.com"],
            external_refs=["ext-123"],
            owned_by=["user-1"],
            tier="enterprise",
        )

    async def test_create_validation_error(self, mock_ctx, mock_client):
        """Test validation error during account creation."""
        # Arrange
        mock_client.accounts.create.side_effect = ValidationError(
            "Validation failed",
            status_code=400,
            field_errors={"display_name": "required"},
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Validation error"):
            await devrev_accounts_create(mock_ctx, display_name="")


class TestAccountsUpdateTool:
    """Tests for devrev_accounts_update tool."""

    async def test_update_display_name(self, mock_ctx, mock_client):
        """Test updating account display name."""
        # Arrange
        account = _make_mock_account({"id": "ACC-123", "display_name": "Updated Name"})
        mock_client.accounts.update.return_value = account

        # Act
        result = await devrev_accounts_update(mock_ctx, id="ACC-123", display_name="Updated Name")

        # Assert
        assert result["display_name"] == "Updated Name"
        mock_client.accounts.update.assert_called_once_with(
            "ACC-123",
            display_name="Updated Name",
            description=None,
            tier=None,
        )

    async def test_update_error(self, mock_ctx, mock_client):
        """Test error during account update."""
        # Arrange
        mock_client.accounts.update.side_effect = NotFoundError(
            "Account not found", status_code=404
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_accounts_update(mock_ctx, id="invalid", display_name="New Name")


class TestAccountsDeleteTool:
    """Tests for devrev_accounts_delete tool."""

    async def test_delete_success(self, mock_ctx, mock_client):
        """Test deleting an account."""
        # Arrange
        mock_client.accounts.delete.return_value = None

        # Act
        result = await devrev_accounts_delete(mock_ctx, id="ACC-123")

        # Assert
        assert result["deleted"] is True
        assert result["id"] == "ACC-123"
        mock_client.accounts.delete.assert_called_once_with("ACC-123")

    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test deleting a non-existent account."""
        # Arrange
        mock_client.accounts.delete.side_effect = NotFoundError(
            "Account not found", status_code=404
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Not found"):
            await devrev_accounts_delete(mock_ctx, id="invalid")


class TestAccountsMergeTool:
    """Tests for devrev_accounts_merge tool."""

    async def test_merge_success(self, mock_ctx, mock_client):
        """Test merging two accounts."""
        # Arrange
        account = _make_mock_account({"id": "ACC-PRIMARY", "display_name": "Primary Account"})
        mock_client.accounts.merge.return_value = account

        # Act
        result = await devrev_accounts_merge(
            mock_ctx,
            primary_account="ACC-PRIMARY",
            secondary_account="ACC-SECONDARY",
        )

        # Assert
        assert result["id"] == "ACC-PRIMARY"
        mock_client.accounts.merge.assert_called_once_with(
            primary_account="ACC-PRIMARY",
            secondary_account="ACC-SECONDARY",
        )

    async def test_merge_error(self, mock_ctx, mock_client):
        """Test error during account merge."""
        # Arrange
        mock_client.accounts.merge.side_effect = ValidationError(
            "Cannot merge accounts",
            status_code=400,
        )

        # Act & Assert
        with pytest.raises(RuntimeError, match="Validation error"):
            await devrev_accounts_merge(
                mock_ctx,
                primary_account="ACC-1",
                secondary_account="ACC-2",
            )
