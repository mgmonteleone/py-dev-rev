#!/usr/bin/env python3
"""Debug script for article content creation and inspection.

Usage: python3 scripts/debug_articles.py
Requires: DEVREV_API_TOKEN environment variable
"""

import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from devrev.client import DevRevClient  # noqa: E402
from devrev.models.articles import (  # noqa: E402
    ArticlesGetRequest,
    ArticleStatus,
)
from devrev.models.artifacts import ArtifactGetRequest  # noqa: E402


def inspect_article(client: DevRevClient, article_id: str) -> None:
    """Inspect an article and its artifact content."""
    print("\n" + "=" * 60)
    print(f"INSPECTING ARTICLE: {article_id}")
    print("=" * 60)

    # Get article metadata
    article = client.articles.get(ArticlesGetRequest(id=article_id))
    print(f"\nTitle: {article.title}")
    print(f"Status: {article.status}")
    print(f"Description: {article.description}")
    print(f"Resource: {json.dumps(article.resource, indent=2, default=str)}")

    # Try to get content artifact
    if article.resource:
        # Check for artifacts array (how DevRev stores them)
        artifacts = article.resource.get("artifacts", [])
        if artifacts:
            for art_info in artifacts:
                art_id = art_info.get("id", "")
                file_info = art_info.get("file", {})
                print(f"\n--- Artifact: {art_id} ---")
                print(f"  File name: {file_info.get('name')}")
                print(f"  File type: {file_info.get('type')}")
                print(f"  File size: {file_info.get('size')}")

                # Get full artifact metadata
                try:
                    artifact = client.artifacts.get(ArtifactGetRequest(id=art_id))
                    print(f"  Artifact metadata - file_name: {artifact.file_name}")
                    print(f"  Artifact metadata - file_type: {artifact.file_type}")
                    print(f"  Artifact metadata - version: {artifact.version}")
                except Exception as e:
                    print(f"  Error getting artifact metadata: {e}")

                # Download content
                try:
                    content_bytes = client.artifacts.download(art_id)
                    content = content_bytes.decode("utf-8")
                    print(f"  Content length: {len(content)}")
                    print("  Content preview (first 2000 chars):")
                    print(f"  {content[:2000]}")
                    if len(content) > 2000:
                        print(f"  ... ({len(content) - 2000} more chars)")
                except Exception as e:
                    print(f"  Error downloading content: {e}")

        # Check for content_artifact reference (how our SDK stores them)
        content_artifact_id = article.resource.get("content_artifact")
        if content_artifact_id:
            print(f"\n--- Content Artifact (SDK style): {content_artifact_id} ---")
            try:
                content_bytes = client.artifacts.download(content_artifact_id)
                content = content_bytes.decode("utf-8")
                print(f"  Content length: {len(content)}")
                print(f"  Content preview: {content[:1000]}")
            except Exception as e:
                print(f"  Error: {e}")


def test_create_article(client: DevRevClient, owner_id: str) -> None:
    """Test creating an article with HTML content."""
    print("\n" + "=" * 60)
    print("TEST: Creating article with HTML content")
    print("=" * 60)

    html_content = """<h1>Test Article from py-dev-rev SDK</h1>
<p>This is a <strong>test article</strong> created via the py-dev-rev SDK.</p>
<h2>Features</h2>
<ul>
<li>Rich <em>formatted</em> text</li>
<li>Lists and headings</li>
<li>Code: <code>print("hello")</code></li>
</ul>
<p>Created at: 2026-03-07 for debugging purposes.</p>"""

    try:
        article = client.articles.create_with_content(
            title="SDK Test - Rich Content Article",
            content=html_content,
            owned_by=[owner_id],
            description="Test article created by py-dev-rev SDK debug script",
            status=ArticleStatus.DRAFT,
            content_format="text/html",
        )
        print(f"✅ Article created: {article.id} (display: {article.display_id})")
        print(f"  Title: {article.title}")
        print(f"  Resource: {json.dumps(article.resource, indent=2, default=str)}")

        # Now test get_with_content on the new article
        test_get_with_content(client, article.id)

        # Now test update_content
        test_update_content(client, article.id)

    except Exception as e:
        print(f"❌ Failed to create article: {e}")
        import traceback

        traceback.print_exc()


def test_get_with_content(client: DevRevClient, article_id: str) -> None:
    """Test the get_with_content method."""
    print("\n" + "=" * 60)
    print(f"TEST: get_with_content for {article_id}")
    print("=" * 60)

    try:
        result = client.articles.get_with_content(article_id)
        print("✅ get_with_content succeeded!")
        print(f"  Title: {result.article.title}")
        print(f"  Content format: {result.content_format}")
        print(f"  Content version: {result.content_version}")
        print(f"  Content length: {len(result.content)}")
        print(f"  Content preview: {result.content[:500]}")
    except Exception as e:
        print(f"❌ get_with_content failed: {e}")
        import traceback

        traceback.print_exc()


def test_update_content(client: DevRevClient, article_id: str) -> None:
    """Test updating article content."""
    print("\n" + "=" * 60)
    print(f"TEST: update_content for {article_id}")
    print("=" * 60)

    updated_html = """<h1>Updated Article</h1>
<p>This content was <strong>updated</strong> by the py-dev-rev SDK.</p>
<p>Updated at: 2026-03-07</p>"""

    try:
        article = client.articles.update_content(article_id, updated_html)
        print("✅ update_content succeeded!")
        print(f"  Title: {article.title}")
        print(f"  Resource: {json.dumps(article.resource, indent=2, default=str)}")

        # Verify by re-reading
        result = client.articles.get_with_content(article_id)
        print(f"  Verified content length: {len(result.content)}")
        print(f"  Verified content: {result.content[:300]}")
    except Exception as e:
        print(f"❌ update_content failed: {e}")
        import traceback

        traceback.print_exc()


def main() -> None:
    """Run article diagnostics."""
    token = os.environ.get("DEVREV_API_TOKEN")
    if not token:
        print("ERROR: DEVREV_API_TOKEN environment variable not set")
        sys.exit(1)

    client = DevRevClient()

    # 1. Inspect the known working article ART-2817
    art_2817_id = "don:core:dvrv-us-1:devo/11Ca9baGrM:article/2817"
    inspect_article(client, art_2817_id)

    # 2. Test get_with_content on ART-2817
    test_get_with_content(client, art_2817_id)

    # 3. Get owner ID for creating test articles
    owner_id = "don:identity:dvrv-us-1:devo/11Ca9baGrM:devu/4"  # MGM

    # 4. Try creating a new article with HTML content
    test_create_article(client, owner_id)

    # 5. Test get_with_content on the newly created article
    # (test_create_article already inspects it, but let's also test the unified method)


if __name__ == "__main__":
    main()
