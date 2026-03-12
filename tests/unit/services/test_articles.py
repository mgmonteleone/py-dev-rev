"""Unit tests for ArticlesService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.articles import (
    Article,
    ArticleAccessLevel,
    ArticlesCreateRequest,
    ArticlesDeleteRequest,
    ArticlesGetRequest,
    ArticlesListRequest,
    ArticleStatus,
    ArticlesUpdateRequest,
    ArticlesUpdateRequestOwnedBy,
    ArticlesUpdateRequestTags,
    ArticleType,
    SetSharedWithMembership,
)
from devrev.models.base import SetTagWithValue
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
            description="# Test Description",
            status=ArticleStatus.PUBLISHED,
            owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
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

        assert len(result.articles) == 1
        assert isinstance(result.articles[0], Article)
        assert result.articles[0].id == "don:core:article:123"
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

        assert len(result.articles) == 1
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

        assert len(result.articles) == 0
        mock_http_client.post.assert_called_once()

    def test_create_article_with_full_params(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test creating an article with all supported parameters."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        service = ArticlesService(mock_http_client)
        request = ArticlesCreateRequest(
            title="Full Article",
            status=ArticleStatus.DRAFT,
            owned_by=["don:identity:user:456"],
            description="A fully specified article",
            resource={"content_artifact": "don:core:artifact:789"},
        )
        result = service.create(request)

        assert isinstance(result, Article)
        mock_http_client.post.assert_called_once()

    def test_update_article_with_full_params(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test updating an article with all supported parameters."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        service = ArticlesService(mock_http_client)
        request = ArticlesUpdateRequest(
            id="don:core:article:123",
            title="Updated Title",
            status=ArticleStatus.PUBLISHED,
            access_level=ArticleAccessLevel.EXTERNAL,
            owned_by=ArticlesUpdateRequestOwnedBy(set=["don:identity:user:456"]),
            tags=ArticlesUpdateRequestTags(set=[SetTagWithValue(id="don:core:tag:123")]),
            language="fr",
            description="Updated description",
        )
        result = service.update(request)

        assert isinstance(result, Article)
        mock_http_client.post.assert_called_once()

    def test_list_articles_with_filters(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test listing articles with filter parameters."""
        mock_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data]}
        )

        service = ArticlesService(mock_http_client)
        request = ArticlesListRequest(
            limit=25,
            article_type=[ArticleType.ARTICLE],
            authored_by=["don:identity:user:789"],
            owned_by=["don:identity:user:456"],
            tags=["don:core:tag:123"],
        )
        result = service.list(request)

        assert len(result.articles) == 1
        assert isinstance(result.articles[0], Article)
        mock_http_client.post.assert_called_once()

    def test_list_articles_with_status_filter(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test listing articles filtered by status."""
        mock_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data]}
        )

        service = ArticlesService(mock_http_client)
        result = service.list(status=[ArticleStatus.DRAFT])

        assert len(result.articles) == 1
        # Verify status was sent in request payload
        call_data = mock_http_client.post.call_args.kwargs["data"]
        assert call_data["status"] == ["draft"]
        mock_http_client.post.assert_called_once()

    def test_list_articles_with_pagination_cursor(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test listing articles returns next_cursor for pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data], "next_cursor": "abc123"}
        )

        service = ArticlesService(mock_http_client)
        result = service.list(limit=10)

        assert len(result.articles) == 1
        assert result.next_cursor == "abc123"
        mock_http_client.post.assert_called_once()

    def test_list_articles_with_keyword_args(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test listing articles using keyword arguments."""
        mock_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data]}
        )

        service = ArticlesService(mock_http_client)
        result = service.list(
            limit=25,
            status=[ArticleStatus.PUBLISHED],
            owned_by=["don:identity:user:456"],
        )

        assert len(result.articles) == 1
        call_data = mock_http_client.post.call_args.kwargs["data"]
        assert call_data["status"] == ["published"]
        assert call_data["owned_by"] == ["don:identity:user:456"]
        assert call_data["limit"] == 25

    def test_create_with_content_language_param(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test that language param is forwarded to the ArticlesCreateRequest."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        mock_parent = MagicMock()
        prepare_resp = MagicMock()
        prepare_resp.id = "artifact-123"
        mock_parent.artifacts.prepare.return_value = prepare_resp
        mock_parent.artifacts.upload.return_value = None

        service = ArticlesService(mock_http_client, parent_client=mock_parent)
        service.create_with_content(
            title="Test Article",
            content="test content",
            owned_by=["user-1"],
            content_format="devrev/rt",
            language="en",
        )

        mock_http_client.post.assert_called_once()
        call_data = mock_http_client.post.call_args.kwargs["data"]
        assert call_data["language"] == "en"

    def test_create_with_content_authored_by_param(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test that authored_by param is forwarded to the ArticlesCreateRequest."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        mock_parent = MagicMock()
        prepare_resp = MagicMock()
        prepare_resp.id = "artifact-123"
        mock_parent.artifacts.prepare.return_value = prepare_resp
        mock_parent.artifacts.upload.return_value = None

        service = ArticlesService(mock_http_client, parent_client=mock_parent)
        service.create_with_content(
            title="Test Article",
            content="test content",
            owned_by=["user-1"],
            content_format="devrev/rt",
            authored_by=["author-1"],
        )

        mock_http_client.post.assert_called_once()
        call_data = mock_http_client.post.call_args.kwargs["data"]
        assert call_data["authored_by"] == ["author-1"]

    def test_create_with_content_language_and_authored_by(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test that both language and authored_by are forwarded to the ArticlesCreateRequest."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        mock_parent = MagicMock()
        prepare_resp = MagicMock()
        prepare_resp.id = "artifact-123"
        mock_parent.artifacts.prepare.return_value = prepare_resp
        mock_parent.artifacts.upload.return_value = None

        service = ArticlesService(mock_http_client, parent_client=mock_parent)
        service.create_with_content(
            title="Test Article",
            content="test content",
            owned_by=["user-1"],
            content_format="devrev/rt",
            language="fr",
            authored_by=["author-1", "author-2"],
        )

        mock_http_client.post.assert_called_once()
        call_data = mock_http_client.post.call_args.kwargs["data"]
        assert call_data["language"] == "fr"
        assert call_data["authored_by"] == ["author-1", "author-2"]

    def test_update_with_content_shared_with_serialization(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test that shared_with is wrapped in ArticlesUpdateRequestSharedWith for updates.

        The update path wraps shared_with in {"set": [...]} unlike the create path
        which passes a raw list. This test asserts the serialized payload shape.
        """
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        mock_parent = MagicMock()
        service = ArticlesService(mock_http_client, parent_client=mock_parent)

        memberships = [
            SetSharedWithMembership(member="don:identity:user:100"),
            SetSharedWithMembership(member="don:identity:user:200", role="editor"),
        ]
        service.update_with_content(
            "don:core:article:123",
            shared_with=memberships,
        )

        # update_with_content calls update -> _post, so check the serialized payload
        mock_http_client.post.assert_called_once()
        call_data = mock_http_client.post.call_args.kwargs["data"]
        assert "shared_with" in call_data
        assert "set" in call_data["shared_with"]
        assert len(call_data["shared_with"]["set"]) == 2
        assert call_data["shared_with"]["set"][0]["member"] == "don:identity:user:100"
        assert call_data["shared_with"]["set"][1]["member"] == "don:identity:user:200"
        assert call_data["shared_with"]["set"][1]["role"] == "editor"

    def test_update_with_content_empty_shared_with_clears_sharing(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test that an empty shared_with list serializes as {"set": []} to clear sharing."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        mock_parent = MagicMock()
        service = ArticlesService(mock_http_client, parent_client=mock_parent)

        service.update_with_content(
            "don:core:article:123",
            shared_with=[],
        )

        mock_http_client.post.assert_called_once()
        call_data = mock_http_client.post.call_args.kwargs["data"]
        assert "shared_with" in call_data
        assert call_data["shared_with"] == {"set": []}

    def test_update_with_content_without_shared_with_omits_field(
        self,
        mock_http_client: MagicMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test that shared_with is omitted from payload when not provided."""
        mock_http_client.post.return_value = create_mock_response({"article": sample_article_data})

        mock_parent = MagicMock()
        service = ArticlesService(mock_http_client, parent_client=mock_parent)

        service.update_with_content(
            "don:core:article:123",
            title="Updated Title",
        )

        mock_http_client.post.assert_called_once()
        call_data = mock_http_client.post.call_args.kwargs["data"]
        # shared_with should not be in the payload (or be None/excluded)
        assert call_data.get("shared_with") is None
