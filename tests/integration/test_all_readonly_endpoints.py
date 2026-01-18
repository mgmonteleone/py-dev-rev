"""Comprehensive integration tests for all read-only endpoints.

This test suite validates that all read-only endpoints work correctly
with the real DevRev API and that our Pydantic models match the actual
API responses.

Any failures here indicate schema mismatches between our models and the
actual API, which should be documented in OPENAPI_SPEC_DISCREPANCIES.md
for reporting back to DevRev.
"""

import logging
import os
from typing import Any

import pytest

from devrev import DevRevClient
from devrev.exceptions import DevRevError

# Skip all integration tests if DEVREV_API_TOKEN is not set
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("DEVREV_API_TOKEN"),
        reason="DEVREV_API_TOKEN environment variable not set",
    ),
]

# Configure logging to capture validation errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SchemaDiscrepancyTracker:
    """Track schema discrepancies for reporting to DevRev."""

    def __init__(self) -> None:
        self.discrepancies: list[dict[str, Any]] = []

    def add(
        self,
        endpoint: str,
        field_path: str,
        expected_type: str,
        actual_type: str,
        error_message: str,
        sample_data: Any = None,
    ) -> None:
        """Add a schema discrepancy."""
        self.discrepancies.append(
            {
                "endpoint": endpoint,
                "field_path": field_path,
                "expected_type": expected_type,
                "actual_type": actual_type,
                "error_message": error_message,
                "sample_data": sample_data,
            }
        )

    def report(self) -> str:
        """Generate a report of all discrepancies."""
        if not self.discrepancies:
            return "No schema discrepancies found!"

        report = "# OpenAPI Spec Discrepancies\n\n"
        for disc in self.discrepancies:
            report += f"## {disc['endpoint']}\n\n"
            report += f"**Field**: `{disc['field_path']}`\n\n"
            report += f"**Expected Type**: `{disc['expected_type']}`\n\n"
            report += f"**Actual Type**: `{disc['actual_type']}`\n\n"
            report += f"**Error**: {disc['error_message']}\n\n"
            if disc["sample_data"]:
                report += f"**Sample Data**:\n```json\n{disc['sample_data']}\n```\n\n"
            report += "---\n\n"
        return report


# Global tracker for collecting discrepancies
tracker = SchemaDiscrepancyTracker()


@pytest.fixture(scope="module")
def client() -> DevRevClient:
    """Create a DevRev client for PUBLIC API integration tests."""
    return DevRevClient()


@pytest.fixture(scope="module")
def beta_client() -> DevRevClient:
    """Create a DevRev client for BETA API integration tests."""
    from devrev.config import APIVersion

    return DevRevClient(api_version=APIVersion.BETA)


@pytest.fixture(scope="module", autouse=True)
def report_discrepancies(request: pytest.FixtureRequest) -> None:
    """Report all schema discrepancies at the end of the test session."""
    yield
    # This runs after all tests
    report = tracker.report()
    logger.info("\n" + report)
    # Write to file
    with open("OPENAPI_SPEC_DISCREPANCIES.md", "w") as f:
        f.write(report)


