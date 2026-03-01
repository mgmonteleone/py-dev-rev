"""Performance benchmarks for unified article/artifact methods.

This module contains performance benchmarks to validate that the unified
article management methods meet performance targets:

- create_with_content: <2s for typical 50KB article
- get_with_content: <1s for typical article
- Unified overhead: <200ms vs manual workflow

Run with: pytest tests/performance/ --benchmark-only
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock

import pytest

from devrev.models.articles import Article, ArticleStatus, ArticlesCreateResponse, ArticlesGetResponse
from devrev.models.artifacts import (
    Artifact,
    ArtifactGetResponse,
    ArtifactPrepareResponse,
    ArtifactVersionsPrepareResponse,
)
from devrev.services.articles import ArticlesService


@pytest.fixture
def mock_http_client():
    """Create a mocked HTTP client for performance testing."""
    return MagicMock()


@pytest.fixture
def mock_parent_client():
    """Mock parent DevRev client with artifacts service."""
    client = MagicMock()
    client.artifacts = MagicMock()
    return client


@pytest.fixture
def articles_service(mock_http_client, mock_parent_client):
    """Create ArticlesService with mocked dependencies."""
    service = ArticlesService(mock_http_client)
    service._parent_client = mock_parent_client
    return service


@pytest.fixture
def sample_content_small():
    """Generate 50KB of sample content."""
    return "Sample article content. " * 2500  # ~50KB


@pytest.fixture
def sample_content_medium():
    """Generate 500KB of sample content."""
    return "Sample article content. " * 25000  # ~500KB


@pytest.fixture
def sample_content_large():
    """Generate 5MB of sample content."""
    return "Sample article content. " * 250000  # ~5MB


def setup_create_mocks(
    service: ArticlesService,
    mock_http_client: MagicMock,
    artifact_id: str = "artifact-123",
):
    """Set up mocks for create_with_content workflow."""
    # Mock artifact preparation
    prepare_response = ArtifactPrepareResponse(
        id=artifact_id,
        url="https://s3.example.com/upload",
        form_data=[
            {"key": "key", "value": "upload-key"},
            {"key": "Content-Type", "value": "text/html"},
        ],
    )
    service._parent_client.artifacts.prepare = Mock(return_value=prepare_response)

    # Mock artifact upload
    service._parent_client.artifacts.upload = Mock(return_value=None)

    # Mock HTTP response for article creation
    http_response = Mock()
    http_response.status_code = 200
    http_response.content = b'{"article": {"id": "article-123", "title": "Test Article"}}'
    http_response.json.return_value = {
        "article": {
            "id": "article-123",
            "title": "Test Article",
            "resource": {"content_artifact": artifact_id},
            "owned_by": [{"id": "user-123"}],
        }
    }
    mock_http_client.post.return_value = http_response


def setup_get_mocks(
    service: ArticlesService,
    mock_http_client: MagicMock,
    content: str,
    artifact_id: str = "artifact-123",
):
    """Set up mocks for get_with_content workflow."""
    # Mock HTTP response for article retrieval
    http_response = Mock()
    http_response.status_code = 200
    http_response.content = b'{"article": {"id": "article-123"}}'
    http_response.json.return_value = {
        "article": {
            "id": "article-123",
            "title": "Test Article",
            "resource": {"content_artifact": artifact_id},
            "owned_by": [{"id": "user-123"}],
        }
    }
    mock_http_client.post.return_value = http_response

    # Mock artifact download
    service._parent_client.artifacts.download = Mock(return_value=content.encode("utf-8"))

    # Mock artifact metadata
    artifact = Artifact(
        id=artifact_id,
        file_type="text/html",
        version="1",
    )
    service._parent_client.artifacts.get = Mock(return_value=artifact)


def setup_update_mocks(
    service: ArticlesService,
    mock_http_client: MagicMock,
    artifact_id: str = "artifact-123",
):
    """Set up mocks for update_content workflow."""
    # Mock HTTP response for article retrieval
    http_response = Mock()
    http_response.status_code = 200
    http_response.content = b'{"article": {"id": "article-123"}}'
    http_response.json.return_value = {
        "article": {
            "id": "article-123",
            "title": "Test Article",
            "resource": {"content_artifact": artifact_id},
            "owned_by": [{"id": "user-123"}],
        }
    }
    mock_http_client.post.return_value = http_response

    # Mock version preparation
    version_response = ArtifactVersionsPrepareResponse(
        id=artifact_id,
        url="https://s3.example.com/upload",
        form_data=[
            {"key": "key", "value": "upload-key"},
        ],
    )
    service._parent_client.artifacts.prepare_version = Mock(return_value=version_response)

    # Mock artifact upload
    service._parent_client.artifacts.upload = Mock(return_value=None)


# ============================================================================
# Benchmarks: create_with_content
# ============================================================================


def test_benchmark_create_with_content_small(
    benchmark, articles_service, mock_http_client, sample_content_small
):
    """Benchmark create_with_content with 50KB article.

    Target: <2s for typical 50KB article
    """
    setup_create_mocks(articles_service, mock_http_client)

    def create_article():
        return articles_service.create_with_content(
            title="Performance Test Article",
            content=sample_content_small,
            owned_by=["user-123"],
            content_format="text/html",
        )

    result = benchmark(create_article)

    # Verify result
    assert result.id == "article-123"

    # Verify performance target (mean is in seconds)
    stats = benchmark.stats.stats
    mean_seconds = stats.mean
    assert mean_seconds < 2.0, f"create_with_content (50KB) took {mean_seconds:.4f}s, target: <2s"


def test_benchmark_create_with_content_medium(
    benchmark, articles_service, mock_http_client, sample_content_medium
):
    """Benchmark create_with_content with 500KB article.

    Target: <3s for 500KB article
    """
    setup_create_mocks(articles_service, mock_http_client, artifact_id="artifact-medium")

    def create_article():
        return articles_service.create_with_content(
            title="Medium Performance Test Article",
            content=sample_content_medium,
            owned_by=["user-123"],
            content_format="text/html",
        )

    result = benchmark(create_article)

    # Verify result
    assert result.id == "article-123"

    # Verify performance target (mean is in seconds)
    stats = benchmark.stats.stats
    mean_seconds = stats.mean
    assert mean_seconds < 3.0, f"create_with_content (500KB) took {mean_seconds:.4f}s, target: <3s"


def test_benchmark_create_with_content_large(
    benchmark, articles_service, mock_http_client, sample_content_large
):
    """Benchmark create_with_content with 5MB article.

    Target: <5s for 5MB article
    """
    setup_create_mocks(articles_service, mock_http_client, artifact_id="artifact-large")

    def create_article():
        return articles_service.create_with_content(
            title="Large Performance Test Article",
            content=sample_content_large,
            owned_by=["user-123"],
            content_format="text/html",
        )

    result = benchmark(create_article)

    # Verify result
    assert result.id == "article-123"

    # Verify performance target (mean is in seconds)
    stats = benchmark.stats.stats
    mean_seconds = stats.mean
    assert mean_seconds < 5.0, f"create_with_content (5MB) took {mean_seconds:.4f}s, target: <5s"


# ============================================================================
# Benchmarks: get_with_content
# ============================================================================


def test_benchmark_get_with_content_cached(
    benchmark, articles_service, mock_http_client, sample_content_small
):
    """Benchmark get_with_content with cached content.

    Target: <1s for cached content

    Note: This simulates cached behavior by using simple mocks that return
    immediately without network delays.
    """
    setup_get_mocks(articles_service, mock_http_client, sample_content_small)

    def get_article():
        return articles_service.get_with_content("article-123")

    result = benchmark(get_article)

    # Verify result
    assert result.article.id == "article-123"
    assert len(result.content) > 0

    # Verify performance target (mean is in seconds)
    stats = benchmark.stats.stats
    mean_seconds = stats.mean
    assert mean_seconds < 1.0, f"get_with_content (cached) took {mean_seconds:.4f}s, target: <1s"


def test_benchmark_get_with_content_uncached(
    benchmark, articles_service, mock_http_client, sample_content_small
):
    """Benchmark get_with_content with uncached content.

    Target: <2s for uncached content

    Note: This simulates uncached behavior by adding a small delay to mocks
    to represent network overhead.
    """
    import time

    # Add slight delay to simulate network overhead
    original_download = Mock(return_value=sample_content_small.encode("utf-8"))

    def delayed_download(*args, **kwargs):
        time.sleep(0.1)  # Simulate 100ms network delay
        return original_download(*args, **kwargs)

    setup_get_mocks(articles_service, mock_http_client, sample_content_small)
    articles_service._parent_client.artifacts.download = delayed_download

    def get_article():
        return articles_service.get_with_content("article-123")

    result = benchmark(get_article)

    # Verify result
    assert result.article.id == "article-123"

    # Verify performance target (mean is in seconds)
    stats = benchmark.stats.stats
    mean_seconds = stats.mean
    assert mean_seconds < 2.0, f"get_with_content (uncached) took {mean_seconds:.4f}s, target: <2s"


# ============================================================================
# Benchmarks: update_content
# ============================================================================


def test_benchmark_update_content(
    benchmark, articles_service, mock_http_client, sample_content_small
):
    """Benchmark update_content operation.

    Target: <2s for content update
    """
    setup_update_mocks(articles_service, mock_http_client)

    def update_article():
        return articles_service.update_content(
            "article-123",
            sample_content_small,
            content_format="text/html",
        )

    result = benchmark(update_article)

    # Verify result
    assert result.id == "article-123"

    # Verify performance target (mean is in seconds)
    stats = benchmark.stats.stats
    mean_seconds = stats.mean
    assert mean_seconds < 2.0, f"update_content took {mean_seconds:.4f}s, target: <2s"


# ============================================================================
# Benchmarks: Unified vs Manual Overhead
# ============================================================================


def test_benchmark_unified_vs_manual(
    benchmark, articles_service, mock_http_client, sample_content_small
):
    """Benchmark overhead of unified method vs manual workflow.

    Target: Unified should add <200ms overhead vs manual workflow

    This benchmark compares:
    1. Manual workflow: prepare -> upload -> create (3 separate calls)
    2. Unified workflow: create_with_content (single call, 3 steps internally)
    """
    import time

    # Benchmark manual workflow
    manual_times = []
    for _ in range(10):
        start = time.perf_counter()

        # Manual workflow (3 separate calls)
        prepare_resp = articles_service._parent_client.artifacts.prepare(Mock())
        articles_service._parent_client.artifacts.upload(prepare_resp, sample_content_small)

        # Mock HTTP response for manual create
        http_response = Mock()
        http_response.status_code = 200
        http_response.content = b'{"article": {"id": "article-manual"}}'
        http_response.json.return_value = {
            "article": {
                "id": "article-manual",
                "title": "Manual Test",
                "resource": {"content_artifact": "artifact-123"},
                "owned_by": [{"id": "user-123"}],
            }
        }
        mock_http_client.post.return_value = http_response

        from devrev.models.articles import ArticlesCreateRequest
        articles_service.create(
            ArticlesCreateRequest(
                title="Manual Test",
                owned_by=["user-123"],
                resource={"content_artifact": "artifact-123"},
            )
        )

        manual_times.append(time.perf_counter() - start)

    manual_mean = sum(manual_times) / len(manual_times)

    # Benchmark unified workflow
    setup_create_mocks(articles_service, mock_http_client)

    def unified_workflow():
        return articles_service.create_with_content(
            title="Unified Test",
            content=sample_content_small,
            owned_by=["user-123"],
            content_format="text/html",
        )

    result = benchmark(unified_workflow)
    unified_mean = benchmark.stats.stats.mean

    # Calculate overhead
    overhead = unified_mean - manual_mean

    # Verify result
    assert result.id == "article-123"

    # Verify performance target
    assert overhead < 0.2, (
        f"Unified overhead is {overhead*1000:.0f}ms, target: <200ms "
        f"(manual: {manual_mean*1000:.0f}ms, unified: {unified_mean*1000:.0f}ms)"
    )


# ============================================================================
# Benchmarks: Bulk Operations
# ============================================================================


def test_benchmark_bulk_operations(
    benchmark, articles_service, mock_http_client, sample_content_small
):
    """Benchmark bulk article creation.

    Target: 10 articles creation in <20s
    """
    setup_create_mocks(articles_service, mock_http_client)

    def create_bulk_articles():
        articles = []
        for i in range(10):
            article = articles_service.create_with_content(
                title=f"Bulk Test Article {i}",
                content=sample_content_small,
                owned_by=["user-123"],
                content_format="text/html",
            )
            articles.append(article)
        return articles

    results = benchmark(create_bulk_articles)

    # Verify results
    assert len(results) == 10
    for article in results:
        assert article.id == "article-123"

    # Verify performance target (mean is in seconds)
    stats = benchmark.stats.stats
    mean_seconds = stats.mean
    assert mean_seconds < 20.0, f"Bulk creation (10 articles) took {mean_seconds:.4f}s, target: <20s"
