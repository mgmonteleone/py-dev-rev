"""Unit tests for unified article methods in ArticlesService."""

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from devrev.exceptions import DevRevError
from devrev.models.articles import (
    Article,
    ArticlesGetRequest,
    ArticlesGetResponse,
    ArticleStatus,
    ArticleWithContent,
)
from devrev.models.artifacts import (
    Artifact,
    ArtifactGetRequest,
    ArtifactGetResponse,
    ArtifactPrepareResponse,
    ArtifactVersionsPrepareResponse,
)
from devrev.services.articles import ArticlesService, AsyncArticlesService


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_http_client() -> MagicMock:
    """Mock HTTP client for sync tests."""
    return MagicMock()


@pytest.fixture
def mock_async_http_client() -> MagicMock:
    """Mock async HTTP client for async tests."""
    client = MagicMock()
    client.post = AsyncMock()
    client.get = AsyncMock()
    return client


@pytest.fixture
def mock_parent_client() -> MagicMock:
    """Mock parent DevRev client with artifacts service."""
    client = MagicMock()
    client.artifacts = MagicMock()
    return client


@pytest.fixture
def mock_async_parent_client() -> MagicMock:
    """Mock async parent DevRev client with artifacts service."""
    client = MagicMock()
    client.artifacts = MagicMock()
    client.artifacts.prepare = AsyncMock()
    client.artifacts.upload = AsyncMock()
    client.artifacts.download = AsyncMock()
    client.artifacts.get = AsyncMock()
    client.artifacts.prepare_version = AsyncMock()
    return client


@pytest.fixture
def articles_service(mock_http_client: MagicMock, mock_parent_client: MagicMock) -> ArticlesService:
    """Create ArticlesService with mocked dependencies."""
    service = ArticlesService(mock_http_client)
    service._parent_client = mock_parent_client
    return service


@pytest.fixture
def articles_service_no_parent(mock_http_client: MagicMock) -> ArticlesService:
    """Create ArticlesService without parent client."""
    return ArticlesService(mock_http_client)


@pytest.fixture
def async_articles_service(
    mock_async_http_client: MagicMock, mock_async_parent_client: MagicMock
) -> AsyncArticlesService:
    """Create AsyncArticlesService with mocked dependencies."""
    service = AsyncArticlesService(mock_async_http_client)
    service._parent_client = mock_async_parent_client
    return service


@pytest.fixture
def async_articles_service_no_parent(mock_async_http_client: MagicMock) -> AsyncArticlesService:
    """Create AsyncArticlesService without parent client."""
    return AsyncArticlesService(mock_async_http_client)


@pytest.fixture
def mock_artifact_prepare_response() -> ArtifactPrepareResponse:
    """Mock artifact preparation response."""
    return ArtifactPrepareResponse(
        id="artifact-123",
        url="https://s3.example.com/upload",
        form_data=[
            {"key": "key", "value": "upload-key"},
            {"key": "Content-Type", "value": "text/html"},
        ],
    )


@pytest.fixture
def mock_article() -> Article:
    """Mock article with content artifact reference."""
    return Article(
        id="article-123",
        title="Test Article",
        description="Test description",
        owned_by=[{"id": "user-123"}],
        resource={"content_artifact": "artifact-123"},
    )


@pytest.fixture
def mock_article_no_resource() -> Article:
    """Mock article without resource field."""
    return Article(
        id="article-456",
        title="No Resource Article",
        owned_by=[{"id": "user-123"}],
    )


@pytest.fixture
def mock_artifact() -> Artifact:
    """Mock artifact metadata."""
    return Artifact(
        id="artifact-123",
        file_name="test.html",
        file_type="text/html",
        version="1",
    )


# ============================================================================
# create_with_content() Tests - Sync
# ============================================================================


