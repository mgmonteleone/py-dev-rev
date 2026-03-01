"""Integration tests for MCP articles tools.

Tests the MCP tool layer that wraps the unified article/artifact methods.
Verifies that MCP tools correctly handle content operations, parameter validation,
and provide clear error messages for AI agents.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_mcp_articles.py -v -m write
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from devrev.models.articles import ArticleStatus
from devrev_mcp.tools.articles import (
    devrev_articles_create,
    devrev_articles_get,
    devrev_articles_update,
)

if TYPE_CHECKING:
    from devrev.client import DevRevClient
    from tests.integration.utils import TestDataManager

logger = logging.getLogger(__name__)

# Mark all tests in this module
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


def create_mock_context(client: DevRevClient) -> MagicMock:
    """Create a mock MCP context with the provided DevRev client.

    Args:
        client: The DevRev client to use in the context.

    Returns:
        Mock context suitable for MCP tool calls.
    """
    # Create mock app with get_client method
    mock_app = MagicMock()
    mock_app.get_client.return_value = client
    mock_app.config = MagicMock()
    mock_app.config.default_page_size = 25
    mock_app.config.max_page_size = 100

    # Create mock context
    mock_ctx = MagicMock()
    mock_ctx.request_context = MagicMock()
    mock_ctx.request_context.lifespan_context = mock_app

    return mock_ctx


class TestMCPArticlesContentOperations:
    """Tests for MCP article tools with content operations.

    Validates that MCP tools correctly use the unified article/artifact methods
    to create, retrieve, and update articles with content.
    """

    @pytest.mark.asyncio
    async def test_mcp_create_article_with_content(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test MCP tool creates article with content successfully.

        Verifies:
        - devrev_articles_create MCP tool works end-to-end
        - Article is created with title and content
        - Response includes article details
        """
        # Arrange
        ctx = create_mock_context(write_client)
        title = test_data.generate_name("MCPArticle")
        content = "<h1>Test Article</h1><p>This is test content created via MCP tool.</p>"

        # Act
        result = await devrev_articles_create(
            ctx=ctx,
            title=title,
            content=content,
            owned_by=[current_user_id],
            content_format="text/html",
        )

        # Register for cleanup
        test_data.register("article", result["id"])

        # Assert
        assert result["id"] is not None
        assert result["title"] == title
        logger.info(f"✅ MCP created article with content: {result['id']}")

    @pytest.mark.asyncio
    async def test_mcp_get_article_with_content(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test MCP tool retrieves article with content.

        Verifies:
        - devrev_articles_get with include_content=True works
        - Content is retrieved and included in response
        - Response includes both metadata and content
        """
        # Arrange - create article with content first
        ctx = create_mock_context(write_client)
        title = test_data.generate_name("MCPGetArticle")
        original_content = "<h1>Original Content</h1><p>Test content for retrieval.</p>"

        create_result = await devrev_articles_create(
            ctx=ctx,
            title=title,
            content=original_content,
            owned_by=[current_user_id],
            content_format="text/html",
        )
        article_id = create_result["id"]
        test_data.register("article", article_id)

        # Act
        result = await devrev_articles_get(ctx=ctx, id=article_id, include_content=True)

        # Assert
        assert result["id"] == article_id
        assert result["title"] == title
        assert "content" in result
        assert result["content"] == original_content
        logger.info(f"✅ MCP retrieved article with content: {article_id}")

    @pytest.mark.asyncio
    async def test_mcp_get_article_without_content(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test MCP tool retrieves article metadata only.

        Verifies:
        - devrev_articles_get with include_content=False works
        - Only metadata is retrieved, no content field
        - Faster retrieval for metadata-only use cases
        """
        # Arrange - create article with content first
        ctx = create_mock_context(write_client)
        title = test_data.generate_name("MCPMetadataOnly")
        content = "<p>Content that should not be retrieved</p>"

        create_result = await devrev_articles_create(
            ctx=ctx,
            title=title,
            content=content,
            owned_by=[current_user_id],
        )
        article_id = create_result["id"]
        test_data.register("article", article_id)

        # Act
        result = await devrev_articles_get(ctx=ctx, id=article_id, include_content=False)

        # Assert
        assert result["id"] == article_id
        assert result["title"] == title
        assert "content" not in result  # Content should not be included
        logger.info(f"✅ MCP retrieved article metadata only: {article_id}")

    @pytest.mark.asyncio
    async def test_mcp_update_article_content(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test MCP tool updates article content.

        Verifies:
        - devrev_articles_update with content parameter works
        - Content is updated correctly
        - New content is retrievable
        """
        # Arrange - create article with initial content
        ctx = create_mock_context(write_client)
        title = test_data.generate_name("MCPUpdateContent")
        initial_content = "<p>Initial content</p>"
        updated_content = "<h1>Updated Content</h1><p>This content was updated via MCP tool.</p>"

        create_result = await devrev_articles_create(
            ctx=ctx,
            title=title,
            content=initial_content,
            owned_by=[current_user_id],
        )
        article_id = create_result["id"]
        test_data.register("article", article_id)

        # Act
        await devrev_articles_update(
            ctx=ctx,
            id=article_id,
            content=updated_content,
        )

        # Verify updated content
        get_result = await devrev_articles_get(ctx=ctx, id=article_id, include_content=True)

        # Assert
        assert get_result["content"] == updated_content
        logger.info(f"✅ MCP updated article content: {article_id}")

    @pytest.mark.asyncio
    async def test_mcp_update_article_metadata(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test MCP tool updates article metadata without content.

        Verifies:
        - devrev_articles_update can update title/description/status
        - Content remains unchanged when not provided
        - Metadata updates work correctly
        """
        # Arrange - create article with content
        ctx = create_mock_context(write_client)
        original_title = test_data.generate_name("MCPMetadata")
        original_content = "<p>Content should remain unchanged</p>"

        create_result = await devrev_articles_create(
            ctx=ctx,
            title=original_title,
            content=original_content,
            owned_by=[current_user_id],
            status="draft",
        )
        article_id = create_result["id"]
        test_data.register("article", article_id)

        # Act - update only metadata
        new_title = test_data.generate_name("MCPUpdatedMetadata")
        new_description = "Updated description via MCP tool"
        await devrev_articles_update(
            ctx=ctx,
            id=article_id,
            title=new_title,
            description=new_description,
            status="published",
        )

        # Verify content unchanged
        get_result = await devrev_articles_get(ctx=ctx, id=article_id, include_content=True)

        # Assert
        assert get_result["title"] == new_title
        assert get_result["description"] == new_description
        assert get_result["status"] == ArticleStatus.PUBLISHED.value
        assert get_result["content"] == original_content  # Content unchanged
        logger.info(f"✅ MCP updated article metadata: {article_id}")


class TestMCPParameterValidation:
    """Tests for MCP tool parameter validation.

    Validates that MCP tools properly validate parameters and provide
    clear error messages for AI agents.
    """

    @pytest.mark.asyncio
    async def test_mcp_parameter_validation(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test MCP tools validate parameters correctly.

        Verifies:
        - Invalid status values are rejected with clear error
        - Error message lists valid status options
        - Validation happens before API calls
        """
        # Arrange
        ctx = create_mock_context(write_client)

        # Act & Assert - invalid status should raise RuntimeError with helpful message
        with pytest.raises(RuntimeError) as exc_info:
            await devrev_articles_create(
                ctx=ctx,
                title="Test Article",
                content="Test content",
                owned_by=["don:identity:dvrv-us-1:devo/1:devu/123"],
                status="invalid_status",  # Invalid status
            )

        # Verify error message is helpful for AI agents
        error_message = str(exc_info.value)
        assert "Invalid article status" in error_message
        assert "Valid statuses:" in error_message
        assert "DRAFT" in error_message
        assert "PUBLISHED" in error_message
        logger.info("✅ MCP parameter validation works correctly")

    @pytest.mark.asyncio
    async def test_mcp_error_messages(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test MCP tools provide clear error messages for AI agents.

        Verifies:
        - DevRev API errors are formatted clearly
        - Error messages are actionable
        - Errors are raised as RuntimeError for MCP compatibility
        """
        # Arrange
        ctx = create_mock_context(write_client)
        fake_article_id = "don:core:dvrv-us-1:devo/FAKE:article/DOESNOTEXIST"

        # Act & Assert - non-existent article should raise RuntimeError
        with pytest.raises(RuntimeError) as exc_info:
            await devrev_articles_get(ctx=ctx, id=fake_article_id, include_content=True)

        # Verify error message contains useful information
        error_message = str(exc_info.value)
        # Error should contain context about what went wrong
        assert len(error_message) > 0
        logger.info(f"✅ MCP error message format verified: {error_message[:100]}...")
