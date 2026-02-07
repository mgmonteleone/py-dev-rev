"""Triage prompt for DevRev tickets."""

from __future__ import annotations

from mcp.types import TextContent

from devrev_mcp.server import mcp


@mcp.prompt()
async def triage_ticket(ticket_id: str) -> list[TextContent]:
    """Triage a support ticket — analyze and recommend priority, severity, assignment, and next steps.

    Args:
        ticket_id: DevRev ticket ID (DON format, e.g., don:core:dvrv-us-1:devo/1:ticket/123).
    """
    return [
        TextContent(
            type="text",
            text=(
                f"You are a senior support triage analyst. Analyze ticket {ticket_id} and provide:\n\n"
                "1. **Priority Recommendation**: p0 (critical), p1 (high), p2 (medium), p3 (low)\n"
                "2. **Severity Assessment**: blocker, high, medium, low\n"
                "3. **Component Identification**: Which product part is affected?\n"
                "4. **Suggested Assignee**: Based on the component and issue type\n"
                "5. **Next Action Steps**: What should happen next?\n\n"
                f"First, use the `devrev_works_get` tool to fetch ticket {ticket_id}.\n"
                "Then use `devrev_search_hybrid` to find similar past tickets.\n"
                "Finally, provide your triage assessment."
            ),
        )
    ]
