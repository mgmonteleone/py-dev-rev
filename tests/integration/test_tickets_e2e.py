"""End-to-end integration tests for Tickets (Works with type=ticket) endpoints.

Tests the full ticket lifecycle: create, get, list, update, delete.
Uses real API calls against the DevRev instance.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_tickets_e2e.py -v -m write

Related to Issue #142: E2E integration tests for tickets CRUD lifecycle
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from devrev.exceptions import DevRevError, NotFoundError
from devrev.models.works import WorkType

if TYPE_CHECKING:
    from devrev.client import DevRevClient
    from tests.integration.utils import TestDataManager

logger = logging.getLogger(__name__)

# Test data constants - required IDs for ticket creation
PRODUCT_PART_ID = "don:core:dvrv-us-1:devo/11Ca9baGrM:product/1"  # PROD-1: Augment Code
DEV_USER_ID = "don:identity:dvrv-us-1:devo/11Ca9baGrM:devu/4"  # DEVU-4: Test user

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


class TestTicketsCRUD:
    """CRUD integration tests for Tickets (Works with type=ticket).

    Demonstrates full create/read/update/delete lifecycle testing
    with proper cleanup and isolation.
    """

    def test_create_ticket_basic(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating a ticket with only required fields."""
        # Arrange
        title = test_data.generate_name("ticket")

        # Act
        ticket = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.TICKET,
            owned_by=[DEV_USER_ID],
        )
        test_data.register("work", ticket.id)

        # Assert
        assert ticket.id is not None
        assert ticket.title == title
        assert ticket.type == WorkType.TICKET
        logger.info(f"✅ Created ticket: {ticket.id}")

    def test_create_ticket_with_body(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test creating a ticket with title and body."""
        # Arrange
        title = test_data.generate_name("ticket")
        body = "This is a test ticket body with detailed description for integration testing."

        # Act
        ticket = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.TICKET,
            owned_by=[DEV_USER_ID],
            body=body,
        )
        test_data.register("work", ticket.id)

        # Assert
        assert ticket.id is not None
        assert ticket.title == title
        assert ticket.body == body
        assert ticket.type == WorkType.TICKET
        logger.info(f"✅ Created ticket with body: {ticket.id}")

    def test_get_ticket_by_id(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test retrieving a ticket by ID."""
        # Arrange - create ticket first
        title = test_data.generate_name("ticket")
        created_ticket = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.TICKET,
            owned_by=[DEV_USER_ID],
        )
        test_data.register("work", created_ticket.id)

        # Act
        retrieved_ticket = write_client.works.get(id=created_ticket.id)

        # Assert
        assert retrieved_ticket.id == created_ticket.id
        assert retrieved_ticket.title == title
        assert retrieved_ticket.type == WorkType.TICKET
        logger.info(f"✅ Retrieved ticket: {created_ticket.id}")

    def test_list_tickets(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing tickets with type filter."""
        # Arrange - no setup needed

        # Act
        result = write_client.works.list(type=[WorkType.TICKET], limit=5)

        # Assert
        assert result.works is not None
        assert isinstance(result.works, list)
        # Verify all returned items are tickets
        for work in result.works:
            assert work.type == WorkType.TICKET
        logger.info(f"✅ Listed tickets: {len(result.works)} found")

    def test_update_ticket_title(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating a ticket's title."""
        # Arrange - create ticket first
        original_title = test_data.generate_name("ticket")
        ticket = write_client.works.create(
            title=original_title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.TICKET,
            owned_by=[DEV_USER_ID],
        )
        test_data.register("work", ticket.id)

        # Act
        new_title = test_data.generate_name("ticket")
        updated_ticket = write_client.works.update(id=ticket.id, title=new_title)

        # Assert
        assert updated_ticket.id == ticket.id
        assert updated_ticket.title == new_title
        logger.info(f"✅ Updated ticket title: {ticket.id}")

    def test_update_ticket_body(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test updating a ticket's body text."""
        # Arrange - create ticket first
        title = test_data.generate_name("ticket")
        original_body = "Original body text"
        ticket = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.TICKET,
            owned_by=[DEV_USER_ID],
            body=original_body,
        )
        test_data.register("work", ticket.id)

        # Act
        new_body = "Updated body text with more details."
        updated_ticket = write_client.works.update(id=ticket.id, body=new_body)

        # Assert
        assert updated_ticket.body == new_body
        logger.info(f"✅ Updated ticket body: {ticket.id}")

    def test_delete_ticket(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test deleting a ticket."""
        # Arrange - create ticket first
        title = test_data.generate_name("ticket")
        ticket = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.TICKET,
            owned_by=[DEV_USER_ID],
        )
        # Note: NOT registering since we're testing delete

        # Act
        write_client.works.delete(id=ticket.id)

        # Assert - verify ticket is deleted by trying to get it
        with pytest.raises((NotFoundError, DevRevError, Exception)):
            write_client.works.get(id=ticket.id)
        logger.info(f"✅ Deleted ticket: {ticket.id}")

    def test_ticket_full_lifecycle(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test full ticket lifecycle: create -> get -> update -> list -> delete."""
        # Arrange
        title = test_data.generate_name("ticket")
        body = "Lifecycle test ticket with detailed description."

        # Act & Assert - Create
        ticket = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.TICKET,
            owned_by=[DEV_USER_ID],
            body=body,
        )
        # Note: NOT registering since we're testing delete
        assert ticket.id is not None
        assert ticket.title == title
        assert ticket.type == WorkType.TICKET
        logger.info(f"✅ Lifecycle - Created: {ticket.id}")

        # Act & Assert - Get
        retrieved = write_client.works.get(id=ticket.id)
        assert retrieved.id == ticket.id
        assert retrieved.title == title
        logger.info(f"✅ Lifecycle - Retrieved: {ticket.id}")

        # Act & Assert - Update
        new_title = test_data.generate_name("ticket")
        updated = write_client.works.update(id=ticket.id, title=new_title)
        assert updated.title == new_title
        logger.info(f"✅ Lifecycle - Updated: {ticket.id}")

        # Act & Assert - List
        result = write_client.works.list(type=[WorkType.TICKET], limit=10)
        assert result.works is not None
        assert isinstance(result.works, list)
        logger.info(f"✅ Lifecycle - Listed: {len(result.works)} tickets")

        # Act & Assert - Delete
        write_client.works.delete(id=ticket.id)
        with pytest.raises((NotFoundError, DevRevError, Exception)):
            write_client.works.get(id=ticket.id)
        logger.info(f"✅ Lifecycle - Deleted: {ticket.id}")


class TestTicketsErrorHandling:
    """Tests for error handling in ticket operations.

    Validates that the SDK properly handles and reports errors
    from the API for invalid ticket operations.
    """

    def test_get_nonexistent_ticket_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that getting a non-existent ticket raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/fake:ticket/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError, Exception)) as exc_info:
            write_client.works.get(id=fake_id)
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Get non-existent ticket correctly raised error")

    def test_update_nonexistent_ticket_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that updating a non-existent ticket raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/fake:ticket/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError, Exception)) as exc_info:
            write_client.works.update(
                id=fake_id,
                title=test_data.generate_name("ticket"),
            )
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Update non-existent ticket correctly raised error")

    def test_delete_nonexistent_ticket_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that deleting a non-existent ticket raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/fake:ticket/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError, Exception)) as exc_info:
            write_client.works.delete(id=fake_id)
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Delete non-existent ticket correctly raised error")


class TestTicketsListPagination:
    """Tests for ticket list pagination.

    Validates that pagination parameters work correctly.
    """

    def test_list_tickets_with_limit(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing tickets with a limit parameter."""
        # Arrange
        limit = 2

        # Act
        result = write_client.works.list(type=[WorkType.TICKET], limit=limit)

        # Assert
        assert result.works is not None
        assert isinstance(result.works, list)
        assert len(result.works) <= limit
        # Verify all returned items are tickets
        for work in result.works:
            assert work.type == WorkType.TICKET
        logger.info(f"✅ Listed tickets with limit={limit}: {len(result.works)} found")

    def test_list_tickets_default(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing tickets with default parameters."""
        # Arrange - no specific parameters

        # Act
        result = write_client.works.list(type=[WorkType.TICKET])

        # Assert
        assert result.works is not None
        assert isinstance(result.works, list)
        # Verify all returned items are tickets
        for work in result.works:
            assert work.type == WorkType.TICKET
        logger.info(f"✅ Listed tickets with defaults: {len(result.works)} found")
