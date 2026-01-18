"""Integration tests for all .get() endpoints.

This test suite validates that all .get() endpoints work correctly
with the real DevRev API.
"""

import logging
import os

import pytest

from devrev import DevRevClient
from devrev.models.articles import ArticlesGetRequest
from devrev.models.conversations import ConversationsGetRequest
from devrev.models.groups import GroupsGetRequest
from devrev.models.parts import PartsGetRequest
from devrev.models.slas import SlasGetRequest
from devrev.models.tags import TagsGetRequest
from devrev.models.webhooks import WebhooksGetRequest

# Skip all integration tests if DEVREV_API_TOKEN is not set
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("DEVREV_API_TOKEN"),
        reason="DEVREV_API_TOKEN environment variable not set",
    ),
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def client() -> DevRevClient:
    """Create a DevRev client for integration tests."""
    return DevRevClient()


class TestGetEndpoints:
    """Tests for all .get() endpoints."""

    def test_works_get(self, client: DevRevClient) -> None:
        """Test works.get endpoint."""
        # Get a valid ID from list
        list_result = client.works.list(limit=1)
        if not list_result.works:
            pytest.skip("No works available for testing")

        work_id = list_result.works[0].id

        # Test get
        result = client.works.get(work_id)
        assert result.id == work_id
        assert hasattr(result, "title")
        logger.info(f"✅ works.get: {result.title}")

    def test_tags_get(self, client: DevRevClient) -> None:
        """Test tags.get endpoint."""
        # Get a valid ID from list
        list_result = client.tags.list()
        if not list_result or len(list_result) == 0:
            pytest.skip("No tags available for testing")

        tag_id = list_result[0].id

        # Test get
        request = TagsGetRequest(id=tag_id)
        result = client.tags.get(request)
        assert result.id == tag_id
        assert hasattr(result, "name")
        logger.info(f"✅ tags.get: {result.name}")

    def test_parts_get(self, client: DevRevClient) -> None:
        """Test parts.get endpoint."""
        # Get a valid ID from list
        list_result = client.parts.list(limit=1)
        if not list_result.parts:
            pytest.skip("No parts available for testing")

        part_id = list_result.parts[0].id

        # Test get
        request = PartsGetRequest(id=part_id)
        result = client.parts.get(request)
        assert result.id == part_id
        assert hasattr(result, "name")
        logger.info(f"✅ parts.get: {result.name}")

    def test_dev_users_get(self, client: DevRevClient) -> None:
        """Test dev-users.get endpoint."""
        # Get a valid ID from list
        list_result = client.dev_users.list(limit=1)
        if not list_result.dev_users:
            pytest.skip("No dev users available for testing")

        user_id = list_result.dev_users[0].id

        # Test get
        result = client.dev_users.get(user_id)
        assert result.id == user_id
        assert hasattr(result, "display_name")
        logger.info(f"✅ dev-users.get: {result.display_name}")

    def test_rev_users_get(self, client: DevRevClient) -> None:
        """Test rev-users.get endpoint."""
        # Get a valid ID from list
        list_result = client.rev_users.list(limit=1)
        if not list_result.rev_users:
            pytest.skip("No rev users available for testing")

        user_id = list_result.rev_users[0].id

        # Test get
        result = client.rev_users.get(user_id)
        assert result.id == user_id
        assert hasattr(result, "display_name")
        logger.info(f"✅ rev-users.get: {result.display_name}")

    def test_articles_get(self, client: DevRevClient) -> None:
        """Test articles.get endpoint."""
        # Get a valid ID from list
        list_result = client.articles.list()
        if not list_result or len(list_result) == 0:
            pytest.skip("No articles available for testing")

        article_id = list_result[0].id

        # Test get
        request = ArticlesGetRequest(id=article_id)
        result = client.articles.get(request)
        assert result.id == article_id
        assert hasattr(result, "title")
        logger.info(f"✅ articles.get: {result.title}")

    def test_conversations_get(self, client: DevRevClient) -> None:
        """Test conversations.get endpoint."""
        # Get a valid ID from list
        list_result = client.conversations.list()
        if not list_result or len(list_result) == 0:
            pytest.skip("No conversations available for testing")

        conversation_id = list_result[0].id

        # Test get
        request = ConversationsGetRequest(id=conversation_id)
        result = client.conversations.get(request)
        assert result.id == conversation_id
        logger.info(f"✅ conversations.get: {result.id}")

    def test_groups_get(self, client: DevRevClient) -> None:
        """Test groups.get endpoint."""
        # Get a valid ID from list
        list_result = client.groups.list()
        if not list_result or len(list_result) == 0:
            pytest.skip("No groups available for testing")

        group_id = list_result[0].id

        # Test get
        request = GroupsGetRequest(id=group_id)
        result = client.groups.get(request)
        assert result.id == group_id
        assert hasattr(result, "name")
        logger.info(f"✅ groups.get: {result.name}")

    def test_webhooks_get(self, client: DevRevClient) -> None:
        """Test webhooks.get endpoint."""
        # Get a valid ID from list
        list_result = client.webhooks.list()
        if not list_result or len(list_result) == 0:
            pytest.skip("No webhooks available for testing")

        webhook_id = list_result[0].id

        # Test get
        request = WebhooksGetRequest(id=webhook_id)
        result = client.webhooks.get(request)
        assert result.id == webhook_id
        assert hasattr(result, "url")
        logger.info(f"✅ webhooks.get: {result.url}")

    def test_slas_get(self, client: DevRevClient) -> None:
        """Test slas.get endpoint."""
        # Get a valid ID from list
        list_result = client.slas.list()
        if not list_result or len(list_result) == 0:
            pytest.skip("No SLAs available for testing")

        sla_id = list_result[0].id

        # Test get
        request = SlasGetRequest(id=sla_id)
        result = client.slas.get(request)
        assert result.id == sla_id
        assert hasattr(result, "name")
        logger.info(f"✅ slas.get: {result.name}")
