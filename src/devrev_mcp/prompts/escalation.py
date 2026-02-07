"""Escalation workflow prompt for DevRev tickets."""

from __future__ import annotations

from mcp.types import TextContent

from devrev_mcp.server import mcp


@mcp.prompt()
async def escalate_ticket(ticket_id: str, reason: str) -> list[TextContent]:
    """Prepare an escalation for a support ticket.

    Args:
        ticket_id: DevRev ticket ID to escalate.
        reason: Reason for escalation.
    """
    return [
        TextContent(
            type="text",
            text=(
                f"You are a support team lead preparing an escalation for ticket {ticket_id}.\n\n"
                f"**Escalation Reason**: {reason}\n\n"
                "**Steps**:\n"
                f"1. Use `devrev_works_get` to fetch complete details for ticket {ticket_id}.\n"
                "2. Review the ticket history, timeline, and all comments.\n"
                "3. Use `devrev_search_hybrid` to find similar escalated tickets and their outcomes.\n"
                "4. Assess the business impact:\n"
                "   - Customer tier/importance\n"
                "   - Revenue impact\n"
                "   - Number of users affected\n"
                "   - SLA status\n\n"
                "**Prepare an escalation summary including**:\n"
                "- **Issue Summary**: Clear, concise description of the problem\n"
                "- **Customer Impact**: Who is affected and how severely\n"
                "- **Timeline**: When the issue started and key events\n"
                "- **Troubleshooting Done**: What has been tried so far\n"
                "- **Why Escalating**: Specific reason for escalation\n"
                "- **Recommended Action**: What the escalation team should do\n"
                "- **Urgency Level**: Critical/High/Medium and why\n\n"
                "Format this as a clear escalation brief ready to send to senior support or engineering."
            ),
        )
    ]
