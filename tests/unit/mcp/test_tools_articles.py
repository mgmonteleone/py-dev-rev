"""Unit tests for DevRev MCP Server - Articles Tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import NotFoundError, ValidationError
from devrev_mcp.tools.articles import (
    devrev_articles_count,
    devrev_articles_create,
    devrev_articles_delete,
    devrev_articles_get,
    devrev_articles_list,
    devrev_articles_update,
)


def _make_mock_article(
    id: str = "article-1",
    title: str = "Test Article",
    content: str = "Test content",
    status: str = "published",
) -> MagicMock:
    """Create a mock article object."""
    mock = MagicMock()
    mock.model_dump.return_value = {
        "id": id,
        "display_id": f"ART-{id}",
        "title": title,
        "content": content,
        "status": status,
        "authored_by": [],
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
    }
    return mock


class TestArticlesListTool:
    """Tests for devrev_articles_list tool."""

    @pytest.mark.asyncio
    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing articles when none exist."""
        mock_client.articles.list.return_value = []

        result = await devrev_articles_list(mock_ctx)

        assert result["count"] == 0
        assert result["articles"] == []
        mock_client.articles.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_with_results(self, mock_ctx, mock_client):
        """Test listing articles with results."""
        mock_articles = [
            _make_mock_article(id="article-1", title="Article 1"),
            _make_mock_article(id="article-2", title="Article 2"),
        ]
        mock_client.articles.list.return_value = mock_articles

        result = await devrev_articles_list(mock_ctx, limit=10)

        assert result["count"] == 2
        assert len(result["articles"]) == 2
        assert result["articles"][0]["id"] == "article-1"
        assert result["articles"][1]["id"] == "article-2"

    @pytest.mark.asyncio
    async def test_list_error(self, mock_ctx, mock_client):
        """Test listing articles with API error."""
        mock_client.articles.list.side_effect = ValidationError("Invalid request")

        with pytest.raises(RuntimeError, match="Invalid request"):
            await devrev_articles_list(mock_ctx)


class TestArticlesGetTool:
    """Tests for devrev_articles_get tool."""

    @pytest.mark.asyncio
    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting an article successfully."""
        mock_article = _make_mock_article(id="article-1", title="Test Article")
        mock_client.articles.get.return_value = mock_article

        result = await devrev_articles_get(mock_ctx, id="article-1")

        assert result["id"] == "article-1"
        assert result["title"] == "Test Article"
        mock_client.articles.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent article."""
        mock_client.articles.get.side_effect = NotFoundError("Article not found")

        with pytest.raises(RuntimeError, match="Article not found"):
            await devrev_articles_get(mock_ctx, id="nonexistent")


class TestArticlesCreateTool:
    """Tests for devrev_articles_create tool."""

    @pytest.mark.asyncio
    async def test_create_minimal(self, mock_ctx, mock_client):
        """Test creating an article with minimal fields."""
        mock_article = _make_mock_article(title="New Article", content="New content")
        mock_client.articles.create.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="New Article",
            content="New content",
        )

        assert result["title"] == "New Article"
        assert result["content"] == "New content"
        mock_client.articles.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_with_status(self, mock_ctx, mock_client):
        """Test creating an article with status."""
        mock_article = _make_mock_article(
            title="Draft Article",
            content="Draft content",
            status="draft",
        )
        mock_client.articles.create.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="Draft Article",
            content="Draft content",
            status="draft",
        )

        assert result["status"] == "draft"

    @pytest.mark.asyncio
    async def test_create_validation_error(self, mock_ctx, mock_client):
        """Test creating an article with validation error."""
        mock_client.articles.create.side_effect = ValidationError("Title required")

        with pytest.raises(RuntimeError, match="Title required"):
            await devrev_articles_create(mock_ctx, title="", content="Content")


class TestArticlesUpdateTool:
    """Tests for devrev_articles_update tool."""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_ctx, mock_client):
        """Test updating an article successfully."""
        mock_article = _make_mock_article(
            id="article-1",
            title="Updated Title",
            status="published",
        )
        mock_client.articles.update.return_value = mock_article

        result = await devrev_articles_update(
            mock_ctx,
            id="article-1",
            title="Updated Title",
            status="published",
        )

        assert result["title"] == "Updated Title"
        assert result["status"] == "published"

    @pytest.mark.asyncio
    async def test_update_error(self, mock_ctx, mock_client):
        """Test updating an article with error."""
        mock_client.articles.update.side_effect = NotFoundError("Article not found")

        with pytest.raises(RuntimeError, match="Article not found"):
            await devrev_articles_update(mock_ctx, id="nonexistent", title="New")


class TestArticlesDeleteTool:
    """Tests for devrev_articles_delete tool."""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_ctx, mock_client):
        """Test deleting an article successfully."""
        mock_client.articles.delete.return_value = None

        result = await devrev_articles_delete(mock_ctx, id="article-1")

        assert result["success"] is True
        assert result["id"] == "article-1"
        mock_client.articles.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_not_found(self, mock_ctx, mock_client):
        """Test deleting a non-existent article."""
        mock_client.articles.delete.side_effect = NotFoundError("Article not found")

        with pytest.raises(RuntimeError, match="Article not found"):
            await devrev_articles_delete(mock_ctx, id="nonexistent")


class TestArticlesCountTool:
    """Tests for devrev_articles_count tool."""

    @pytest.mark.asyncio
    async def test_count_success(self, mock_ctx, mock_client):
        """Test counting articles successfully."""
        mock_client.articles.count.return_value = 42

        result = await devrev_articles_count(mock_ctx)

        assert result["count"] == 42
        mock_client.articles.count.assert_called_once_with(status=None)

    @pytest.mark.asyncio
    async def test_count_with_status_filter(self, mock_ctx, mock_client):
        """Test counting articles with status filter."""
        mock_client.articles.count.return_value = 15

        result = await devrev_articles_count(mock_ctx, status=["published"])

        assert result["count"] == 15
        mock_client.articles.count.assert_called_once_with(status=["published"])

    @pytest.mark.asyncio
    async def test_count_error(self, mock_ctx, mock_client):
        """Test counting articles with error."""
        mock_client.articles.count.side_effect = ValidationError("Invalid status")

        with pytest.raises(RuntimeError, match="Invalid status"):
            await devrev_articles_count(mock_ctx, status=["invalid"])
