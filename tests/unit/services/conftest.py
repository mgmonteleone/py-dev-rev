"""Shared fixtures for service unit tests."""

from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from devrev.utils.http import AsyncHTTPClient, HTTPClient


@pytest.fixture
def mock_http_client() -> Generator[MagicMock, None, None]:
    """Create a mock HTTP client for testing sync services."""
    mock = MagicMock(spec=HTTPClient)
    yield mock


@pytest.fixture
def mock_async_http_client() -> Generator[AsyncMock, None, None]:
    """Create a mock async HTTP client for testing async services."""
    mock = AsyncMock(spec=AsyncHTTPClient)
    yield mock


def create_mock_response(data: dict[str, Any], status_code: int = 200) -> MagicMock:
    """Create a mock HTTP response.

    Args:
        data: JSON response data
        status_code: HTTP status code

    Returns:
        Mock response object
    """
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.json.return_value = data
    return response


# Conversation fixtures
@pytest.fixture
def sample_conversation_data() -> dict[str, Any]:
    """Sample conversation data."""
    return {
        "id": "don:core:conversation:123",
        "display_id": "CONV-123",
        "title": "Test Conversation",
        "description": "Test description",
        "stage": "open",
    }


# Article fixtures
@pytest.fixture
def sample_article_data() -> dict[str, Any]:
    """Sample article data."""
    return {
        "id": "don:core:article:123",
        "display_id": "ART-123",
        "title": "Test Article",
        "content": "# Test Content",
        "status": "published",
    }


# Part fixtures
@pytest.fixture
def sample_part_data() -> dict[str, Any]:
    """Sample part data."""
    return {
        "id": "don:core:part:123",
        "display_id": "PART-123",
        "name": "Test Part",
        "description": "Test part description",
        "type": "product",
    }


# Timeline entry fixtures
@pytest.fixture
def sample_timeline_entry_data() -> dict[str, Any]:
    """Sample timeline entry data."""
    return {
        "id": "don:core:timeline_entry:123",
        "object": "don:core:issue:456",
        "entry_type": "timeline_comment",
        "body": "Test comment",
    }


# Code change fixtures
@pytest.fixture
def sample_code_change_data() -> dict[str, Any]:
    """Sample code change data."""
    return {
        "id": "don:core:code_change:123",
        "display_id": "CC-123",
        "title": "Test Code Change",
        "state": "open",
    }


# SLA fixtures
@pytest.fixture
def sample_sla_data() -> dict[str, Any]:
    """Sample SLA data."""
    return {
        "id": "don:core:sla:123",
        "display_id": "SLA-123",
        "name": "Test SLA",
        "description": "Test SLA description",
    }


# Webhook fixtures
@pytest.fixture
def sample_webhook_data() -> dict[str, Any]:
    """Sample webhook data."""
    return {
        "id": "don:core:webhook:123",
        "url": "https://example.com/webhook",
        "event_types": ["work.created", "work.updated"],
    }


# Group fixtures
@pytest.fixture
def sample_group_data() -> dict[str, Any]:
    """Sample group data."""
    return {
        "id": "don:core:group:123",
        "name": "Test Group",
        "description": "Test group description",
    }


# Tag fixtures
@pytest.fixture
def sample_tag_data() -> dict[str, Any]:
    """Sample tag data."""
    return {
        "id": "don:core:tag:123",
        "name": "test-tag",
    }


# Link fixtures
@pytest.fixture
def sample_link_data() -> dict[str, Any]:
    """Sample link data."""
    return {
        "id": "don:core:link:123",
        "source": "don:core:issue:456",
        "target": "don:core:issue:789",
        "link_type": "is_blocked_by",
    }
