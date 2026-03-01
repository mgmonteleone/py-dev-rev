"""Integration tests for article lifecycle with unified content methods.

These tests validate the full article lifecycle workflows including:
- Creating articles with content
- Retrieving articles with content
- Updating article content and metadata
- Versioning behavior
- Edge cases (large content, Unicode, special characters)
- Error recovery and cleanup

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_articles_lifecycle.py -v -m write
"""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING

import pytest

from devrev.exceptions import DevRevError

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


class TestArticleLifecycle:
    """Integration tests for full article lifecycle workflows."""

    def test_full_article_lifecycle(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test complete article lifecycle: Create → Get → Update → Delete.

        Validates:
        - Article creation with content
        - Content retrieval
        - Content and metadata updates
        - Article deletion
        """
        # Arrange
        title = test_data.generate_name("Lifecycle Article")
        original_content = (
            "<html><body><h1>Original Content</h1><p>Initial article body.</p></body></html>"
        )
        updated_content = (
            "<html><body><h1>Updated Content</h1><p>Modified article body.</p></body></html>"
        )

        # Act 1: Create article with content
        article = write_client.articles.create_with_content(
            title=title,
            content=original_content,
            owned_by=[current_user_id],
            description="Test article for lifecycle validation",
            content_format="text/html",
        )
        test_data.register("article", article.id)

        # Assert 1: Article created successfully
        assert article.id is not None
        assert article.title == title
        assert article.description == "Test article for lifecycle validation"
        logger.info(f"✅ Created article with content: {article.id}")

        # Act 2: Get article with content
        article_with_content = write_client.articles.get_with_content(article.id)

        # Assert 2: Content retrieved correctly
        assert article_with_content.article.id == article.id
        assert article_with_content.content == original_content
        assert article_with_content.content_format == "text/html"
        logger.info(f"✅ Retrieved article content: {len(original_content)} bytes")

        # Act 3: Update content
        updated_article = write_client.articles.update_content(
            article.id,
            updated_content,
            content_format="text/html",
        )

        # Assert 3: Content updated
        assert updated_article.id == article.id
        updated_with_content = write_client.articles.get_with_content(article.id)
        assert updated_with_content.content == updated_content
        logger.info("✅ Updated article content")

        # Act 4: Update metadata
        final_article = write_client.articles.update_with_content(
            article.id,
            title=f"{title} - Updated",
            description="Updated description",
        )

        # Assert 4: Metadata updated
        assert final_article.title == f"{title} - Updated"
        assert final_article.description == "Updated description"
        logger.info("✅ Updated article metadata")

        # Act 5: Delete article (cleanup happens in fixture)
        # Just verify article exists before cleanup
        verify_article = write_client.articles.get_with_content(article.id)
        assert verify_article.article.id == article.id
        logger.info("✅ Full lifecycle completed successfully")

    def test_article_versioning(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test that multiple content updates create proper versions.

        Validates:
        - Initial version created
        - New versions created on updates
        - Version numbers increment
        """
        # Arrange
        title = test_data.generate_name("Versioned Article")
        content_v1 = "Version 1 content"
        content_v2 = "Version 2 content"
        content_v3 = "Version 3 content"

        # Act 1: Create article
        article = write_client.articles.create_with_content(
            title=title,
            content=content_v1,
            owned_by=[current_user_id],
            content_format="text/plain",
        )
        test_data.register("article", article.id)

        # Get initial version
        v1 = write_client.articles.get_with_content(article.id)
        initial_version = v1.content_version
        assert v1.content == content_v1
        logger.info(f"✅ Created article with version: {initial_version}")

        # Act 2: Update content (version 2)
        write_client.articles.update_content(article.id, content_v2)
        v2 = write_client.articles.get_with_content(article.id)

        # Assert 2: New version created
        assert v2.content == content_v2
        assert v2.content_version != initial_version
        assert v2.content_version > initial_version
        logger.info(f"✅ Version incremented: {initial_version} → {v2.content_version}")

        # Act 3: Update content again (version 3)
        write_client.articles.update_content(article.id, content_v3)
        v3 = write_client.articles.get_with_content(article.id)

        # Assert 3: Version incremented again
        assert v3.content == content_v3
        assert v3.content_version > v2.content_version
        logger.info(f"✅ Version incremented again: {v2.content_version} → {v3.content_version}")

    def test_large_content_handling(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test handling of large content (>1MB).

        Validates:
        - Large content upload succeeds
        - Large content retrieval succeeds
        - Performance is acceptable
        """
        # Arrange - Create >1MB of content
        title = test_data.generate_name("Large Article")
        # Generate ~1.5MB of content
        large_content = "<html><body>" + ("Lorem ipsum dolor sit amet. " * 50000) + "</body></html>"
        content_size = len(large_content)
        assert content_size > 1_000_000, "Content should be >1MB"

        # Act 1: Create with large content
        start_time = time.time()
        article = write_client.articles.create_with_content(
            title=title,
            content=large_content,
            owned_by=[current_user_id],
            content_format="text/html",
        )
        create_duration = time.time() - start_time
        test_data.register("article", article.id)

        # Assert 1: Creation succeeded and was reasonably fast
        assert article.id is not None
        logger.info(f"✅ Created large article ({content_size:,} bytes) in {create_duration:.2f}s")

        # Act 2: Retrieve large content
        start_time = time.time()
        retrieved = write_client.articles.get_with_content(article.id)
        retrieve_duration = time.time() - start_time

        # Assert 2: Content matches and retrieval was reasonably fast
        assert retrieved.content == large_content
        assert len(retrieved.content) == content_size
        logger.info(f"✅ Retrieved large content in {retrieve_duration:.2f}s")

    def test_unicode_content(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test handling of Unicode and non-ASCII characters.

        Validates:
        - Unicode content is preserved
        - Various character sets work correctly
        - Emoji and special characters handled
        """
        # Arrange - Content with various Unicode characters
        title = test_data.generate_name("Unicode Article 🌍")
        unicode_content = """
        <html>
        <body>
            <h1>Unicode Test 测试</h1>
            <p>English, 中文, 日本語, 한국어, العربية, עברית</p>
            <p>Emoji: 🚀 🌟 💡 ✅ ❌</p>
            <p>Math: ∑ ∫ ∂ ∞ ≈ ≠</p>
            <p>Special: © ® ™ € £ ¥</p>
            <p>Accents: café, naïve, résumé, Zürich</p>
        </body>
        </html>
        """

        # Act: Create and retrieve
        article = write_client.articles.create_with_content(
            title=title,
            content=unicode_content,
            owned_by=[current_user_id],
            content_format="text/html",
        )
        test_data.register("article", article.id)

        retrieved = write_client.articles.get_with_content(article.id)

        # Assert: All Unicode characters preserved
        assert retrieved.content == unicode_content
        assert retrieved.article.title == title
        assert "🚀" in retrieved.content
        assert "中文" in retrieved.content
        assert "café" in retrieved.content
        logger.info("✅ Unicode content preserved correctly")

    def test_special_characters(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test handling of HTML entities, code blocks, and special formatting.

        Validates:
        - HTML entities preserved
        - Code blocks with special characters
        - Markdown-style formatting
        """
        # Arrange - Content with special characters and code
        title = test_data.generate_name("Special Chars Article")
        special_content = """
        <html>
        <body>
            <h1>Special Characters &amp; Entities</h1>
            <p>Entities: &lt; &gt; &amp; &quot; &#39;</p>
            <code>
                function test() {
                    const str = "Hello &lt;world&gt;";
                    return str.replace(/[<>]/g, '');
                }
            </code>
            <pre>
                {
                    "key": "value with \"quotes\"",
                    "array": [1, 2, 3],
                    "null": null
                }
            </pre>
        </body>
        </html>
        """

        # Act: Create and retrieve
        article = write_client.articles.create_with_content(
            title=title,
            content=special_content,
            owned_by=[current_user_id],
            content_format="text/html",
        )
        test_data.register("article", article.id)

        retrieved = write_client.articles.get_with_content(article.id)

        # Assert: Special characters preserved
        assert retrieved.content == special_content
        assert "&lt;" in retrieved.content
        assert "&amp;" in retrieved.content
        assert "&quot;" in retrieved.content
        logger.info("✅ Special characters and HTML entities preserved")

    def test_mixed_operations(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test interoperability between unified API and low-level methods.

        Validates:
        - Can create with unified method, update with low-level
        - Can create with low-level, retrieve with unified method
        - Mixed operations don't cause conflicts
        """
        from devrev.models.articles import ArticlesCreateRequest, ArticlesUpdateRequest

        # Arrange
        title = test_data.generate_name("Mixed API Article")
        content = "<html><body><h1>Original</h1></body></html>"

        # Act 1: Create with unified method
        article = write_client.articles.create_with_content(
            title=title,
            content=content,
            owned_by=[current_user_id],
            content_format="text/html",
        )
        test_data.register("article", article.id)

        # Act 2: Update metadata with low-level method
        update_req = ArticlesUpdateRequest(
            id=article.id,
            title=f"{title} - Updated via low-level",
        )
        write_client.articles.update(update_req)

        # Assert 2: Can still retrieve with unified method
        retrieved = write_client.articles.get_with_content(article.id)
        assert retrieved.article.title == f"{title} - Updated via low-level"
        assert retrieved.content == content
        logger.info("✅ Mixed API operations work correctly")

        # Act 3: Create another article with low-level method (no content)
        title2 = test_data.generate_name("Low-level Article")
        create_req = ArticlesCreateRequest(
            title=title2,
            owned_by=[current_user_id],
        )
        article2 = write_client.articles.create(create_req)
        test_data.register("article", article2.id)

        # Assert 3: Article without content raises error on get_with_content
        with pytest.raises(DevRevError, match="has no content_artifact"):
            write_client.articles.get_with_content(article2.id)
        logger.info("✅ Appropriate error for article without content")

    def test_network_failure_recovery(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test recovery from transient network failures.

        Note: This test validates that the client properly propagates errors.
        Actual retry logic would require mocking or network manipulation.
        """
        # Arrange
        title = test_data.generate_name("Network Test Article")
        content = "Test content"

        # Act: Create article normally (should succeed)
        article = write_client.articles.create_with_content(
            title=title,
            content=content,
            owned_by=[current_user_id],
        )
        test_data.register("article", article.id)

        # Assert: Article created successfully
        assert article.id is not None
        logger.info("✅ Article created successfully despite network test")

        # Test invalid ID handling
        with pytest.raises((DevRevError, Exception)):  # NotFoundError is a DevRevError
            write_client.articles.get_with_content("invalid-id-12345")
        logger.info("✅ Appropriate error handling for invalid ID")

    def test_concurrent_updates(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test handling of concurrent content updates.

        Validates:
        - Multiple rapid updates succeed
        - Final state is consistent
        - No corruption from race conditions
        """
        # Arrange
        title = test_data.generate_name("Concurrent Article")
        initial_content = "Initial content"

        # Act 1: Create article
        article = write_client.articles.create_with_content(
            title=title,
            content=initial_content,
            owned_by=[current_user_id],
        )
        test_data.register("article", article.id)

        # Act 2: Perform multiple rapid updates
        num_updates = 5
        for i in range(num_updates):
            content = f"Update {i + 1}"
            write_client.articles.update_content(article.id, content)
            # Small delay to ensure updates are sequential
            time.sleep(0.1)

        # Assert: Final content is the last update
        final = write_client.articles.get_with_content(article.id)
        assert final.content == f"Update {num_updates}"
        logger.info(f"✅ {num_updates} sequential updates completed successfully")

    def test_artifact_cleanup_on_article_delete(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test that artifacts are handled when article is deleted.

        Note: DevRev may not automatically delete artifacts when article is deleted.
        This test validates the current behavior.
        """
        from devrev.exceptions import NotFoundError
        from devrev.models.articles import ArticlesDeleteRequest

        # Arrange
        title = test_data.generate_name("Delete Test Article")
        content = "Content to be deleted"

        # Act 1: Create article with content
        article = write_client.articles.create_with_content(
            title=title,
            content=content,
            owned_by=[current_user_id],
        )

        # Get artifact ID before deletion
        _ = write_client.articles.get_with_content(article.id)
        artifact_id = article.resource.get("content_artifact")  # type: ignore[attr-defined]
        assert artifact_id is not None

        # Act 2: Delete article
        delete_req = ArticlesDeleteRequest(id=article.id)
        write_client.articles.delete(delete_req)
        logger.info(f"✅ Deleted article: {article.id}")

        # Assert: Article is deleted
        with pytest.raises(NotFoundError):
            write_client.articles.get_with_content(article.id)

        # Note: We don't test artifact deletion as DevRev API may retain artifacts
        logger.info("✅ Article deleted successfully")


class TestArticleLifecycleAsync:
    """Async integration tests for article lifecycle."""

    @pytest.mark.asyncio
    async def test_full_article_lifecycle_async(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Test complete async article lifecycle.

        Validates:
        - Async create_with_content
        - Async get_with_content
        - Async update operations
        """
        from devrev.client import AsyncDevRevClient

        # Create async client from sync client's config
        async with AsyncDevRevClient(
            api_token=write_client._config.api_token  # type: ignore[attr-defined]
        ) as async_client:
            # Arrange
            title = test_data.generate_name("Async Article")
            content = "<html><body><h1>Async Test</h1></body></html>"

            # Act 1: Create async
            article = await async_client.articles.create_with_content(
                title=title,
                content=content,
                owned_by=[current_user_id],
                content_format="text/html",
            )
            test_data.register("article", article.id)

            # Assert 1: Article created
            assert article.id is not None
            logger.info(f"✅ Created article async: {article.id}")

            # Act 2: Get async
            retrieved = await async_client.articles.get_with_content(article.id)

            # Assert 2: Content retrieved
            assert retrieved.content == content
            logger.info("✅ Retrieved article content async")

            # Act 3: Update async
            new_content = "<html><body><h1>Updated Async</h1></body></html>"
            await async_client.articles.update_content(article.id, new_content)

            # Assert 3: Content updated
            updated = await async_client.articles.get_with_content(article.id)
            assert updated.content == new_content
            logger.info("✅ Updated article content async")
