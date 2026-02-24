"""End-to-end integration tests for Issues (Works with type=issue) endpoints.

Tests the full issue lifecycle: create, get, list, update, delete.
Uses real API calls against the DevRev instance.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_issues_e2e.py -v -m write

Related to Issue #142: E2E integration tests for Issues CRUD lifecycle
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

import pytest

from devrev.exceptions import DevRevError, NotFoundError
from devrev.models.works import IssuePriority, WorkType

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

# Required IDs for issue creation
PRODUCT_PART_ID = "don:core:dvrv-us-1:devo/11Ca9baGrM:product/1"


@pytest.fixture(scope="session")
def current_user_id(write_client: DevRevClient) -> str:
    """Get the current authenticated user's DON ID for issue ownership."""
    user = write_client.dev_users.self()
    return user.id


class TestIssuesCRUD:
    """CRUD integration tests for Issues (Works with type=issue).

    Demonstrates full create/read/update/delete lifecycle testing
    with proper cleanup and isolation.
    """

    def test_create_issue_basic(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test creating an issue with only required fields."""
        # Arrange
        title = test_data.generate_name("issue")

        # Act
        work = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.ISSUE,
            owned_by=[current_user_id],
        )
        test_data.register("work", work.id)

        # Assert
        assert work.id is not None
        assert work.title == title
        assert work.type == WorkType.ISSUE
        logger.info(f"✅ Created issue: {work.id}")

    def test_create_issue_with_body(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test creating an issue with body/description."""
        # Arrange
        title = test_data.generate_name("issue")
        body = "# Test Issue\n\nThis is a test issue for integration testing."

        # Act
        work = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.ISSUE,
            owned_by=[current_user_id],
            body=body,
        )
        test_data.register("work", work.id)

        # Assert
        assert work.id is not None
        assert work.title == title
        assert work.body == body
        assert work.type == WorkType.ISSUE
        logger.info(f"✅ Created issue with body: {work.id}")

    def test_get_issue_by_id(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test retrieving an issue by ID."""
        # Arrange - create issue first
        title = test_data.generate_name("issue")
        created_work = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.ISSUE,
            owned_by=[current_user_id],
        )
        test_data.register("work", created_work.id)

        # Act
        retrieved_work = write_client.works.get(id=created_work.id)

        # Assert
        assert retrieved_work.id == created_work.id
        assert retrieved_work.title == title
        assert retrieved_work.type == WorkType.ISSUE
        logger.info(f"✅ Retrieved issue: {created_work.id}")

    def test_list_issues(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing issues with type filter."""
        # Arrange - no setup needed

        # Act
        result = write_client.works.list(type=[WorkType.ISSUE], limit=5)

        # Assert
        assert result.works is not None
        assert isinstance(result.works, list)
        # Verify all returned items are issues
        for work in result.works:
            assert work.type == WorkType.ISSUE
        logger.info(f"✅ Listed issues: {len(result.works)} found")

    def test_update_issue_title(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test updating an issue's title."""
        # Arrange - create issue first
        original_title = test_data.generate_name("issue")
        work = write_client.works.create(
            title=original_title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.ISSUE,
            owned_by=[current_user_id],
        )
        test_data.register("work", work.id)

        # Act
        new_title = test_data.generate_name("issue")
        updated_work = write_client.works.update(id=work.id, title=new_title)

        # Assert
        assert updated_work.id == work.id
        assert updated_work.title == new_title
        logger.info(f"✅ Updated issue title: {work.id}")

    def test_update_issue_body(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test updating an issue's body text."""
        # Arrange - create issue first
        title = test_data.generate_name("issue")
        original_body = "Original body text"
        work = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.ISSUE,
            owned_by=[current_user_id],
            body=original_body,
        )
        test_data.register("work", work.id)

        # Act
        new_body = "# Updated Body\n\nThis is the new body text."
        updated_work = write_client.works.update(id=work.id, body=new_body)

        # Assert
        assert updated_work.body == new_body
        logger.info(f"✅ Updated issue body: {work.id}")

    def test_delete_issue(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test deleting an issue."""
        # Arrange - create issue first
        title = test_data.generate_name("issue")
        work = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.ISSUE,
            owned_by=[current_user_id],
        )
        # Note: NOT registering since we're testing delete

        # Act
        write_client.works.delete(id=work.id)

        # Assert - verify issue is deleted by trying to get it
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.works.get(id=work.id)
        logger.info(f"✅ Deleted issue: {work.id}")

    def test_issue_full_lifecycle(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test full issue lifecycle: create -> get -> update -> list -> delete."""
        # Arrange
        title = test_data.generate_name("issue")
        body = "# Lifecycle Test\n\nTesting full lifecycle."

        # Act & Assert - Create
        work = write_client.works.create(
            title=title,
            applies_to_part=PRODUCT_PART_ID,
            type=WorkType.ISSUE,
            owned_by=[current_user_id],
            body=body,
            priority=IssuePriority.P2,
        )
        # Note: NOT registering since we're testing delete
        assert work.id is not None
        assert work.title == title
        assert work.type == WorkType.ISSUE
        logger.info(f"✅ Lifecycle - Created: {work.id}")

        # Act & Assert - Get
        retrieved = write_client.works.get(id=work.id)
        assert retrieved.id == work.id
        assert retrieved.title == title
        logger.info(f"✅ Lifecycle - Retrieved: {work.id}")

        # Act & Assert - Update
        new_title = test_data.generate_name("issue")
        updated = write_client.works.update(id=work.id, title=new_title)
        assert updated.title == new_title
        logger.info(f"✅ Lifecycle - Updated: {work.id}")

        # Act & Assert - List
        result = write_client.works.list(type=[WorkType.ISSUE], limit=10)
        assert result.works is not None
        assert isinstance(result.works, list)
        logger.info(f"✅ Lifecycle - Listed: {len(result.works)} issues")

        # Act & Assert - Delete
        write_client.works.delete(id=work.id)
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.works.get(id=work.id)
        logger.info(f"✅ Lifecycle - Deleted: {work.id}")


class TestIssuesErrorHandling:
    """Tests for error handling in issues operations.

    Validates that the SDK properly handles and reports errors
    from the API for invalid issue operations.
    """

    def test_get_nonexistent_issue_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that getting a non-existent issue raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/fake:issue/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.works.get(id=fake_id)
        logger.info("✅ Get non-existent issue correctly raised error")

    def test_update_nonexistent_issue_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that updating a non-existent issue raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/fake:issue/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.works.update(
                id=fake_id,
                title=test_data.generate_name("issue"),
            )
        logger.info("✅ Update non-existent issue correctly raised error")

    def test_delete_nonexistent_issue_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that deleting a non-existent issue raises an error."""
        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/fake:issue/nonexistent99"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.works.delete(id=fake_id)
        logger.info("✅ Delete non-existent issue correctly raised error")


class TestIssuesListPagination:
    """Tests for issues list pagination.

    Validates that pagination parameters work correctly.
    """

    def test_list_issues_with_limit(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing issues with a limit parameter."""
        # Arrange
        limit = 2

        # Act
        result = write_client.works.list(type=[WorkType.ISSUE], limit=limit)

        # Assert
        assert result.works is not None
        assert isinstance(result.works, list)
        assert len(result.works) <= limit
        logger.info(f"✅ Listed issues with limit={limit}: {len(result.works)} found")

    def test_list_issues_default(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing issues with default parameters."""
        # Arrange - no specific parameters

        # Act
        result = write_client.works.list(type=[WorkType.ISSUE])

        # Assert
        assert result.works is not None
        assert isinstance(result.works, list)
        logger.info(f"✅ Listed issues with defaults: {len(result.works)} found")