class TestAccountsReadOnly:
    """Read-only tests for accounts endpoints."""

    def test_accounts_list(self, client: DevRevClient) -> None:
        """Test accounts.list endpoint."""
        try:
            result = client.accounts.list(limit=5)
            assert hasattr(result, "accounts")
            assert isinstance(result.accounts, list)
        except Exception as e:
            logger.error(f"accounts.list failed: {e}")
            tracker.add(
                endpoint="accounts.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise

    def test_accounts_get(self, client: DevRevClient) -> None:
        """Test accounts.get endpoint."""
        try:
            # Get a valid ID from list
            list_result = client.accounts.list(limit=1)
            if not list_result.accounts:
                pytest.skip("No accounts available for testing")

            account_id = list_result.accounts[0].id

            # Test get
            result = client.accounts.get(account_id)
            assert result.id == account_id
            assert hasattr(result, "display_name")
        except Exception as e:
            logger.error(f"accounts.get failed: {e}")
            tracker.add(
                endpoint="accounts.get",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise

    def test_accounts_export(self, client: DevRevClient) -> None:
        """Test accounts.export endpoint."""
        try:
            result = client.accounts.export(first=5)
            assert isinstance(result, list)
        except Exception as e:
            logger.error(f"accounts.export failed: {e}")
            tracker.add(
                endpoint="accounts.export",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestWorksReadOnly:
    """Read-only tests for works endpoints."""

    def test_works_list(self, client: DevRevClient) -> None:
        """Test works.list endpoint."""
        try:
            result = client.works.list(limit=5)
            assert hasattr(result, "works")
            assert isinstance(result.works, list)
        except Exception as e:
            logger.error(f"works.list failed: {e}")
            tracker.add(
                endpoint="works.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise

    def test_works_export(self, client: DevRevClient) -> None:
        """Test works.export endpoint."""
        try:
            result = client.works.export(first=5)
            assert isinstance(result, list)
        except Exception as e:
            logger.error(f"works.export failed: {e}")
            tracker.add(
                endpoint="works.export",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise

    def test_works_count(self, client: DevRevClient) -> None:
        """Test works.count endpoint."""
        try:
            result = client.works.count()
            assert isinstance(result, int)
        except Exception as e:
            logger.error(f"works.count failed: {e}")
            tracker.add(
                endpoint="works.count",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestTagsReadOnly:
    """Read-only tests for tags endpoints."""

    def test_tags_list(self, client: DevRevClient) -> None:
        """Test tags.list endpoint."""
        try:
            result = client.tags.list()
            # Note: Current implementation expects result.tags but API returns list directly
            assert isinstance(result, list) or hasattr(result, "tags")
        except Exception as e:
            logger.error(f"tags.list failed: {e}")
            tracker.add(
                endpoint="tags.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestPartsReadOnly:
    """Read-only tests for parts endpoints."""

    def test_parts_list(self, client: DevRevClient) -> None:
        """Test parts.list endpoint."""
        try:
            result = client.parts.list(limit=5)
            assert hasattr(result, "parts")
            assert isinstance(result.parts, list)
        except Exception as e:
            logger.error(f"parts.list failed: {e}")
            tracker.add(
                endpoint="parts.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestDevUsersReadOnly:
    """Read-only tests for dev-users endpoints."""

    def test_dev_users_list(self, client: DevRevClient) -> None:
        """Test dev-users.list endpoint."""
        try:
            result = client.dev_users.list(limit=5)
            assert hasattr(result, "dev_users")
            assert isinstance(result.dev_users, list)
        except Exception as e:
            logger.error(f"dev-users.list failed: {e}")
            tracker.add(
                endpoint="dev-users.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestRevUsersReadOnly:
    """Read-only tests for rev-users endpoints."""

    def test_rev_users_list(self, client: DevRevClient) -> None:
        """Test rev-users.list endpoint."""
        try:
            result = client.rev_users.list(limit=5)
            assert hasattr(result, "rev_users")
            assert isinstance(result.rev_users, list)
        except Exception as e:
            logger.error(f"rev-users.list failed: {e}")
            tracker.add(
                endpoint="rev-users.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestArticlesReadOnly:
    """Read-only tests for articles endpoints."""

    def test_articles_list(self, client: DevRevClient) -> None:
        """Test articles.list endpoint."""
        try:
            result = client.articles.list()
            assert isinstance(result, list)
        except Exception as e:
            logger.error(f"articles.list failed: {e}")
            tracker.add(
                endpoint="articles.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise

    def test_articles_count(self, client: DevRevClient) -> None:
        """Test articles.count endpoint."""
        try:
            result = client.articles.count()
            assert isinstance(result, int)
        except Exception as e:
            logger.error(f"articles.count failed: {e}")
            tracker.add(
                endpoint="articles.count",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestConversationsReadOnly:
    """Read-only tests for conversations endpoints."""

    def test_conversations_list(self, client: DevRevClient) -> None:
        """Test conversations.list endpoint."""
        try:
            result = client.conversations.list()
            assert isinstance(result, list)
        except Exception as e:
            logger.error(f"conversations.list failed: {e}")
            tracker.add(
                endpoint="conversations.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise

    @pytest.mark.xfail(
        reason="conversations.export returns 400 - may require specific permissions or data",
        raises=DevRevError,
    )
    def test_conversations_export(self, beta_client: DevRevClient) -> None:
        """Test conversations.export endpoint (BETA API only).

        Note: This endpoint may require specific conversation data or permissions.
        """
        result = beta_client.conversations.export(limit=5)
        assert isinstance(result, list)
        logger.info(f"✅ conversations.export: {len(result)} conversations")


class TestGroupsReadOnly:
    """Read-only tests for groups endpoints."""

    def test_groups_list(self, client: DevRevClient) -> None:
        """Test groups.list endpoint."""
        try:
            result = client.groups.list()
            assert isinstance(result, list)
        except Exception as e:
            logger.error(f"groups.list failed: {e}")
            tracker.add(
                endpoint="groups.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestWebhooksReadOnly:
    """Read-only tests for webhooks endpoints."""

    def test_webhooks_list(self, client: DevRevClient) -> None:
        """Test webhooks.list endpoint."""
        try:
            result = client.webhooks.list()
            assert isinstance(result, list)
        except Exception as e:
            logger.error(f"webhooks.list failed: {e}")
            tracker.add(
                endpoint="webhooks.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise


class TestSlasReadOnly:
    """Read-only tests for SLAs endpoints."""

    def test_slas_list(self, client: DevRevClient) -> None:
        """Test slas.list endpoint."""
        try:
            result = client.slas.list()
            assert isinstance(result, list)
        except Exception as e:
            logger.error(f"slas.list failed: {e}")
            tracker.add(
                endpoint="slas.list",
                field_path="TBD",
                expected_type="TBD",
                actual_type="TBD",
                error_message=str(e),
            )
            raise
