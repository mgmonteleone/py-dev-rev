"""End-to-end integration tests for Contacts (Rev Users) endpoints.

Tests the full contact lifecycle: create, get, list, update, delete.
Uses real API calls against the DevRev instance.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_contacts_e2e.py -v -m write

Related to Issue #142: E2E integration tests for Contacts (Rev Users) CRUD lifecycle
"""

from __future__ import annotations

import logging
import os
import uuid
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

# Known rev_org ID for testing (from DevRev instance)
REV_ORG_ID = "don:identity:dvrv-us-1:devo/11Ca9baGrM:revo/2ZGx7WNI"


class TestContactsCRUD:
    """CRUD integration tests for Rev Users (Contacts) service.

    Demonstrates full create/read/update/delete lifecycle testing
    with proper cleanup and isolation.
    """

    def test_create_contact_basic(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating a contact with only rev_org (minimal required)."""
        # Arrange - no additional fields needed

        # Act
        contact = write_client.rev_users.create(REV_ORG_ID)
        test_data.register("rev_user", contact.id)

        # Assert
        assert contact.id is not None
        assert contact.id.startswith("don:identity:")
        logger.info(f"✅ Created basic contact: {contact.id}")

    def test_create_contact_with_display_name(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating a contact with display name."""
        # Arrange
        display_name = test_data.generate_name("Contact")

        # Act
        contact = write_client.rev_users.create(REV_ORG_ID, display_name=display_name)
        test_data.register("rev_user", contact.id)

        # Assert
        assert contact.id is not None
        assert contact.display_name == display_name
        logger.info(f"✅ Created contact with display name: {contact.id}")

    def test_create_contact_with_email(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating a contact with email address."""
        # Arrange
        uuid_suffix = uuid.uuid4().hex[:8]
        email = f"sdk_test_{uuid_suffix}@example.com"

        # Act
        contact = write_client.rev_users.create(REV_ORG_ID, email=email)
        test_data.register("rev_user", contact.id)

        # Assert
        assert contact.id is not None
        assert contact.email == email
        logger.info(f"✅ Created contact with email: {contact.id}")

    def test_get_contact_by_id(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test retrieving a contact by ID."""
        # Arrange - create contact first
        display_name = test_data.generate_name("GetContact")
        created_contact = write_client.rev_users.create(REV_ORG_ID, display_name=display_name)
        test_data.register("rev_user", created_contact.id)

        # Act
        retrieved_contact = write_client.rev_users.get(id=created_contact.id)

        # Assert
        assert retrieved_contact.id == created_contact.id
        assert retrieved_contact.display_name == display_name
        logger.info(f"✅ Retrieved contact: {created_contact.id}")

    def test_list_contacts(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing contacts."""
        # Arrange - no setup needed

        # Act
        result = write_client.rev_users.list(limit=5)

        # Assert
        assert result is not None
        assert hasattr(result, "rev_users")
        assert isinstance(result.rev_users, list)
        logger.info(f"✅ Listed contacts: {len(result.rev_users)} found")

    def test_update_contact_display_name(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating a contact's display name."""
        # Arrange - create contact first
        original_name = test_data.generate_name("OriginalName")
        contact = write_client.rev_users.create(REV_ORG_ID, display_name=original_name)
        test_data.register("rev_user", contact.id)

        # Act
        new_name = test_data.generate_name("UpdatedName")
        updated_contact = write_client.rev_users.update(id=contact.id, display_name=new_name)

        # Assert
        assert updated_contact.id == contact.id
        assert updated_contact.display_name == new_name
        logger.info(f"✅ Updated contact display name: {contact.id}")

    def test_update_contact_email(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating a contact's email address."""
        # Arrange - create contact first
        uuid_suffix = uuid.uuid4().hex[:8]
        original_email = f"sdk_test_original_{uuid_suffix}@example.com"
        contact = write_client.rev_users.create(REV_ORG_ID, email=original_email)
        test_data.register("rev_user", contact.id)

        # Act
        new_uuid = uuid.uuid4().hex[:8]
        new_email = f"sdk_test_updated_{new_uuid}@example.com"
        updated_contact = write_client.rev_users.update(id=contact.id, email=new_email)

        # Assert
        assert updated_contact.id == contact.id
        assert updated_contact.email == new_email
        logger.info(f"✅ Updated contact email: {contact.id}")

    def test_delete_contact(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test deleting a contact."""
        # Arrange - create contact first
        display_name = test_data.generate_name("ToDelete")
        contact = write_client.rev_users.create(REV_ORG_ID, display_name=display_name)
        # Note: NOT registering since we're testing delete

        # Act
        write_client.rev_users.delete(id=contact.id)

        # Assert - verify contact is deleted by trying to get it
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.rev_users.get(id=contact.id)
        logger.info(f"✅ Deleted contact: {contact.id}")

    def test_contact_full_lifecycle(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test full contact lifecycle: create -> get -> update -> list -> delete."""
        # Arrange
        display_name = test_data.generate_name("LifecycleContact")
        uuid_suffix = uuid.uuid4().hex[:8]
        email = f"sdk_test_lifecycle_{uuid_suffix}@example.com"

        # Act & Assert - Create
        contact = write_client.rev_users.create(
            REV_ORG_ID,
            display_name=display_name,
            email=email,
        )
        # Note: NOT registering since we're testing delete
        assert contact.id is not None
        assert contact.display_name == display_name
        assert contact.email == email
        logger.info(f"✅ Lifecycle - Created: {contact.id}")

        # Act & Assert - Get
        retrieved = write_client.rev_users.get(id=contact.id)
        assert retrieved.id == contact.id
        assert retrieved.display_name == display_name
        logger.info(f"✅ Lifecycle - Retrieved: {contact.id}")

        # Act & Assert - Update
        new_name = test_data.generate_name("UpdatedLifecycle")
        updated = write_client.rev_users.update(id=contact.id, display_name=new_name)
        assert updated.display_name == new_name
        logger.info(f"✅ Lifecycle - Updated: {contact.id}")

        # Act & Assert - List
        result = write_client.rev_users.list(limit=10)
        assert isinstance(result.rev_users, list)
        logger.info(f"✅ Lifecycle - Listed: {len(result.rev_users)} contacts")

        # Act & Assert - Delete
        write_client.rev_users.delete(id=contact.id)
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.rev_users.get(id=contact.id)
        logger.info(f"✅ Lifecycle - Deleted: {contact.id}")


class TestContactsErrorHandling:
    """Tests for error handling in contacts operations.

    Validates that the SDK properly handles and reports errors
    from the API for invalid contact operations.
    """

    def test_get_nonexistent_contact_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that getting a non-existent contact raises an error."""
        # Arrange
        fake_id = "don:identity:dvrv-us-1:devo/fake:revu/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.rev_users.get(id=fake_id)
        logger.info("✅ Get non-existent contact correctly raised error")

    def test_update_nonexistent_contact_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that updating a non-existent contact raises an error."""
        # Arrange
        fake_id = "don:identity:dvrv-us-1:devo/fake:revu/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.rev_users.update(
                id=fake_id,
                display_name=test_data.generate_name("ShouldFail"),
            )
        logger.info("✅ Update non-existent contact correctly raised error")

    def test_delete_nonexistent_contact_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that deleting a non-existent contact raises an error."""
        # Arrange
        fake_id = "don:identity:dvrv-us-1:devo/fake:revu/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.rev_users.delete(id=fake_id)
        logger.info("✅ Delete non-existent contact correctly raised error")


class TestContactsListPagination:
    """Tests for contacts list pagination.

    Validates that pagination parameters work correctly.
    """

    def test_list_contacts_with_limit(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing contacts with a limit parameter."""
        # Arrange
        limit = 2

        # Act
        result = write_client.rev_users.list(limit=limit)

        # Assert
        assert result is not None
        assert hasattr(result, "rev_users")
        assert isinstance(result.rev_users, list)
        assert len(result.rev_users) <= limit
        logger.info(f"✅ Listed contacts with limit={limit}: {len(result.rev_users)} found")

    def test_list_contacts_default(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing contacts with default parameters."""
        # Arrange - no specific parameters

        # Act
        result = write_client.rev_users.list()

        # Assert
        assert result is not None
        assert hasattr(result, "rev_users")
        assert isinstance(result.rev_users, list)
        logger.info(f"✅ Listed contacts with defaults: {len(result.rev_users)} found")
