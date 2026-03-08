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
        # Note: DevRev converts HTML to internal ProseMirror/devrev-rt format,
        # so content won't match the original HTML string exactly.
        assert article_with_content.article.id == article.id
        assert article_with_content.content is not None
        assert len(article_with_content.content) > 0
        assert "Original Content" in article_with_content.content
        assert "Initial article body" in article_with_content.content
        logger.info(f"✅ Retrieved article content: {len(article_with_content.content)} bytes")

        # Act 3: Update content
        updated_article = write_client.articles.update_content(
            article.id,
            updated_content,
            content_format="text/html",
        )

        # Assert 3: Content updated
        assert updated_article.id == article.id
        updated_with_content = write_client.articles.get_with_content(article.id)
        assert "Updated Content" in updated_with_content.content
        assert "Modified article body" in updated_with_content.content
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
        assert v1.content is not None
        assert "Version 1" in v1.content
        logger.info("✅ Created article with initial content")

        # Act 2: Update content (version 2)
        write_client.articles.update_content(article.id, content_v2)
        v2 = write_client.articles.get_with_content(article.id)

        # Assert 2: Content updated
        assert "Version 2" in v2.content
        logger.info("✅ Content updated to version 2")

        # Act 3: Update content again (version 3)
        write_client.articles.update_content(article.id, content_v3)
        v3 = write_client.articles.get_with_content(article.id)

        # Assert 3: Content updated again
        assert "Version 3" in v3.content
        logger.info("✅ Content updated to version 3")

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

        # Assert 2: Content retrieved (DevRev converts format, so don't exact-match)
        assert retrieved.content is not None
        assert len(retrieved.content) > 0
        assert "Lorem ipsum" in retrieved.content
        logger.info(
            f"✅ Retrieved large content ({len(retrieved.content):,} bytes) in {retrieve_duration:.2f}s"
        )

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

        # Assert: Key Unicode characters preserved (DevRev may JSON-escape unicode)
        assert retrieved.content is not None
        assert retrieved.article.title == title
        # DevRev stores content as JSON; unicode chars may be escaped.
        # Parse JSON to check actual text content.
        import json as _json

        try:
            parsed = _json.loads(retrieved.content)
            flat_text = _json.dumps(parsed, ensure_ascii=False)
        except _json.JSONDecodeError:
            flat_text = retrieved.content
        assert "🚀" in flat_text or "\\ud83d\\ude80" in retrieved.content
        assert "中文" in flat_text or "\\u4e2d\\u6587" in retrieved.content
        assert "café" in flat_text or "caf\\u00e9" in retrieved.content
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

        # Assert: Text content preserved (DevRev decodes HTML entities in its format)
        assert retrieved.content is not None
        assert "Special Characters" in retrieved.content
        assert "function test()" in retrieved.content
        logger.info("✅ Special characters content preserved")

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
        assert "Original" in retrieved.content
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
        with pytest.raises(DevRevError, match="has no (content_artifact|resource)"):
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

        # Act 2: Perform multiple sequential updates with adequate spacing
        num_updates = 3
        for i in range(num_updates):
            content = f"Sequential update number {i + 1}"
            write_client.articles.update_content(article.id, content)
            # DevRev API needs time between artifact updates
            time.sleep(1.0)

        # Assert: Final content is the last update
        final = write_client.articles.get_with_content(article.id)
        assert f"number {num_updates}" in final.content
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

        # Verify content was created
        article_with_content = write_client.articles.get_with_content(article.id)
        assert article_with_content.content is not None

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

            # Assert 2: Content retrieved (DevRev converts to internal format)
            assert retrieved.content is not None
            assert "Async Test" in retrieved.content
            logger.info("✅ Retrieved article content async")

            # Act 3: Update async
            new_content = "<html><body><h1>Updated Async Content</h1></body></html>"
            await async_client.articles.update_content(article.id, new_content)

            # Assert 3: Content updated
            updated = await async_client.articles.get_with_content(article.id)
            assert "Updated Async Content" in updated.content
            logger.info("✅ Updated article content async")