class TestCreateWithContent:
    """Tests for create_with_content() method."""

    def test_create_with_content_success(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test successful article creation with content."""
        # Setup mocks
        mock_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        # Execute
        result = articles_service.create_with_content(
            title="Test Article",
            content="<html>Test content</html>",
            owned_by=["user-123"],
            content_format="text/html",
        )

        # Verify
        assert result.id == "article-123"
        assert result.title == "Test Article"
        mock_parent_client.artifacts.prepare.assert_called_once()
        mock_parent_client.artifacts.upload.assert_called_once()

    def test_create_with_content_html(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test article creation with HTML content format."""
        mock_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        result = articles_service.create_with_content(
            title="HTML Article",
            content="<html><body>HTML content</body></html>",
            owned_by=["user-123"],
            content_format="text/html",
        )

        assert result is not None
        # Verify content format was used
        prepare_call = mock_parent_client.artifacts.prepare.call_args
        assert prepare_call[0][0].file_type == "text/html"

    def test_create_with_content_markdown(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test article creation with Markdown content format."""
        mock_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        result = articles_service.create_with_content(
            title="Markdown Article",
            content="# Heading\n\nMarkdown content",
            owned_by=["user-123"],
            content_format="text/markdown",
        )

        assert result is not None
        prepare_call = mock_parent_client.artifacts.prepare.call_args
        assert prepare_call[0][0].file_type == "text/markdown"

    def test_create_with_content_plain_text(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test article creation with plain text content format (default)."""
        mock_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        result = articles_service.create_with_content(
            title="Plain Text Article",
            content="Plain text content",
            owned_by=["user-123"],
        )

        assert result is not None
        prepare_call = mock_parent_client.artifacts.prepare.call_args
        assert prepare_call[0][0].file_type == "text/plain"

    def test_create_with_content_with_metadata(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test article creation with description and status metadata."""
        mock_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        result = articles_service.create_with_content(
            title="Article with Metadata",
            content="Content",
            owned_by=["user-123"],
            description="Short description",
            status=ArticleStatus.PUBLISHED,
        )

        assert result is not None
        # Verify metadata was passed to create
        post_call = mock_http_client.post.call_args
        data = post_call[1]["data"]
        assert data["description"] == "Short description"
        assert data["status"] == "published"

    def test_create_with_content_rollback_on_artifact_failure(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
    ) -> None:
        """Test that article is not created if artifact preparation fails."""
        # Artifact preparation fails
        mock_parent_client.artifacts.prepare.side_effect = Exception("Artifact prepare failed")

        with pytest.raises(DevRevError, match="Failed to create article with content"):
            articles_service.create_with_content(
                title="Failed Article",
                content="Content",
                owned_by=["user-123"],
            )

        # Verify upload and article creation were not called
        mock_parent_client.artifacts.upload.assert_not_called()

    def test_create_with_content_rollback_on_article_failure(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_http_client: MagicMock,
    ) -> None:
        """Test rollback behavior when article creation fails after artifact upload."""
        # Artifact operations succeed
        mock_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_parent_client.artifacts.upload.return_value = None

        # Article creation fails
        mock_http_client.post.side_effect = Exception("Article create failed")

        with pytest.raises(DevRevError, match="Failed to create article with content"):
            articles_service.create_with_content(
                title="Failed Article",
                content="Content",
                owned_by=["user-123"],
            )

        # Verify artifact was prepared and uploaded before failure
        mock_parent_client.artifacts.prepare.assert_called_once()
        mock_parent_client.artifacts.upload.assert_called_once()

    def test_create_with_content_no_parent_client(
        self,
        articles_service_no_parent: ArticlesService,
    ) -> None:
        """Test error when parent_client is not set."""
        with pytest.raises(DevRevError, match="create_with_content requires parent client"):
            articles_service_no_parent.create_with_content(
                title="Test",
                content="Content",
                owned_by=["user-123"],
            )


# ============================================================================
# get_with_content() Tests - Sync
# ============================================================================


class TestGetWithContent:
    """Tests for get_with_content() method."""

    def test_get_with_content_success(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_artifact: Artifact,
        mock_http_client: MagicMock,
    ) -> None:
        """Test successful retrieval of article with content."""
        # Need to handle multiple post calls
        def post_side_effect(endpoint, *args, **kwargs):
            if "articles.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"article": mock_article.model_dump(mode="json")}
                return response
            elif "artifacts.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"artifact": mock_artifact.model_dump(mode="json")}
                return response
            return MagicMock()

        mock_http_client.post.side_effect = post_side_effect

        # Mock artifact operations
        mock_parent_client.artifacts.download.return_value = b"<html>Article content</html>"
        mock_parent_client.artifacts.get.return_value = mock_artifact

        result = articles_service.get_with_content("article-123")

        assert isinstance(result, ArticleWithContent)
        assert result.article.id == "article-123"
        assert result.content == "<html>Article content</html>"
        assert result.content_format == "text/html"

    def test_get_with_content_html(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_artifact: Artifact,
        mock_http_client: MagicMock,
    ) -> None:
        """Test HTML content decoding."""
        def post_side_effect(endpoint, *args, **kwargs):
            if "articles.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"article": mock_article.model_dump(mode="json")}
                return response
            elif "artifacts.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"artifact": mock_artifact.model_dump(mode="json")}
                return response
            return MagicMock()

        mock_http_client.post.side_effect = post_side_effect
        mock_parent_client.artifacts.download.return_value = b"<html><body>HTML content</body></html>"
        mock_parent_client.artifacts.get.return_value = mock_artifact

        result = articles_service.get_with_content("article-123")

        assert result.content == "<html><body>HTML content</body></html>"
        assert result.content_format == "text/html"

    def test_get_with_content_markdown(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test markdown content retrieval."""
        markdown_artifact = Artifact(
            id="artifact-123",
            file_name="test.md",
            file_type="text/markdown",
            version="1",
        )

        def post_side_effect(endpoint, *args, **kwargs):
            if "articles.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"article": mock_article.model_dump(mode="json")}
                return response
            elif "artifacts.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"artifact": markdown_artifact.model_dump(mode="json")}
                return response
            return MagicMock()

        mock_http_client.post.side_effect = post_side_effect
        mock_parent_client.artifacts.download.return_value = b"# Heading\n\nMarkdown content"
        mock_parent_client.artifacts.get.return_value = markdown_artifact

        result = articles_service.get_with_content("article-123")

        assert result.content == "# Heading\n\nMarkdown content"
        assert result.content_format == "text/markdown"

    def test_get_with_content_no_artifact(
        self,
        articles_service: ArticlesService,
        mock_article_no_resource: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test error when article has no content artifact."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article_no_resource.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        with pytest.raises(DevRevError, match="has no resource field"):
            articles_service.get_with_content("article-456")

    def test_get_with_content_missing_resource(
        self,
        articles_service: ArticlesService,
        mock_http_client: MagicMock,
    ) -> None:
        """Test error when article resource field is missing."""
        article_no_resource = Article(
            id="article-789",
            title="No Resource",
            owned_by=[{"id": "user-123"}],
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": article_no_resource.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        with pytest.raises(DevRevError, match="has no resource field"):
            articles_service.get_with_content("article-789")

    def test_get_with_content_artifact_not_found(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test error handling when artifact download fails."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        mock_parent_client.artifacts.download.side_effect = Exception("Artifact not found")

        with pytest.raises(DevRevError, match="Failed to download content"):
            articles_service.get_with_content("article-123")

    def test_get_with_content_no_parent_client(
        self,
        articles_service_no_parent: ArticlesService,
    ) -> None:
        """Test error when parent_client is not set."""
        with pytest.raises(DevRevError, match="get_with_content requires parent client"):
            articles_service_no_parent.get_with_content("article-123")


# ============================================================================
# update_content() Tests - Sync
# ============================================================================


class TestUpdateContent:
    """Tests for update_content() method."""

    def test_update_content_success(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test successful content update."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_parent_client.artifacts.prepare_version.return_value = version_response
        mock_parent_client.artifacts.upload.return_value = None

        def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_http_client.post.side_effect = post_side_effect

        result = articles_service.update_content(
            "article-123",
            "<html>Updated content</html>",
        )

        assert result.id == "article-123"
        mock_parent_client.artifacts.prepare_version.assert_called_once()
        mock_parent_client.artifacts.upload.assert_called_once()

    def test_update_content_new_version(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test that new artifact version is created."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_parent_client.artifacts.prepare_version.return_value = version_response
        mock_parent_client.artifacts.upload.return_value = None

        def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_http_client.post.side_effect = post_side_effect

        articles_service.update_content("article-123", "New content")

        # Verify version preparation was called with artifact ID
        prepare_call = mock_parent_client.artifacts.prepare_version.call_args
        assert prepare_call[0][0].id == "artifact-123"

    def test_update_content_format_change(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test updating content format."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_parent_client.artifacts.prepare_version.return_value = version_response
        mock_parent_client.artifacts.upload.return_value = None

        def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_http_client.post.side_effect = post_side_effect

        result = articles_service.update_content(
            "article-123",
            "# New markdown content",
            content_format="text/markdown",
        )

        assert result is not None

    def test_update_content_no_artifact(
        self,
        articles_service: ArticlesService,
        mock_article_no_resource: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test error when article has no existing content artifact."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article_no_resource.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        with pytest.raises(DevRevError, match="has no resource field"):
            articles_service.update_content("article-456", "New content")

    def test_update_content_no_parent_client(
        self,
        articles_service_no_parent: ArticlesService,
    ) -> None:
        """Test error when parent_client is not set."""
        with pytest.raises(DevRevError, match="update_content requires parent client"):
            articles_service_no_parent.update_content("article-123", "Content")


# ============================================================================
# update_with_content() Tests - Sync
# ============================================================================


class TestUpdateWithContent:
    """Tests for update_with_content() method."""

    def test_update_with_content_metadata_only(
        self,
        articles_service: ArticlesService,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test updating only metadata (title/description)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        result = articles_service.update_with_content(
            "article-123",
            title="New Title",
            description="New description",
        )

        assert result.id == "article-123"
        # Verify update was called
        post_call = mock_http_client.post.call_args
        assert "articles.update" in post_call[0][0]

    def test_update_with_content_content_only(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test updating only content."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_parent_client.artifacts.prepare_version.return_value = version_response
        mock_parent_client.artifacts.upload.return_value = None

        def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_http_client.post.side_effect = post_side_effect

        result = articles_service.update_with_content(
            "article-123",
            content="New content only",
        )

        assert result.id == "article-123"
        mock_parent_client.artifacts.prepare_version.assert_called_once()

    def test_update_with_content_both(
        self,
        articles_service: ArticlesService,
        mock_parent_client: MagicMock,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test updating both metadata and content."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_parent_client.artifacts.prepare_version.return_value = version_response
        mock_parent_client.artifacts.upload.return_value = None

        def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_http_client.post.side_effect = post_side_effect

        result = articles_service.update_with_content(
            "article-123",
            title="New Title",
            content="New content",
            status=ArticleStatus.PUBLISHED,
        )

        assert result.id == "article-123"
        # Both content update and metadata update should be called
        mock_parent_client.artifacts.prepare_version.assert_called_once()

    def test_update_with_content_no_changes(
        self,
        articles_service: ArticlesService,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test handling when no changes are provided (no-op)."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        result = articles_service.update_with_content("article-123")

        assert result.id == "article-123"
        # Should just return the article via get

    def test_update_with_content_status_only(
        self,
        articles_service: ArticlesService,
        mock_article: Article,
        mock_http_client: MagicMock,
    ) -> None:
        """Test updating only status."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_http_client.post.return_value = mock_response

        result = articles_service.update_with_content(
            "article-123",
            status=ArticleStatus.ARCHIVED,
        )

        assert result.id == "article-123"

    def test_update_with_content_no_parent_client(
        self,
        articles_service_no_parent: ArticlesService,
    ) -> None:
        """Test error when parent_client is not set."""
        with pytest.raises(DevRevError, match="update_with_content requires parent client"):
            articles_service_no_parent.update_with_content("article-123", title="New")


# ============================================================================
# Async Tests
# ============================================================================


class TestCreateWithContentAsync:
    """Async tests for create_with_content() method."""

    @pytest.mark.asyncio
    async def test_async_create_with_content_success(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async article creation with content."""
        mock_async_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_async_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        result = await async_articles_service.create_with_content(
            title="Async Article",
            content="<html>Async content</html>",
            owned_by=["user-123"],
            content_format="text/html",
        )

        assert result.id == "article-123"

    @pytest.mark.asyncio
    async def test_async_create_with_content_html(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async HTML content creation."""
        mock_async_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_async_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        result = await async_articles_service.create_with_content(
            title="HTML Article",
            content="<html>HTML</html>",
            owned_by=["user-123"],
            content_format="text/html",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_async_create_with_content_markdown(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async markdown content creation."""
        mock_async_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_async_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        result = await async_articles_service.create_with_content(
            title="Markdown",
            content="# Heading",
            owned_by=["user-123"],
            content_format="text/markdown",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_async_create_with_content_plain_text(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async plain text content creation."""
        mock_async_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_async_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        result = await async_articles_service.create_with_content(
            title="Plain",
            content="Plain text",
            owned_by=["user-123"],
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_async_create_with_content_with_metadata(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async creation with metadata."""
        mock_async_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_async_parent_client.artifacts.upload.return_value = None

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        result = await async_articles_service.create_with_content(
            title="With Metadata",
            content="Content",
            owned_by=["user-123"],
            description="Description",
            status=ArticleStatus.DRAFT,
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_async_create_with_content_rollback_on_artifact_failure(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
    ) -> None:
        """Test async rollback on artifact failure."""
        mock_async_parent_client.artifacts.prepare.side_effect = Exception("Prepare failed")

        with pytest.raises(DevRevError, match="Failed to create article with content"):
            await async_articles_service.create_with_content(
                title="Failed",
                content="Content",
                owned_by=["user-123"],
            )

    @pytest.mark.asyncio
    async def test_async_create_with_content_rollback_on_article_failure(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_artifact_prepare_response: ArtifactPrepareResponse,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async rollback on article creation failure."""
        mock_async_parent_client.artifacts.prepare.return_value = mock_artifact_prepare_response
        mock_async_parent_client.artifacts.upload.return_value = None
        mock_async_http_client.post.side_effect = Exception("Article create failed")

        with pytest.raises(DevRevError, match="Failed to create article with content"):
            await async_articles_service.create_with_content(
                title="Failed",
                content="Content",
                owned_by=["user-123"],
            )

    @pytest.mark.asyncio
    async def test_async_create_with_content_no_parent_client(
        self,
        async_articles_service_no_parent: AsyncArticlesService,
    ) -> None:
        """Test async error when parent_client not set."""
        with pytest.raises(DevRevError, match="create_with_content requires parent client"):
            await async_articles_service_no_parent.create_with_content(
                title="Test",
                content="Content",
                owned_by=["user-123"],
            )


class TestGetWithContentAsync:
    """Async tests for get_with_content() method."""

    @pytest.mark.asyncio
    async def test_async_get_with_content_success(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_artifact: Artifact,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async retrieval with content."""
        async def post_side_effect(endpoint, *args, **kwargs):
            if "articles.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"article": mock_article.model_dump(mode="json")}
                return response
            elif "artifacts.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"artifact": mock_artifact.model_dump(mode="json")}
                return response
            return MagicMock()

        mock_async_http_client.post.side_effect = post_side_effect
        mock_async_parent_client.artifacts.download.return_value = b"<html>Content</html>"

        # Create AsyncMock that returns the artifact
        async_get_mock = AsyncMock(return_value=mock_artifact)
        mock_async_parent_client.artifacts.get = async_get_mock

        result = await async_articles_service.get_with_content("article-123")

        assert isinstance(result, ArticleWithContent)
        assert result.content == "<html>Content</html>"

    @pytest.mark.asyncio
    async def test_async_get_with_content_html(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_artifact: Artifact,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async HTML content retrieval."""
        async def post_side_effect(endpoint, *args, **kwargs):
            if "articles.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"article": mock_article.model_dump(mode="json")}
                return response
            return MagicMock()

        mock_async_http_client.post.side_effect = post_side_effect
        mock_async_parent_client.artifacts.download.return_value = b"<html>HTML</html>"

        # Create AsyncMock that returns the artifact
        async_get_mock = AsyncMock(return_value=mock_artifact)
        mock_async_parent_client.artifacts.get = async_get_mock

        result = await async_articles_service.get_with_content("article-123")

        assert result.content_format == "text/html"

    @pytest.mark.asyncio
    async def test_async_get_with_content_markdown(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async markdown content retrieval."""
        markdown_artifact = Artifact(
            id="artifact-123",
            file_name="test.md",
            file_type="text/markdown",
            version="1",
        )

        async def post_side_effect(endpoint, *args, **kwargs):
            if "articles.get" in endpoint:
                response = MagicMock()
                response.json.return_value = {"article": mock_article.model_dump(mode="json")}
                return response
            return MagicMock()

        mock_async_http_client.post.side_effect = post_side_effect
        mock_async_parent_client.artifacts.download.return_value = b"# Markdown"

        # Create AsyncMock that returns the artifact
        async_get_mock = AsyncMock(return_value=markdown_artifact)
        mock_async_parent_client.artifacts.get = async_get_mock

        result = await async_articles_service.get_with_content("article-123")

        assert result.content_format == "text/markdown"

    @pytest.mark.asyncio
    async def test_async_get_with_content_no_artifact(
        self,
        async_articles_service: AsyncArticlesService,
        mock_article_no_resource: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async error when no artifact."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article_no_resource.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        with pytest.raises(DevRevError, match="has no resource field"):
            await async_articles_service.get_with_content("article-456")

    @pytest.mark.asyncio
    async def test_async_get_with_content_missing_resource(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async error when resource missing."""
        article = Article(
            id="article-789",
            title="No Resource",
            owned_by=[{"id": "user-123"}],
        )

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        with pytest.raises(DevRevError, match="has no resource field"):
            await async_articles_service.get_with_content("article-789")

    @pytest.mark.asyncio
    async def test_async_get_with_content_artifact_not_found(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async error when artifact not found."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        mock_async_parent_client.artifacts.download.side_effect = Exception("Not found")

        with pytest.raises(DevRevError, match="Failed to download content"):
            await async_articles_service.get_with_content("article-123")

    @pytest.mark.asyncio
    async def test_async_get_with_content_no_parent_client(
        self,
        async_articles_service_no_parent: AsyncArticlesService,
    ) -> None:
        """Test async error when parent_client not set."""
        with pytest.raises(DevRevError, match="get_with_content requires parent client"):
            await async_articles_service_no_parent.get_with_content("article-123")


class TestUpdateContentAsync:
    """Async tests for update_content() method."""

    @pytest.mark.asyncio
    async def test_async_update_content_success(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async content update."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_async_parent_client.artifacts.prepare_version.return_value = version_response
        mock_async_parent_client.artifacts.upload.return_value = None

        async def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_async_http_client.post.side_effect = post_side_effect

        result = await async_articles_service.update_content("article-123", "New content")

        assert result.id == "article-123"

    @pytest.mark.asyncio
    async def test_async_update_content_new_version(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async new version creation."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_async_parent_client.artifacts.prepare_version.return_value = version_response
        mock_async_parent_client.artifacts.upload.return_value = None

        async def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_async_http_client.post.side_effect = post_side_effect

        await async_articles_service.update_content("article-123", "New")

        mock_async_parent_client.artifacts.prepare_version.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_update_content_format_change(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async content format change."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_async_parent_client.artifacts.prepare_version.return_value = version_response
        mock_async_parent_client.artifacts.upload.return_value = None

        async def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_async_http_client.post.side_effect = post_side_effect

        result = await async_articles_service.update_content(
            "article-123",
            "# Markdown",
            content_format="text/markdown",
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_async_update_content_no_artifact(
        self,
        async_articles_service: AsyncArticlesService,
        mock_article_no_resource: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async error when no artifact."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article_no_resource.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        with pytest.raises(DevRevError, match="has no resource field"):
            await async_articles_service.update_content("article-456", "Content")

    @pytest.mark.asyncio
    async def test_async_update_content_no_parent_client(
        self,
        async_articles_service_no_parent: AsyncArticlesService,
    ) -> None:
        """Test async error when parent_client not set."""
        with pytest.raises(DevRevError, match="update_content requires parent client"):
            await async_articles_service_no_parent.update_content("article-123", "Content")


class TestUpdateWithContentAsync:
    """Async tests for update_with_content() method."""

    @pytest.mark.asyncio
    async def test_async_update_with_content_metadata_only(
        self,
        async_articles_service: AsyncArticlesService,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async metadata-only update."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        result = await async_articles_service.update_with_content(
            "article-123",
            title="New Title",
        )

        assert result.id == "article-123"

    @pytest.mark.asyncio
    async def test_async_update_with_content_content_only(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async content-only update."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_async_parent_client.artifacts.prepare_version.return_value = version_response
        mock_async_parent_client.artifacts.upload.return_value = None

        async def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_async_http_client.post.side_effect = post_side_effect

        result = await async_articles_service.update_with_content(
            "article-123",
            content="New content",
        )

        assert result.id == "article-123"

    @pytest.mark.asyncio
    async def test_async_update_with_content_both(
        self,
        async_articles_service: AsyncArticlesService,
        mock_async_parent_client: MagicMock,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async update of both metadata and content."""
        version_response = ArtifactVersionsPrepareResponse(
            id="artifact-123",
            url="https://s3.example.com/upload",
            form_data=[],
        )

        mock_async_parent_client.artifacts.prepare_version.return_value = version_response
        mock_async_parent_client.artifacts.upload.return_value = None

        async def post_side_effect(endpoint, *args, **kwargs):
            response = MagicMock()
            response.json.return_value = {"article": mock_article.model_dump(mode="json")}
            return response

        mock_async_http_client.post.side_effect = post_side_effect

        result = await async_articles_service.update_with_content(
            "article-123",
            title="New Title",
            content="New content",
        )

        assert result.id == "article-123"

    @pytest.mark.asyncio
    async def test_async_update_with_content_no_changes(
        self,
        async_articles_service: AsyncArticlesService,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async no-op update."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        result = await async_articles_service.update_with_content("article-123")

        assert result.id == "article-123"

    @pytest.mark.asyncio
    async def test_async_update_with_content_status_only(
        self,
        async_articles_service: AsyncArticlesService,
        mock_article: Article,
        mock_async_http_client: MagicMock,
    ) -> None:
        """Test async status-only update."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "article": mock_article.model_dump(mode="json")
        }
        mock_async_http_client.post.return_value = mock_response

        result = await async_articles_service.update_with_content(
            "article-123",
            status=ArticleStatus.PUBLISHED,
        )

        assert result.id == "article-123"

    @pytest.mark.asyncio
    async def test_async_update_with_content_no_parent_client(
        self,
        async_articles_service_no_parent: AsyncArticlesService,
    ) -> None:
        """Test async error when parent_client not set."""
        with pytest.raises(DevRevError, match="update_with_content requires parent client"):
            await async_articles_service_no_parent.update_with_content(
                "article-123",
                title="New",
            )
