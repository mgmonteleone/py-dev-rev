"""Tests for DevRev MCP resources."""

from __future__ import annotations

import json

import pytest

from devrev_mcp.resources.account import get_account_resource
from devrev_mcp.resources.article import get_article_resource
from devrev_mcp.resources.conversation import get_conversation_resource
from devrev_mcp.resources.part import get_part_resource
from devrev_mcp.resources.ticket import get_ticket_resource
from devrev_mcp.resources.user import get_dev_user_resource, get_rev_user_resource


@pytest.mark.asyncio
async def test_ticket_resource():
    """Test ticket resource returns correct metadata."""
    result = await get_ticket_resource("don:core:ticket:123")
    data = json.loads(result)
    assert data["uri"] == "devrev://ticket/don:core:ticket:123"
    assert data["type"] == "ticket"
    assert data["id"] == "don:core:ticket:123"
    assert "devrev_works_get" in data["note"]


@pytest.mark.asyncio
async def test_account_resource():
    """Test account resource returns correct metadata."""
    result = await get_account_resource("don:core:account:456")
    data = json.loads(result)
    assert data["uri"] == "devrev://account/don:core:account:456"
    assert data["type"] == "account"
    assert data["id"] == "don:core:account:456"
    assert "devrev_accounts_get" in data["note"]


@pytest.mark.asyncio
async def test_article_resource():
    """Test article resource returns correct metadata."""
    result = await get_article_resource("don:core:article:789")
    data = json.loads(result)
    assert data["uri"] == "devrev://article/don:core:article:789"
    assert data["type"] == "article"
    assert data["id"] == "don:core:article:789"
    assert data["mime_type"] == "text/markdown"
    assert "devrev_articles_get" in data["note"]


@pytest.mark.asyncio
async def test_dev_user_resource():
    """Test dev user resource returns correct metadata."""
    result = await get_dev_user_resource("don:core:dev_user:111")
    data = json.loads(result)
    assert data["uri"] == "devrev://user/dev/don:core:dev_user:111"
    assert data["type"] == "dev_user"
    assert data["id"] == "don:core:dev_user:111"
    assert "devrev_dev_users_get" in data["note"]


@pytest.mark.asyncio
async def test_rev_user_resource():
    """Test rev user resource returns correct metadata."""
    result = await get_rev_user_resource("don:core:rev_user:222")
    data = json.loads(result)
    assert data["uri"] == "devrev://user/rev/don:core:rev_user:222"
    assert data["type"] == "rev_user"
    assert data["id"] == "don:core:rev_user:222"
    assert "devrev_rev_users_get" in data["note"]


@pytest.mark.asyncio
async def test_part_resource():
    """Test part resource returns correct metadata."""
    result = await get_part_resource("don:core:part:333")
    data = json.loads(result)
    assert data["uri"] == "devrev://part/don:core:part:333"
    assert data["type"] == "part"
    assert data["id"] == "don:core:part:333"
    assert "devrev_parts_get" in data["note"]


@pytest.mark.asyncio
async def test_conversation_resource():
    """Test conversation resource returns correct metadata."""
    result = await get_conversation_resource("don:core:conversation:444")
    data = json.loads(result)
    assert data["uri"] == "devrev://conversation/don:core:conversation:444"
    assert data["type"] == "conversation"
    assert data["id"] == "don:core:conversation:444"
    assert "devrev_conversations_get" in data["note"]


@pytest.mark.asyncio
async def test_ticket_resource_with_complex_id():
    """Test ticket resource with a more complex DON ID."""
    complex_id = "don:core:dvrv-us-1:devo/1:ticket/12345"
    result = await get_ticket_resource(complex_id)
    data = json.loads(result)
    assert data["uri"] == f"devrev://ticket/{complex_id}"
    assert data["id"] == complex_id


@pytest.mark.asyncio
async def test_account_resource_with_complex_id():
    """Test account resource with a more complex DON ID."""
    complex_id = "don:core:dvrv-us-1:devo/1:account/67890"
    result = await get_account_resource(complex_id)
    data = json.loads(result)
    assert data["uri"] == f"devrev://account/{complex_id}"
    assert data["id"] == complex_id


@pytest.mark.asyncio
async def test_all_resources_return_valid_json():
    """Test that all resources return valid JSON strings."""
    resources = [
        get_ticket_resource("test:123"),
        get_account_resource("test:456"),
        get_article_resource("test:789"),
        get_dev_user_resource("test:111"),
        get_rev_user_resource("test:222"),
        get_part_resource("test:333"),
        get_conversation_resource("test:444"),
    ]

    for resource_coro in resources:
        result = await resource_coro
        # Should not raise an exception
        data = json.loads(result)
        # All resources should have these fields
        assert "uri" in data
        assert "type" in data
        assert "id" in data
        assert "note" in data
