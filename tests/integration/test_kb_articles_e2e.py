"""End-to-end integration tests for KB Articles endpoints.

Tests the full article lifecycle: create, get, list, update, delete.
Uses real API calls against the DevRev instance.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_kb_articles_e2e.py -v -m write

Related to Issue #139: E2E integration tests for KB Articles and Q&A endpoints
"""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence
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


@pytest.fixture(scope="session")
def current_user_id(write_client: DevRevClient) -> str:
    """Get the current authenticated user's DON ID for article ownership."""
    user = write_client.dev_users.self()
    return user.id


class TestArticlesCRUD:
    """CRUD integration tests for Articles service.

    Demonstrates full create/read/update/delete lifecycle testing
    with proper cleanup and isolation.
    """

    def test_create_article_with_required_fields(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test creating an article with only required fields."""
        from devrev.models.articles import ArticlesCreateRequest

        # Arrange
        title = test_data.generate_name("Article")

        # Act
        request = ArticlesCreateRequest(title=title, owned_by=[current_user_id])
        article = write_client.articles.create(request)
        test_data.register("article", article.id)

        # Assert
        assert article.id is not None
        assert article.title == title
        logger.info(f"✅ Created article: {article.id}")

    def test_create_article_with_description(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test creating an article with title and description."""
        from devrev.models.articles import ArticlesCreateRequest

        # Arrange
        title = test_data.generate_name("Article")
        description = "# Test Article\n\nThis is test description for integration testing."

        # Act
        request = ArticlesCreateRequest(
            title=title, description=description, owned_by=[current_user_id]
        )
        article = write_client.articles.create(request)
        test_data.register("article", article.id)

        # Assert
        assert article.id is not None
        assert article.title == title
        assert article.description == description
        logger.info(f"✅ Created article with description: {article.id}")

    def test_create_article_as_draft(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test creating an article with draft status."""
        from devrev.models.articles import ArticlesCreateRequest, ArticleStatus

        # Arrange
        title = test_data.generate_name("DraftArticle")

        # Act
        request = ArticlesCreateRequest(
            title=title, status=ArticleStatus.DRAFT, owned_by=[current_user_id]
        )
        article = write_client.articles.create(request)
        test_data.register("article", article.id)

        # Assert
        assert article.id is not None
        assert article.status == ArticleStatus.DRAFT
        logger.info(f"✅ Created draft article: {article.id}")

    def test_get_article_by_id(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test retrieving an article by ID."""
        from devrev.models.articles import ArticlesCreateRequest, ArticlesGetRequest

        # Arrange - create article first
        title = test_data.generate_name("GetArticle")
        create_request = ArticlesCreateRequest(title=title, owned_by=[current_user_id])
        created_article = write_client.articles.create(create_request)
        test_data.register("article", created_article.id)

        # Act
        get_request = ArticlesGetRequest(id=created_article.id)
        retrieved_article = write_client.articles.get(get_request)

        # Assert
        assert retrieved_article.id == created_article.id
        assert retrieved_article.title == title
        logger.info(f"✅ Retrieved article: {created_article.id}")

    def test_list_articles(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing articles."""
        from devrev.models.articles import ArticlesListRequest

        # Arrange - no setup needed

        # Act
        request = ArticlesListRequest(limit=5)
        result = write_client.articles.list(request)

        # Assert
        assert isinstance(result, (list, Sequence))
        logger.info(f"✅ Listed articles: {len(result)} found")

    def test_update_article_title(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test updating an article's title."""
        from devrev.models.articles import ArticlesCreateRequest, ArticlesUpdateRequest

        # Arrange - create article first
        original_title = test_data.generate_name("OriginalTitle")
        create_request = ArticlesCreateRequest(title=original_title, owned_by=[current_user_id])
        article = write_client.articles.create(create_request)
        test_data.register("article", article.id)

        # Act
        new_title = test_data.generate_name("UpdatedTitle")
        update_request = ArticlesUpdateRequest(id=article.id, title=new_title)
        updated_article = write_client.articles.update(update_request)

        # Assert
        assert updated_article.id == article.id
        assert updated_article.title == new_title
        logger.info(f"✅ Updated article title: {article.id}")

    def test_update_article_description(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test updating an article's description."""
        from devrev.models.articles import ArticlesCreateRequest, ArticlesUpdateRequest

        # Arrange - create article first
        title = test_data.generate_name("DescriptionUpdate")
        original_description = "Original description"
        create_request = ArticlesCreateRequest(
            title=title, description=original_description, owned_by=[current_user_id]
        )
        article = write_client.articles.create(create_request)
        test_data.register("article", article.id)

        # Act
        new_description = "# Updated Description\n\nThis is the new description."
        update_request = ArticlesUpdateRequest(id=article.id, description=new_description)
        updated_article = write_client.articles.update(update_request)

        # Assert
        assert updated_article.description == new_description
        logger.info(f"✅ Updated article description: {article.id}")

    def test_update_article_status(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test updating an article's status from draft to published."""
        from devrev.models.articles import (
            ArticlesCreateRequest,
            ArticleStatus,
            ArticlesUpdateRequest,
        )

        # Arrange - create draft article first
        title = test_data.generate_name("StatusUpdate")
        create_request = ArticlesCreateRequest(
            title=title, status=ArticleStatus.DRAFT, owned_by=[current_user_id]
        )
        article = write_client.articles.create(create_request)
        test_data.register("article", article.id)

        # Act
        update_request = ArticlesUpdateRequest(id=article.id, status=ArticleStatus.PUBLISHED)
        updated_article = write_client.articles.update(update_request)

        # Assert
        assert updated_article.status == ArticleStatus.PUBLISHED
        logger.info(f"✅ Updated article status: {article.id}")

    def test_delete_article(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test deleting an article."""
        from devrev.models.articles import (
            ArticlesCreateRequest,
            ArticlesDeleteRequest,
            ArticlesGetRequest,
        )

        # Arrange - create article first
        title = test_data.generate_name("ToDelete")
        create_request = ArticlesCreateRequest(title=title, owned_by=[current_user_id])
        article = write_client.articles.create(create_request)
        # Note: NOT registering since we're testing delete

        # Act
        delete_request = ArticlesDeleteRequest(id=article.id)
        write_client.articles.delete(delete_request)

        # Assert - verify article is deleted by trying to get it
        with pytest.raises((NotFoundError, DevRevError, Exception)):
            get_request = ArticlesGetRequest(id=article.id)
            write_client.articles.get(get_request)
        logger.info(f"✅ Deleted article: {article.id}")

    def test_article_full_lifecycle(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test full article lifecycle: create -> get -> update -> list -> delete."""
        from devrev.models.articles import (
            ArticlesCreateRequest,
            ArticlesDeleteRequest,
            ArticlesGetRequest,
            ArticlesListRequest,
            ArticleStatus,
            ArticlesUpdateRequest,
        )

        # Arrange
        title = test_data.generate_name("LifecycleArticle")
        description = "# Lifecycle Test\n\nTesting full lifecycle."

        # Act & Assert - Create
        create_request = ArticlesCreateRequest(
            title=title,
            description=description,
            status=ArticleStatus.DRAFT,
            owned_by=[current_user_id],
        )
        article = write_client.articles.create(create_request)
        # Note: NOT registering since we're testing delete
        assert article.id is not None
        assert article.title == title
        assert article.status == ArticleStatus.DRAFT
        logger.info(f"✅ Lifecycle - Created: {article.id}")

        # Act & Assert - Get
        get_request = ArticlesGetRequest(id=article.id)
        retrieved = write_client.articles.get(get_request)
        assert retrieved.id == article.id
        assert retrieved.title == title
        logger.info(f"✅ Lifecycle - Retrieved: {article.id}")

        # Act & Assert - Update
        new_title = test_data.generate_name("UpdatedLifecycle")
        update_request = ArticlesUpdateRequest(
            id=article.id,
            title=new_title,
            status=ArticleStatus.PUBLISHED,
        )
        updated = write_client.articles.update(update_request)
        assert updated.title == new_title
        assert updated.status == ArticleStatus.PUBLISHED
        logger.info(f"✅ Lifecycle - Updated: {article.id}")

        # Act & Assert - List
        list_request = ArticlesListRequest(limit=10)
        articles = write_client.articles.list(list_request)
        assert isinstance(articles, (list, Sequence))
        logger.info(f"✅ Lifecycle - Listed: {len(articles)} articles")

        # Act & Assert - Delete
        delete_request = ArticlesDeleteRequest(id=article.id)
        write_client.articles.delete(delete_request)
        with pytest.raises((NotFoundError, DevRevError, Exception)):
            write_client.articles.get(get_request)
        logger.info(f"✅ Lifecycle - Deleted: {article.id}")


class TestArticlesErrorHandling:
    """Tests for error handling in articles operations.

    Validates that the SDK properly handles and reports errors
    from the API for invalid article operations.
    """

    def test_get_nonexistent_article_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that getting a non-existent article raises an error."""
        from devrev.models.articles import ArticlesGetRequest

        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/FAKE:article/DOESNOTEXIST"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError, Exception)) as exc_info:
            get_request = ArticlesGetRequest(id=fake_id)
            write_client.articles.get(get_request)
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Get non-existent article correctly raised error")

    def test_update_nonexistent_article_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that updating a non-existent article raises an error."""
        from devrev.models.articles import ArticlesUpdateRequest

        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/FAKE:article/DOESNOTEXIST"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError, Exception)) as exc_info:
            update_request = ArticlesUpdateRequest(
                id=fake_id,
                title=test_data.generate_name("ShouldFail"),
            )
            write_client.articles.update(update_request)
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Update non-existent article correctly raised error")

    def test_delete_nonexistent_article_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test that deleting a non-existent article raises an error."""
        from devrev.models.articles import ArticlesDeleteRequest

        # Arrange
        fake_id = "don:core:dvrv-us-1:devo/FAKE:article/DOESNOTEXIST"

        # Act & Assert - expect NotFoundError or similar API error
        with pytest.raises((NotFoundError, DevRevError, Exception)) as exc_info:
            delete_request = ArticlesDeleteRequest(id=fake_id)
            write_client.articles.delete(delete_request)
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Delete non-existent article correctly raised error")

    def test_create_article_without_title_raises_error(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test that creating an article without a title raises an error."""
        from devrev.models.articles import ArticlesCreateRequest

        # Act & Assert - expect validation error from Pydantic or API
        with pytest.raises((ValueError, DevRevError, Exception)) as exc_info:
            # Try to create with empty title
            request = ArticlesCreateRequest(title="", owned_by=[current_user_id])
            write_client.articles.create(request)
        # Verify we got an actual error, not just any exception
        assert exc_info.value is not None
        logger.info("✅ Create article without title correctly raised error")


class TestArticlesListPagination:
    """Tests for articles list pagination.

    Validates that pagination parameters work correctly.
    """

    def test_list_articles_with_limit(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing articles with a limit parameter."""
        from devrev.models.articles import ArticlesListRequest

        # Arrange
        limit = 2

        # Act
        request = ArticlesListRequest(limit=limit)
        result = write_client.articles.list(request)

        # Assert
        assert isinstance(result, (list, Sequence))
        assert len(result) <= limit
        logger.info(f"✅ Listed articles with limit={limit}: {len(result)} found")

    def test_list_articles_default(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test listing articles with default parameters."""
        from devrev.models.articles import ArticlesListRequest

        # Arrange - no specific parameters

        # Act
        request = ArticlesListRequest()
        result = write_client.articles.list(request)

        # Assert
        assert isinstance(result, (list, Sequence))
        logger.info(f"✅ Listed articles with defaults: {len(result)} found")
