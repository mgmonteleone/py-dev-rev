"""Tests for DevRev MCP prompts."""

from __future__ import annotations

import pytest
from mcp.types import TextContent

from devrev_mcp.prompts.escalation import escalate_ticket
from devrev_mcp.prompts.investigate import (
    find_similar_tickets,
    investigate_issue,
    onboard_customer,
)
from devrev_mcp.prompts.response import draft_customer_response
from devrev_mcp.prompts.summarize import summarize_account, weekly_support_report
from devrev_mcp.prompts.triage import triage_ticket


@pytest.mark.asyncio
async def test_triage_ticket():
    """Test triage_ticket prompt returns valid content."""
    result = await triage_ticket("don:core:dvrv-us-1:devo/1:ticket/123")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "don:core:dvrv-us-1:devo/1:ticket/123" in result[0].text
    assert any(keyword in result[0].text.lower() for keyword in ["triage", "priority", "severity"])


@pytest.mark.asyncio
async def test_draft_customer_response_default():
    """Test draft_customer_response with default parameters."""
    result = await draft_customer_response("don:core:ticket:456")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "don:core:ticket:456" in result[0].text
    assert "professional" in result[0].text.lower()


@pytest.mark.asyncio
async def test_draft_customer_response_friendly_tone():
    """Test draft_customer_response with friendly tone."""
    result = await draft_customer_response("ticket:789", tone="friendly", include_kb=True)

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert "ticket:789" in result[0].text
    assert "friendly" in result[0].text.lower()
    assert "knowledge base" in result[0].text.lower() or "kb" in result[0].text.lower()


@pytest.mark.asyncio
async def test_draft_customer_response_no_kb():
    """Test draft_customer_response without KB search."""
    result = await draft_customer_response("ticket:999", tone="technical", include_kb=False)

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert "ticket:999" in result[0].text
    assert "technical" in result[0].text.lower()


@pytest.mark.asyncio
async def test_escalate_ticket():
    """Test escalate_ticket prompt returns valid content."""
    result = await escalate_ticket(
        "don:core:ticket:111", reason="Customer is VIP and issue is blocking production"
    )

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "don:core:ticket:111" in result[0].text
    assert "Customer is VIP and issue is blocking production" in result[0].text
    assert any(keyword in result[0].text.lower() for keyword in ["escalat", "impact", "urgency"])


@pytest.mark.asyncio
async def test_summarize_account():
    """Test summarize_account prompt returns valid content."""
    result = await summarize_account("don:core:account:222")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "don:core:account:222" in result[0].text
    assert any(keyword in result[0].text.lower() for keyword in ["account", "health", "summary"])


@pytest.mark.asyncio
async def test_weekly_support_report_default():
    """Test weekly_support_report with default period."""
    result = await weekly_support_report()

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "7" in result[0].text
    assert any(keyword in result[0].text.lower() for keyword in ["report", "metrics", "support"])


@pytest.mark.asyncio
async def test_weekly_support_report_custom_period():
    """Test weekly_support_report with custom period."""
    result = await weekly_support_report(period_days=14)

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert "14" in result[0].text
    assert "report" in result[0].text.lower()


@pytest.mark.asyncio
async def test_investigate_issue_default():
    """Test investigate_issue with default depth."""
    result = await investigate_issue("don:core:ticket:333")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "don:core:ticket:333" in result[0].text
    assert "standard" in result[0].text.lower()
    assert any(
        keyword in result[0].text.lower() for keyword in ["investigat", "analysis", "root cause"]
    )


@pytest.mark.asyncio
async def test_investigate_issue_deep():
    """Test investigate_issue with deep investigation."""
    result = await investigate_issue("ticket:444", depth="deep")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert "ticket:444" in result[0].text
    assert "deep" in result[0].text.lower()


@pytest.mark.asyncio
async def test_investigate_issue_shallow():
    """Test investigate_issue with shallow investigation."""
    result = await investigate_issue("ticket:555", depth="shallow")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert "ticket:555" in result[0].text
    assert "shallow" in result[0].text.lower()


@pytest.mark.asyncio
async def test_find_similar_tickets_default():
    """Test find_similar_tickets with default limit."""
    result = await find_similar_tickets("login error with SSO")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "login error with SSO" in result[0].text
    assert "5" in result[0].text
    assert any(keyword in result[0].text.lower() for keyword in ["similar", "search", "tickets"])


@pytest.mark.asyncio
async def test_find_similar_tickets_custom_limit():
    """Test find_similar_tickets with custom limit."""
    result = await find_similar_tickets("database connection timeout", limit=10)

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert "database connection timeout" in result[0].text
    assert "10" in result[0].text


@pytest.mark.asyncio
async def test_onboard_customer_basic():
    """Test onboard_customer without product part."""
    result = await onboard_customer("don:core:account:666")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert result[0].type == "text"
    assert "don:core:account:666" in result[0].text
    assert any(keyword in result[0].text.lower() for keyword in ["onboard", "checklist", "setup"])


@pytest.mark.asyncio
async def test_onboard_customer_with_product():
    """Test onboard_customer with product part."""
    result = await onboard_customer("don:core:account:777", product_part_id="don:core:product:888")

    assert len(result) >= 1
    assert isinstance(result[0], TextContent)
    assert "don:core:account:777" in result[0].text
    assert "don:core:product:888" in result[0].text
    assert "onboard" in result[0].text.lower()
