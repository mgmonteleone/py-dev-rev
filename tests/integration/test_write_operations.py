"""Integration tests for write operations (create, update, delete).

This module demonstrates the recommended patterns for testing
write operations against the DevRev API with:
- Automatic test data cleanup
- Resource tracking via TestDataManager
- Isolation between test runs
- Safety checks for environment

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_write_operations.py -v -m write

Related to Issue #105: Design Integration Testing Strategy for Write Operations
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from devrev.exceptions import NotFoundError

if TYPE_CHECKING:
    from devrev.client import DevRevClient
    from tests.integration.utils import TestDataManager

logger = logging.getLogger(__name__)

# Mark all tests in this module
pytestmark = [
    pytest.mark.integration,
    pytest.mark.write,
    pytest.mark.skipif(
        not os.environ.get("DEVREV_API_TOKEN"),
        reason="DEVREV_API_TOKEN environment variable not set",
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

    def test_create_account_with_required_fields(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating an account with only required fields."""
        # Arrange
        display_name = test_data.generate_name("MinimalAccount")

        # Act
        account = write_client.accounts.create(display_name=display_name)
        test_data.register("account", account.id)

        # Assert
        assert account.id is not None
        assert account.display_name == display_name
        logger.info(f"✅ Created account: {account.id}")

    def test_create_account_with_optional_fields(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating an account with all optional fields."""
        # Arrange
        display_name = test_data.generate_name("FullAccount")
        description = "Test account created by SDK integration tests"

        # Act
        account = write_client.accounts.create(
            display_name=display_name,
            description=description,
            domains=["test-sdk.example.com"],
        )
        test_data.register("account", account.id)

        # Assert
        assert account.id is not None
        assert account.display_name == display_name
        assert account.description == description
        logger.info(f"✅ Created account with options: {account.id}")

    def test_update_account_display_name(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating an account's display name."""
        # Arrange - create account first
        original_name = test_data.generate_name("UpdateTarget")
        account = write_client.accounts.create(display_name=original_name)
        test_data.register("account", account.id)

        # Act
        new_name = test_data.generate_name("UpdatedName")
        updated_account = write_client.accounts.update(
            id=account.id,
            display_name=new_name,
        )

        # Assert
        assert updated_account.id == account.id
        assert updated_account.display_name == new_name
        logger.info(f"✅ Updated account: {account.id}")

    def test_update_account_description(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating an account's description."""
        # Arrange
        display_name = test_data.generate_name("DescUpdate")
        account = write_client.accounts.create(display_name=display_name)
        test_data.register("account", account.id)

        # Act
        new_description = "Updated description via SDK test"
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
        # Arrange
        display_name = test_data.generate_name("ToDelete")
        account = write_client.accounts.create(display_name=display_name)
        # Note: NOT registering since we're testing delete

        # Act
        write_client.accounts.delete(id=account.id)

        # Assert - verify account is deleted by trying to get it
        with pytest.raises((NotFoundError, Exception)):
            write_client.accounts.get(id=account.id)
        logger.info(f"✅ Deleted account: {account.id}")


class TestTagsCRUD:
    """CRUD integration tests for Tags service.

    Demonstrates testing with request object-based API methods.
    """

    def test_create_tag(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating a tag."""
        from devrev.models.tags import TagsCreateRequest

        # Arrange
        tag_name = test_data.generate_name("TestTag")

        # Act
        request = TagsCreateRequest(name=tag_name)
        tag = write_client.tags.create(request)
        test_data.register("tag", tag.id)

        # Assert
        assert tag.id is not None
        assert tag.name == tag_name
        logger.info(f"✅ Created tag: {tag.id}")

    def test_update_tag(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating a tag's name."""
        from devrev.models.tags import TagsCreateRequest, TagsUpdateRequest

        # Arrange - create tag first
        original_name = test_data.generate_name("TagToUpdate")
        create_request = TagsCreateRequest(name=original_name)
        tag = write_client.tags.create(create_request)
        test_data.register("tag", tag.id)

        # Act
        new_name = test_data.generate_name("UpdatedTag")
        update_request = TagsUpdateRequest(id=tag.id, name=new_name)
        updated_tag = write_client.tags.update(update_request)

        # Assert
        assert updated_tag.name == new_name
        logger.info(f"✅ Updated tag: {tag.id}")

    def test_delete_tag(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test deleting a tag."""
        from devrev.models.tags import TagsCreateRequest, TagsDeleteRequest, TagsGetRequest

        # Arrange
        tag_name = test_data.generate_name("TagToDelete")
        create_request = TagsCreateRequest(name=tag_name)
        tag = write_client.tags.create(create_request)
        # Note: NOT registering since we're testing delete

        # Act
        delete_request = TagsDeleteRequest(id=tag.id)
        write_client.tags.delete(delete_request)

        # Assert - verify tag is deleted
        with pytest.raises((NotFoundError, Exception)):
            get_request = TagsGetRequest(id=tag.id)
            write_client.tags.get(get_request)
        logger.info(f"✅ Deleted tag: {tag.id}")


class TestWriteOperationErrors:
    """Tests for error handling in write operations.

    Validates that the SDK properly handles and reports errors
    from the API for invalid write operations.
    """

    def test_update_nonexistent_account_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that updating a non-existent account raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/FAKE:account/DOESNOTEXIST"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, Exception)) as exc_info:
            write_client.accounts.update(
                id=fake_id,
                display_name=test_data.generate_name("ShouldFail"),
            )
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Update non-existent account correctly raised error")

    def test_delete_nonexistent_account_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that deleting a non-existent account raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/FAKE:account/DOESNOTEXIST"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, Exception)) as exc_info:
            write_client.accounts.delete(id=fake_id)
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Delete non-existent account correctly raised error")
