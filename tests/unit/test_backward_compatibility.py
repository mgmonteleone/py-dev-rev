"""Backward compatibility tests for article/artifact changes.

This test suite ensures that recent changes to add unified methods
and parent_client references do not break existing functionality.
"""

from typing import Any
from unittest.mock import MagicMock

import pytest

from devrev.models.articles import (
    Article,
    ArticlesCreateRequest,
    ArticlesGetRequest,
    ArticlesListRequest,
    ArticlesUpdateRequest,
    ArticleStatus,
)
from devrev.services.articles import ArticlesService
from devrev.services.base import BaseService


def create_mock_response(data: dict[str, Any], status_code: int = 200) -> MagicMock:
    """Create a mock HTTP response.

    Args:
        data: JSON response data
        status_code: HTTP status code

    Returns:
        Mock response object
    """
    response = MagicMock()
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.json.return_value = data
    response.content = b"content"
    return response


@pytest.fixture
def mock_http_client() -> MagicMock:
    """Create a mock HTTP client for testing."""
    return MagicMock()


@pytest.fixture
def sample_article_data() -> dict[str, Any]:
    """Sample article data."""
    return {
        "id": "don:core:article:123",
        "display_id": "ART-123",
        "title": "Test Article",
        "description": "Test Description",
        "status": "published",
        "owned_by": [{"id": "don:identity:dvrv-us-1:devo/1:devu/1", "display_name": "Test User"}],
    }


class TestExistingArticleAPIsUnchanged:
    """Test that existing article API methods still work exactly as before."""

    def test_existing_articles_create_still_works(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Verify existing articles.create() method unchanged.

        This ensures that code using the old API still works:
        ```python
        service = ArticlesService(http_client)
        article = service.create(ArticlesCreateRequest(...))
        ```
        """
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        # Old API pattern - no parent_client
        service = ArticlesService(mock_http_client)
        request = ArticlesCreateRequest(
            title="Test Article",
            description="Test Description",
            status=ArticleStatus.PUBLISHED,
            owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
        )
        result = service.create(request)

        # Verify behavior unchanged
        assert isinstance(result, Article)
        assert result.id == "don:core:article:123"
        assert result.title == "Test Article"
        mock_http_client.post.assert_called_once()

    def test_existing_articles_get_still_works(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Verify existing articles.get() method unchanged.

        This ensures that code using the old API still works:
        ```python
        service = ArticlesService(http_client)
        article = service.get(ArticlesGetRequest(id="..."))
        ```
        """
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        # Old API pattern
        service = ArticlesService(mock_http_client)
        request = ArticlesGetRequest(id="don:core:article:123")
        result = service.get(request)

        # Verify behavior unchanged
        assert isinstance(result, Article)
        assert result.id == "don:core:article:123"
        mock_http_client.post.assert_called_once()

    def test_existing_articles_update_still_works(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Verify existing articles.update() method unchanged.

        This ensures that code using the old API still works:
        ```python
        service = ArticlesService(http_client)
        article = service.update(ArticlesUpdateRequest(...))
        ```
        """
        updated_data = {**sample_article_data, "title": "Updated Title"}
        mock_http_client.post.return_value = create_mock_response({"article": updated_data})

        # Old API pattern
        service = ArticlesService(mock_http_client)
        request = ArticlesUpdateRequest(
            id="don:core:article:123",
            title="Updated Title",
        )
        result = service.update(request)

        # Verify behavior unchanged
        assert isinstance(result, Article)
        assert result.title == "Updated Title"
        mock_http_client.post.assert_called_once()

    def test_existing_articles_list_still_works(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Verify existing articles.list() method unchanged.

        This ensures that code using the old API still works:
        ```python
        service = ArticlesService(http_client)
        articles = service.list()
        ```
        """
        mock_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data]}
        )

        # Old API pattern
        service = ArticlesService(mock_http_client)
        result = service.list()

        # Verify behavior unchanged
        assert len(result) == 1
        assert isinstance(result[0], Article)
        assert result[0].id == "don:core:article:123"
        mock_http_client.post.assert_called_once()


class TestBaseServiceBackwardCompatibility:
    """Test that BaseService changes maintain backward compatibility."""

    def test_base_service_without_parent_client(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Verify services work without parent_client parameter.

        The parent_client parameter was added as optional, so existing
        code that doesn't pass it should continue to work:
        ```python
        service = BaseService(http_client)  # No parent_client
        ```
        """
        # Old API pattern - only http_client
        service = BaseService(mock_http_client)

        # Verify service is initialized correctly
        assert service._http is mock_http_client
        assert service._parent_client is None  # Should default to None

    def test_base_service_with_parent_client(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Verify services work with parent_client parameter.

        New code can optionally pass parent_client:
        ```python
        service = BaseService(http_client, parent_client=client)
        ```
        """
        mock_parent_client = MagicMock()

        # New API pattern - with parent_client
        service = BaseService(mock_http_client, parent_client=mock_parent_client)

        # Verify both are set correctly
        assert service._http is mock_http_client
        assert service._parent_client is mock_parent_client


class TestArticleModelBackwardCompatibility:
    """Test that Article model changes maintain backward compatibility."""

    def test_article_model_resource_field_optional(self) -> None:
        """Verify Article.resource field is optional.

        Existing articles without resource field should still validate:
        ```python
        article = Article(id="...", title="...")  # No resource field
        ```
        """
        # Old-style article without resource field
        article_data = {
            "id": "don:core:article:123",
            "title": "Test Article",
        }

        # Should validate successfully
        article = Article.model_validate(article_data)
        assert article.id == "don:core:article:123"
        assert article.title == "Test Article"
        assert article.resource is None  # Should be None, not error

    def test_article_model_with_resource_field(self) -> None:
        """Verify Article.resource field works when provided.

        New articles with resource field should work:
        ```python
        article = Article(id="...", title="...", resource={"content_artifact": "..."})
        ```
        """
        # New-style article with resource field
        article_data = {
            "id": "don:core:article:123",
            "title": "Test Article",
            "resource": {"content_artifact": "artifact-456"},
        }

        # Should validate successfully
        article = Article.model_validate(article_data)
        assert article.id == "don:core:article:123"
        assert article.resource == {"content_artifact": "artifact-456"}


class TestExistingTestSuiteStillPasses:
    """Verify existing test suite still passes.

    This test runs a subset of existing article tests to ensure
    our changes don't break existing functionality.
    """

    def test_existing_tests_pass(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Run existing test patterns to verify no regressions.

        This test exercises the same patterns used in test_articles.py
        to ensure backward compatibility.
        """
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        # Test create
        service = ArticlesService(mock_http_client)
        create_req = ArticlesCreateRequest(
            title="Test",
            owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
        )
        article = service.create(create_req)
        assert article.id == "don:core:article:123"

        # Test get
        mock_http_client.reset_mock()
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})
        get_req = ArticlesGetRequest(id="don:core:article:123")
        article = service.get(get_req)
        assert article.id == "don:core:article:123"

        # Test list
        mock_http_client.reset_mock()
        mock_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data]}
        )
        articles = service.list()
        assert len(articles) == 1

        # Test update
        mock_http_client.reset_mock()
        updated_data = {**sample_article_data, "title": "Updated"}
        mock_http_client.post.return_value = create_mock_response({"article": updated_data})
        update_req = ArticlesUpdateRequest(id="don:core:article:123", title="Updated")
        article = service.update(update_req)
        assert article.title == "Updated"
