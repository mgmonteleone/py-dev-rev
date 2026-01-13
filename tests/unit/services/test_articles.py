"""Unit tests for ArticlesService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.articles import (
    Article,
    ArticlesCreateRequest,
    ArticlesDeleteRequest,
    ArticlesGetRequest,
    ArticlesListRequest,
    ArticleStatus,
    ArticlesUpdateRequest,
)
from devrev.services.articles import ArticlesService

from .conftest import create_mock_response


class TestArticlesService:
    """Tests for ArticlesService."""

    def test_create_article(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test creating an article."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        service = ArticlesService(mock_http_client)
        request = ArticlesCreateRequest(
            title="Test Article",
            content="# Test Content",
            status=ArticleStatus.PUBLISHED,
        )
        result = service.create(request)

        assert isinstance(result, Article)
        assert result.id == "don:core:article:123"
        assert result.title == "Test Article"
        mock_http_client.post.assert_called_once()

    def test_get_article(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test getting an article by ID."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        service = ArticlesService(mock_http_client)
        request = ArticlesGetRequest(id="don:core:article:123")
        result = service.get(request)

        assert isinstance(result, Article)
        assert result.id == "don:core:article:123"
        mock_http_client.post.assert_called_once()

    def test_list_articles(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test listing articles."""
        mock_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data]}
        )

        service = ArticlesService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], Article)
        assert result[0].id == "don:core:article:123"
        mock_http_client.post.assert_called_once()

    def test_list_articles_with_request(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test listing articles with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data]}
        )

        service = ArticlesService(mock_http_client)
        request = ArticlesListRequest(limit=50, cursor="next-cursor")
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_article(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test updating an article."""
        updated_data = {**sample_article_data, "title": "Updated Title"}
        mock_http_client.post.return_value = create_mock_response({"article": updated_data})

        service = ArticlesService(mock_http_client)
        request = ArticlesUpdateRequest(
            id="don:core:article:123",
            title="Updated Title",
        )
        result = service.update(request)

        assert isinstance(result, Article)
        assert result.title == "Updated Title"
        mock_http_client.post.assert_called_once()

    def test_delete_article(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting an article."""
        mock_http_client.post.return_value = create_mock_response({})

        service = ArticlesService(mock_http_client)
        request = ArticlesDeleteRequest(id="don:core:article:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_articles_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing articles returns empty list."""
        mock_http_client.post.return_value = create_mock_response({"articles": []})

        service = ArticlesService(mock_http_client)
        result = service.list()

        assert len(result) == 0
        mock_http_client.post.assert_called_once()
