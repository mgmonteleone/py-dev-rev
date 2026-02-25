"""End-to-end integration tests for Accounts endpoints.

Tests the full account lifecycle: create, get, list, update, delete.
Uses real API calls against the DevRev instance.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_accounts_e2e.py -v -m write

Related to Issue #142: E2E integration tests for Accounts CRUD lifecycle
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from devrev.exceptions import DevRevError, NotFoundError

if TYPE_CHECKING:
    from devrev.client import DevRevClient
    from tests.integration.utils import TestDataManager

logger = logging.getLogger(__name__)

# Mark all tests in this module
# Check for either DEVREV_API_TOKEN or DEVREV_TEST_API_TOKEN (matches write_client fixture)
_has_api_token = bool(os.environ.get("DEVREV_API_TOKEN") or os.environ.get("DEVREV_TEST_API_TOKEN"))

pytestmark = [
    pytest.mark.integration,
    pytest.mark.write,
    pytest.mark.skipif(
        not _has_api_token,
        reason="DEVREV_API_TOKEN or DEVREV_TEST_API_TOKEN environment variable required",
    ),
    pytest.mark.skipif(
        os.environ.get("DEVREV_WRITE_TESTS_ENABLED", "").lower() not in ("true", "1", "yes"),
        reason="DEVREV_WRITE_TESTS_ENABLED must be set to 'true' for write tests",
    ),
]


class TestAccountsCRUD:
    """CRUD integration tests for Accounts service.

    Demonstrates full create/read/update/delete lifecycle testing
    with proper cleanup and isolation.
    """

    def test_create_account_basic(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating an account with only required fields."""
        # Arrange
        display_name = test_data.generate_name("account")

        # Act
        account = write_client.accounts.create(display_name=display_name)
        test_data.register("account", account.id)

        # Assert
        assert account.id is not None
        assert account.display_name == display_name
        logger.info(f"✅ Created account: {account.id}")

    def test_create_account_with_description(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating an account with display_name and description."""
        # Arrange
        display_name = test_data.generate_name("account")
        description = "Test account for integration testing"

        # Act
        account = write_client.accounts.create(
            display_name=display_name,
            description=description,
        )
        test_data.register("account", account.id)

        # Assert
        assert account.id is not None
        assert account.display_name == display_name
        assert account.description == description
        logger.info(f"✅ Created account with description: {account.id}")

    def test_get_account_by_id(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test retrieving an account by ID."""
        # Arrange - create account first
        display_name = test_data.generate_name("account")
        created_account = write_client.accounts.create(display_name=display_name)
        test_data.register("account", created_account.id)

        # Act
        retrieved_account = write_client.accounts.get(id=created_account.id)

        # Assert
        assert retrieved_account.id == created_account.id
        assert retrieved_account.display_name == display_name
        logger.info(f"✅ Retrieved account: {created_account.id}")

    def test_list_accounts(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing accounts."""
        # Arrange - no setup needed

        # Act
        result = write_client.accounts.list(limit=5)

        # Assert
        assert hasattr(result, "accounts")
        assert isinstance(result.accounts, list)
        logger.info(f"✅ Listed accounts: {len(result.accounts)} found")

    def test_update_account_display_name(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating an account's display_name."""
        # Arrange - create account first
        original_name = test_data.generate_name("account")
        account = write_client.accounts.create(display_name=original_name)
        test_data.register("account", account.id)

        # Act
        new_name = test_data.generate_name("account")
        updated_account = write_client.accounts.update(id=account.id, display_name=new_name)

        # Assert
        assert updated_account.id == account.id
        assert updated_account.display_name == new_name
        logger.info(f"✅ Updated account display_name: {account.id}")

    def test_update_account_description(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating an account's description."""
        # Arrange - create account first
        display_name = test_data.generate_name("account")
        original_description = "Original description"
        account = write_client.accounts.create(
            display_name=display_name,
            description=original_description,
        )
        test_data.register("account", account.id)

        # Act
        new_description = "Updated description for integration testing"
        updated_account = write_client.accounts.update(
            id=account.id,
            description=new_description,
        )

        # Assert
        assert updated_account.description == new_description
        logger.info(f"✅ Updated account description: {account.id}")

    def test_delete_account(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test deleting an account."""
        # Arrange - create account first
        display_name = test_data.generate_name("account")
        account = write_client.accounts.create(display_name=display_name)
        # Note: NOT registering since we're testing delete

        # Act
        write_client.accounts.delete(id=account.id)

        # Assert - verify account is deleted by trying to get it
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.accounts.get(id=account.id)
        logger.info(f"✅ Deleted account: {account.id}")

    def test_account_full_lifecycle(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test full account lifecycle: create -> get -> update -> list -> delete."""
        # Arrange
        display_name = test_data.generate_name("account")
        description = "Lifecycle test account"

        # Act & Assert - Create
        account = write_client.accounts.create(
            display_name=display_name,
            description=description,
        )
        # Note: NOT registering since we're testing delete
        assert account.id is not None
        assert account.display_name == display_name
        assert account.description == description
        logger.info(f"✅ Lifecycle - Created: {account.id}")

        # Act & Assert - Get
        retrieved = write_client.accounts.get(id=account.id)
        assert retrieved.id == account.id
        assert retrieved.display_name == display_name
        logger.info(f"✅ Lifecycle - Retrieved: {account.id}")

        # Act & Assert - Update
        new_name = test_data.generate_name("account")
        new_description = "Updated lifecycle test account"
        updated = write_client.accounts.update(
            id=account.id,
            display_name=new_name,
            description=new_description,
        )
        assert updated.display_name == new_name
        assert updated.description == new_description
        logger.info(f"✅ Lifecycle - Updated: {account.id}")

        # Act & Assert - List
        result = write_client.accounts.list(limit=10)
        assert hasattr(result, "accounts")
        assert isinstance(result.accounts, list)
        logger.info(f"✅ Lifecycle - Listed: {len(result.accounts)} accounts")

        # Act & Assert - Delete
        write_client.accounts.delete(id=account.id)
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.accounts.get(id=account.id)
        logger.info(f"✅ Lifecycle - Deleted: {account.id}")


class TestAccountsErrorHandling:
    """Tests for error handling in accounts operations.

    Validates that the SDK properly handles and reports errors
    from the API for invalid account operations.
    """

    def test_get_nonexistent_account_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that getting a non-existent account raises an error."""
        # Arrange
        fake_id = "don:identity:dvrv-us-1:devo/fake:account/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.accounts.get(id=fake_id)
        logger.info("✅ Get non-existent account correctly raised error")

    def test_update_nonexistent_account_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that updating a non-existent account raises an error."""
        # Arrange
        fake_id = "don:identity:dvrv-us-1:devo/fake:account/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.accounts.update(
                id=fake_id,
                display_name=test_data.generate_name("account"),
            )
        logger.info("✅ Update non-existent account correctly raised error")

    def test_delete_nonexistent_account_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that deleting a non-existent account raises an error."""
        # Arrange
        fake_id = "don:identity:dvrv-us-1:devo/fake:account/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.accounts.delete(id=fake_id)
        logger.info("✅ Delete non-existent account correctly raised error")


class TestAccountsListPagination:
    """Tests for accounts list pagination.

    Validates that pagination parameters work correctly.
    """

    def test_list_accounts_with_limit(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing accounts with a limit parameter."""
        # Arrange
        limit = 2

        # Act
        result = write_client.accounts.list(limit=limit)

        # Assert
        assert hasattr(result, "accounts")
        assert isinstance(result.accounts, list)
        assert len(result.accounts) <= limit
        logger.info(f"✅ Listed accounts with limit={limit}: {len(result.accounts)} found")

    def test_list_accounts_default(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing accounts with default parameters."""
        # Arrange - no specific parameters

        # Act
        result = write_client.accounts.list()

        # Assert
        assert hasattr(result, "accounts")
        assert isinstance(result.accounts, list)
        logger.info(f"✅ Listed accounts with defaults: {len(result.accounts)} found")
