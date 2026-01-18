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


# Incident fixtures
@pytest.fixture
def sample_incident_data() -> dict[str, Any]:
    """Sample incident data matching actual API response structure.

    The API returns complex objects for stage and severity, not simple strings.
    """
    return {
        "id": "don:core:incident:123",
        "display_id": "INC-123",
        "title": "Test Incident",
        "body": "Test incident description",
        "stage": {
            "stage": {"id": "don:core:custom_stage:123", "name": "Acknowledged"},
            "state": {"id": "don:core:custom_state:456", "name": "Active", "is_final": False},
        },
        "severity": {"id": 1, "label": "Sev1", "ordinal": 1},
    }


# Engagement fixtures
@pytest.fixture
def sample_engagement_data() -> dict[str, Any]:
    """Sample engagement data."""
    return {
        "id": "don:core:engagement:123",
        "display_id": "ENG-123",
        "title": "Test Engagement",
        "engagement_type": "meeting",
        "description": "Test engagement description",
        "members": ["don:identity:user:456"],
        "parent": None,
        "scheduled_date": "2024-01-15T10:00:00Z",
        "tags": ["don:core:tag:789"],
    }


# Brand fixtures
@pytest.fixture
def sample_brand_data() -> dict[str, Any]:
    """Sample brand data."""
    return {
        "id": "don:core:brand:123",
        "display_id": "BRAND-123",
        "name": "Test Brand",
        "description": "Test brand description",
        "logo_url": "https://example.com/logo.png",
    }


# Search fixtures
@pytest.fixture
def sample_search_response_data() -> dict[str, Any]:
    """Sample search response data."""
    return {
        "results": [
            {
                "id": "don:core:work:123",
                "type": "work",
                "score": 0.95,
                "highlights": ["priority:p0", "status:open"],
                "work_summary": {
                    "id": "don:core:work:123",
                    "display_id": "ISS-123",
                    "title": "Critical bug in authentication",
                    "type": "issue",
                    "stage": "in_progress",
                    "priority": "p0",
                },
            },
            {
                "id": "don:core:article:456",
                "type": "article",
                "score": 0.87,
                "highlights": ["authentication", "login"],
                "article_summary": {
                    "id": "don:core:article:456",
                    "title": "Authentication troubleshooting guide",
                    "status": "published",
                },
            },
        ],
        "next_cursor": "cursor-abc123",
        "total_count": 42,
    }


# Recommendations fixtures
@pytest.fixture
def sample_chat_message_data() -> dict[str, Any]:
    """Sample chat message data."""
    return {
        "role": "user",
        "content": "Hello, how can I help you?",
    }


@pytest.fixture
def sample_chat_completion_data() -> dict[str, Any]:
    """Sample chat completion response data."""
    return {
        "id": "chatcmpl-123",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "I can help you with your DevRev questions!",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        },
    }


@pytest.fixture
def sample_get_reply_data() -> dict[str, Any]:
    """Sample get reply response data."""
    return {
        "reply": "Thank you for contacting us. We'll look into this issue.",
        "confidence": 0.95,
    }


# Question Answer fixtures
@pytest.fixture
def sample_question_answer_data() -> dict[str, Any]:
    """Sample question answer data."""
    return {
        "id": "don:core:question_answer:123",
        "display_id": "QA-123",
        "question": "How do I reset my password?",
        "answer": "Click on the 'Forgot Password' link on the login page.",
        "status": "published",
        "created_at": "2024-01-15T10:00:00Z",
        "modified_at": "2024-01-15T12:00:00Z",
    }


# UOM fixtures
@pytest.fixture
def sample_uom_data() -> dict[str, Any]:
    """Sample UOM data."""
    return {
        "id": "don:core:uom:123",
        "name": "Test UOM",
        "description": "Test description",
        "aggregation_type": "sum",
        "metric_scope": "org",
        "is_enabled": True,
    }


# Notification fixtures
@pytest.fixture
def sample_notification_send_response_data() -> dict[str, Any]:
    """Sample notification send response data."""
    return {
        "success": True,
        "notification_id": "don:core:notification:123",
    }


# Track events fixtures
@pytest.fixture
def sample_track_event_data() -> dict[str, Any]:
    """Sample track event data."""
    return {
        "name": "user_login",
        "properties": {
            "source": "web",
            "browser": "chrome",
        },
        "timestamp": "2024-01-15T10:00:00Z",
        "user_id": "don:identity:user:123",
    }


@pytest.fixture
def sample_track_events_publish_response_data() -> dict[str, Any]:
    """Sample track events publish response data."""
    return {
        "success": True,
        "count": 2,
    }


# Preferences fixtures
@pytest.fixture
def sample_preferences_data() -> dict[str, Any]:
    """Sample preferences data."""
    return {
        "id": "don:identity:preferences:123",
        "notifications_enabled": True,
        "email_notifications": True,
        "theme": "dark",
        "locale": "en-US",
    }
