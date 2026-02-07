"""Summary and reporting prompts for DevRev."""

from __future__ import annotations

from mcp.types import TextContent

from devrev_mcp.server import mcp


@mcp.prompt()
async def summarize_account(account_id: str) -> list[TextContent]:
    """Generate a comprehensive account health summary.

    Args:
        account_id: DevRev account ID.
    """
    return [
        TextContent(
            type="text",
            text=(
                f"You are a customer success manager creating a health summary for account {account_id}.\n\n"
                "**Steps**:\n"
                f"1. Use `devrev_accounts_get` to fetch account {account_id} details.\n"
                "2. Use `devrev_search_hybrid` to find all recent tickets for this account (last 30 days).\n"
                "3. Analyze ticket patterns, response times, and resolution rates.\n"
                "4. Look for any escalations or critical issues.\n\n"
                "**Generate a comprehensive summary including**:\n"
                "- **Account Overview**: Name, tier, key contacts\n"
                "- **Support Activity**: Number of tickets, types, trends\n"
                "- **Health Indicators**:\n"
                "  - Ticket volume trend (increasing/decreasing/stable)\n"
                "  - Average resolution time\n"
                "  - Customer satisfaction signals\n"
                "  - Escalation count\n"
                "- **Risk Assessment**: Any red flags or concerns\n"
                "- **Opportunities**: Upsell, training, or engagement opportunities\n"
                "- **Recommended Actions**: What the CSM should do next\n\n"
                "Provide an executive summary suitable for account review meetings."
            ),
        )
    ]


@mcp.prompt()
async def weekly_support_report(period_days: int = 7) -> list[TextContent]:
    """Generate a weekly support metrics report.

    Args:
        period_days: Number of days to cover (default: 7).
    """
    return [
        TextContent(
            type="text",
            text=(
                f"You are a support operations manager creating a {period_days}-day support metrics report.\n\n"
                "**Steps**:\n"
                f"1. Use `devrev_search_hybrid` to find all tickets created in the last {period_days} days.\n"
                "2. Categorize tickets by type, priority, and status.\n"
                "3. Calculate key metrics and identify trends.\n\n"
                "**Generate a report including**:\n"
                "- **Volume Metrics**:\n"
                f"  - Total tickets created in last {period_days} days\n"
                "  - Breakdown by priority (p0, p1, p2, p3)\n"
                "  - Breakdown by type (bug, feature request, question, etc.)\n"
                "- **Performance Metrics**:\n"
                "  - Average first response time\n"
                "  - Average resolution time\n"
                "  - Tickets resolved vs. still open\n"
                "  - SLA compliance rate\n"
                "- **Quality Indicators**:\n"
                "  - Escalation rate\n"
                "  - Reopened tickets\n"
                "  - Customer satisfaction (if available)\n"
                "- **Trends**:\n"
                f"  - Comparison to previous {period_days}-day period\n"
                "  - Emerging issues or patterns\n"
                "  - Top affected customers\n"
                "- **Action Items**:\n"
                "  - Areas needing attention\n"
                "  - Process improvements\n"
                "  - Resource allocation recommendations\n\n"
                "Format as an executive summary suitable for leadership review."
            ),
        )
    ]