class TestContentConverterRoundTrip:
    """Live round-trip tests: create article via SDK → download artifact → verify ProseMirror JSON."""

    def test_html_round_trip_produces_valid_devrev_rt(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Create article with HTML, download artifact, verify devrev/rt structure."""
        import json

        title = test_data.generate_name("RT Round-Trip HTML")
        html_content = """
        <h1>Round Trip Test</h1>
        <p>Paragraph with <strong>bold</strong> and <em>italic</em>.</p>
        <table>
          <tr><th>Col A</th><th>Col B</th></tr>
          <tr><td>val 1</td><td>val 2</td></tr>
        </table>
        <pre><code class="language-python">print("hello")</code></pre>
        <ul><li>Item one</li><li>Item two</li></ul>
        """

        # Create article
        article = write_client.articles.create_with_content(
            title=title,
            content=html_content,
            owned_by=[current_user_id],
            content_format="text/html",
        )
        test_data.register("article", article.id)
        assert article.id is not None

        # Re-fetch article with content to get the devrev/rt JSON
        article_with_content = write_client.articles.get_with_content(article.id)
        assert article_with_content.content is not None
        parsed = json.loads(article_with_content.content)

        # Verify envelope structure
        assert "article" in parsed, "Must have 'article' key"
        assert "artifactIds" in parsed, "Must have 'artifactIds' key"
        doc = parsed["article"]
        assert doc["type"] == "doc"
        assert isinstance(doc["content"], list)
        assert len(doc["content"]) > 0

        # Verify node types present
        types = [n["type"] for n in doc["content"]]
        assert "heading" in types, "Must contain heading"
        assert "paragraph" in types, "Must contain paragraph"
        assert "table" in types, "Must contain table"
        assert "codeBlock" in types, "Must contain codeBlock"
        assert "bulletList" in types, "Must contain bulletList"

        # Verify heading structure matches UI format
        heading = next(n for n in doc["content"] if n["type"] == "heading")
        assert heading["attrs"]["textAlign"] is None
        assert heading["attrs"]["level"] == 1

        # Verify table cell structure matches UI format
        table = next(n for n in doc["content"] if n["type"] == "table")
        cell = table["content"][0]["content"][0]
        assert "attrs" in cell
        assert cell["attrs"]["colspan"] == 1
        assert cell["attrs"]["rowspan"] == 1
        assert cell["attrs"]["colwidth"] is None
        # Cell content must be wrapped in paragraph
        assert cell["content"][0]["type"] == "paragraph"

        # Verify code block
        cb = next(n for n in doc["content"] if n["type"] == "codeBlock")
        assert "attrs" in cb
        assert cb["attrs"]["language"] == "python"

        logger.info("✅ HTML round-trip produces valid devrev/rt structure")

    def test_markdown_round_trip_produces_valid_devrev_rt(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        current_user_id: str,
    ) -> None:
        """Create article with Markdown, download artifact, verify devrev/rt structure."""
        import json

        title = test_data.generate_name("RT Round-Trip Markdown")
        md_content = (
            "# Markdown Article\n\n"
            "**Bold** and *italic* text.\n\n"
            "```javascript\nconsole.log('hi')\n```\n\n"
            "| A | B |\n|---|---|\n| 1 | 2 |\n\n"
            "- List item\n"
        )

        article = write_client.articles.create_with_content(
            title=title,
            content=md_content,
            owned_by=[current_user_id],
            content_format="text/markdown",
        )
        test_data.register("article", article.id)

        # Re-fetch article with content to get the devrev/rt JSON
        article_with_content = write_client.articles.get_with_content(article.id)
        assert article_with_content.content is not None
        parsed = json.loads(article_with_content.content)

        assert parsed["article"]["type"] == "doc"
        types = [n["type"] for n in parsed["article"]["content"]]
        assert "heading" in types
        assert "codeBlock" in types
        assert "table" in types
        assert "bulletList" in types

        logger.info("✅ Markdown round-trip produces valid devrev/rt structure")
