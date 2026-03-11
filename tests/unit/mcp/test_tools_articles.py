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
    description: str = "Test content",
    status: str = "published",
) -> MagicMock:
    """Create a mock article object."""
    mock = MagicMock()
    mock.model_dump.return_value = {
        "id": id,
        "display_id": f"ART-{id}",
        "title": title,
        "description": description,
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
        response = MagicMock()
        response.articles = []
        response.next_cursor = None
        mock_client.articles.list.return_value = response

        result = await devrev_articles_list(mock_ctx)

        assert result["count"] == 0
        assert result["articles"] == []
        assert "next_cursor" not in result
        mock_client.articles.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_with_results(self, mock_ctx, mock_client):
        """Test listing articles with results."""
        mock_articles = [
            _make_mock_article(id="article-1", title="Article 1"),
            _make_mock_article(id="article-2", title="Article 2"),
        ]
        response = MagicMock()
        response.articles = mock_articles
        response.next_cursor = None
        mock_client.articles.list.return_value = response

        result = await devrev_articles_list(mock_ctx, limit=10)

        assert result["count"] == 2
        assert len(result["articles"]) == 2
        assert result["articles"][0]["id"] == "article-1"
        assert result["articles"][1]["id"] == "article-2"

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing articles returns pagination cursor."""
        response = MagicMock()
        response.articles = [_make_mock_article(id="article-1", title="Article 1")]
        response.next_cursor = "cursor-123"
        mock_client.articles.list.return_value = response

        result = await devrev_articles_list(mock_ctx, cursor="prev-cursor", limit=10)

        assert result["count"] == 1
        assert result["next_cursor"] == "cursor-123"
        mock_client.articles.list.assert_called_once()
        call_args = mock_client.articles.list.call_args
        request = call_args[0][0]
        assert request.cursor == "prev-cursor"
        assert request.limit == 10

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
        mock_article = _make_mock_article(title="New Article", description="New content")
        mock_client.articles.create_with_content.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="New Article",
            content="New content",
            owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
        )

        assert result["title"] == "New Article"
        assert result["description"] == "New content"
        mock_client.articles.create_with_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_with_status(self, mock_ctx, mock_client):
        """Test creating an article with status."""
        mock_article = _make_mock_article(
            title="Draft Article",
            description="Draft content",
            status="draft",
        )
        mock_client.articles.create_with_content.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="Draft Article",
            content="Draft content",
            owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
            status="draft",
        )

        assert result["status"] == "draft"

    @pytest.mark.asyncio
    async def test_create_validation_error(self, mock_ctx, mock_client):
        """Test creating an article with validation error."""
        mock_client.articles.create_with_content.side_effect = ValidationError("Title required")

        with pytest.raises(RuntimeError, match="Title required"):
            await devrev_articles_create(
                mock_ctx,
                title="",
                content="Content",
                owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
            )

    @pytest.mark.asyncio
    async def test_create_with_applies_to_parts(self, mock_ctx, mock_client):
        """Test creating an article with applies_to_parts."""
        mock_article = _make_mock_article(
            title="Article with Parts",
            description="Content with parts",
        )
        mock_client.articles.create_with_content.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="Article with Parts",
            content="Content with parts",
            owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
            applies_to_parts=[
                "don:core:dvrv-us-1:devo/1:product/1",
                "don:core:dvrv-us-1:devo/1:capability/2",
            ],
        )

        assert result["title"] == "Article with Parts"
        # Verify applies_to_parts was passed to SDK
        call_args = mock_client.articles.create_with_content.call_args
        assert call_args[1]["applies_to_parts"] == [
            "don:core:dvrv-us-1:devo/1:product/1",
            "don:core:dvrv-us-1:devo/1:capability/2",
        ]

    @pytest.mark.asyncio
    async def test_create_with_scope(self, mock_ctx, mock_client):
        """Test creating an article with scope (internal)."""
        mock_article = _make_mock_article(
            title="Internal Article",
            description="Internal content",
        )
        mock_client.articles.create_with_content.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="Internal Article",
            content="Internal content",
            owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
            scope=1,  # 1 = internal
        )

        assert result["title"] == "Internal Article"
        # Verify scope was passed to SDK
        call_args = mock_client.articles.create_with_content.call_args
        assert call_args[1]["scope"] == 1

    @pytest.mark.asyncio
    async def test_create_with_tags(self, mock_ctx, mock_client):
        """Test creating an article with tags."""
        mock_article = _make_mock_article(
            title="Tagged Article",
            description="Content with tags",
        )
        mock_client.articles.create_with_content.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="Tagged Article",
            content="Content with tags",
            owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
            tags=["don:core:dvrv-us-1:devo/1:tag/1", "don:core:dvrv-us-1:devo/1:tag/2"],
        )

        assert result["title"] == "Tagged Article"
        # Verify tags were converted to SetTagWithValue and passed to SDK
        call_args = mock_client.articles.create_with_content.call_args
        tags_arg = call_args[1]["tags"]
        assert len(tags_arg) == 2
        assert tags_arg[0].id == "don:core:dvrv-us-1:devo/1:tag/1"
        assert tags_arg[1].id == "don:core:dvrv-us-1:devo/1:tag/2"


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
        mock_client.articles.update_with_content.return_value = mock_article

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
        mock_client.articles.update_with_content.side_effect = NotFoundError("Article not found")

        with pytest.raises(RuntimeError, match="Article not found"):
            await devrev_articles_update(mock_ctx, id="nonexistent", title="New")

    @pytest.mark.asyncio
    async def test_update_with_applies_to_parts(self, mock_ctx, mock_client):
        """Test updating an article with applies_to_parts."""
        mock_article = _make_mock_article(
            id="article-1",
            title="Updated Article",
            status="published",
        )
        mock_client.articles.update_with_content.return_value = mock_article

        result = await devrev_articles_update(
            mock_ctx,
            id="article-1",
            title="Updated Article",
            applies_to_parts=["don:core:dvrv-us-1:devo/1:feature/3"],
        )

        assert result["title"] == "Updated Article"
        # Verify applies_to_parts was passed to SDK
        call_args = mock_client.articles.update_with_content.call_args
        assert call_args[1]["applies_to_parts"] == ["don:core:dvrv-us-1:devo/1:feature/3"]

    @pytest.mark.asyncio
    async def test_update_with_access_level(self, mock_ctx, mock_client):
        """Test updating an article with access_level."""
        from devrev.models.articles import ArticleAccessLevel

        mock_article = _make_mock_article(
            id="article-1",
            title="Internal Article",
            status="published",
        )
        mock_client.articles.update_with_content.return_value = mock_article

        result = await devrev_articles_update(
            mock_ctx,
            id="article-1",
            access_level="internal",
        )

        assert result["title"] == "Internal Article"
        # Verify access_level was converted to enum and passed to SDK
        call_args = mock_client.articles.update_with_content.call_args
        assert call_args[1]["access_level"] == ArticleAccessLevel.INTERNAL

    @pytest.mark.asyncio
    async def test_update_with_tags(self, mock_ctx, mock_client):
        """Test updating an article with tags."""
        mock_article = _make_mock_article(
            id="article-1",
            title="Tagged Article",
            status="published",
        )
        mock_client.articles.update_with_content.return_value = mock_article

        result = await devrev_articles_update(
            mock_ctx,
            id="article-1",
            tags=["don:core:dvrv-us-1:devo/1:tag/1"],
        )

        assert result["title"] == "Tagged Article"
        # Verify tags were converted to SetTagWithValue and passed to SDK
        call_args = mock_client.articles.update_with_content.call_args
        tags_arg = call_args[1]["tags"]
        assert len(tags_arg) == 1
        assert tags_arg[0].id == "don:core:dvrv-us-1:devo/1:tag/1"

    @pytest.mark.asyncio
    async def test_update_with_invalid_access_level(self, mock_ctx, mock_client):
        """Test updating an article with invalid access_level raises error."""
        with pytest.raises(RuntimeError, match="Invalid access level"):
            await devrev_articles_update(
                mock_ctx,
                id="article-1",
                access_level="invalid_level",
            )

    @pytest.mark.asyncio
    async def test_update_with_empty_tags_removes_all(self, mock_ctx, mock_client):
        """Test updating with empty tags list removes all tags."""
        mock_article = _make_mock_article(
            id="article-1",
            title="No Tags Article",
            status="published",
        )
        mock_client.articles.update_with_content.return_value = mock_article

        result = await devrev_articles_update(
            mock_ctx,
            id="article-1",
            tags=[],
        )

        assert result["title"] == "No Tags Article"
        # Verify empty list is passed (not None) to clear tags
        call_args = mock_client.articles.update_with_content.call_args
        tags_arg = call_args[1]["tags"]
        assert tags_arg is not None
        assert tags_arg == []

    @pytest.mark.asyncio
    async def test_update_with_shared_with(self, mock_ctx, mock_client):
        """Test updating an article with shared_with memberships."""
        mock_article = _make_mock_article(
            id="article-1",
            title="Shared Article",
            status="published",
        )
        mock_client.articles.update_with_content.return_value = mock_article

        result = await devrev_articles_update(
            mock_ctx,
            id="article-1",
            shared_with=[
                {"member": "don:identity:dvrv-us-1:devo/1:devu/100", "role": "editor"},
            ],
        )

        assert result["title"] == "Shared Article"
        # Verify shared_with was converted and passed to SDK
        call_args = mock_client.articles.update_with_content.call_args
        shared_arg = call_args[1]["shared_with"]
        assert shared_arg is not None
        assert len(shared_arg) == 1
        assert shared_arg[0].member == "don:identity:dvrv-us-1:devo/1:devu/100"
        assert shared_arg[0].role == "editor"

    @pytest.mark.asyncio
    async def test_update_without_shared_with(self, mock_ctx, mock_client):
        """Test updating an article without shared_with passes None."""
        mock_article = _make_mock_article(id="article-1", title="Article")
        mock_client.articles.update_with_content.return_value = mock_article

        await devrev_articles_update(
            mock_ctx,
            id="article-1",
            title="Article",
        )

        call_args = mock_client.articles.update_with_content.call_args
        assert call_args[1]["shared_with"] is None

    @pytest.mark.asyncio
    async def test_create_with_empty_tags(self, mock_ctx, mock_client):
        """Test creating with empty tags list passes empty list (not None)."""
        mock_article = _make_mock_article(
            title="No Tags Article",
            description="Content without tags",
        )
        mock_client.articles.create_with_content.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="No Tags Article",
            content="Content without tags",
            owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
            tags=[],
        )

        assert result["title"] == "No Tags Article"
        # Verify empty list is passed (not None)
        call_args = mock_client.articles.create_with_content.call_args
        tags_arg = call_args[1]["tags"]
        assert tags_arg is not None
        assert tags_arg == []

    @pytest.mark.asyncio
    async def test_create_with_shared_with(self, mock_ctx, mock_client):
        """Test creating an article with shared_with memberships."""
        mock_article = _make_mock_article(
            title="Shared Article",
            description="Content shared with users",
        )
        mock_client.articles.create_with_content.return_value = mock_article

        result = await devrev_articles_create(
            mock_ctx,
            title="Shared Article",
            content="Content shared with users",
            owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
            shared_with=[
                {"member": "don:identity:dvrv-us-1:devo/1:devu/100", "role": "viewer"},
                {"member": "don:identity:dvrv-us-1:devo/1:devu/200"},
            ],
        )

        assert result["title"] == "Shared Article"
        # Verify shared_with was converted and passed to SDK
        call_args = mock_client.articles.create_with_content.call_args
        shared_arg = call_args[1]["shared_with"]
        assert shared_arg is not None
        assert len(shared_arg) == 2
        assert shared_arg[0].member == "don:identity:dvrv-us-1:devo/1:devu/100"
        assert shared_arg[0].role == "viewer"
        assert shared_arg[1].member == "don:identity:dvrv-us-1:devo/1:devu/200"
        assert shared_arg[1].role is None

    @pytest.mark.asyncio
    async def test_create_without_shared_with(self, mock_ctx, mock_client):
        """Test creating an article without shared_with passes None."""
        mock_article = _make_mock_article(title="Normal Article", description="Content")
        mock_client.articles.create_with_content.return_value = mock_article

        await devrev_articles_create(
            mock_ctx,
            title="Normal Article",
            content="Content",
            owned_by=["don:identity:dvrv-us-1:devo/test:devu/1"],
        )

        call_args = mock_client.articles.create_with_content.call_args
        assert call_args[1]["shared_with"] is None


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
