"""Investigation and research prompts for DevRev tickets."""

from __future__ import annotations

from mcp.types import TextContent

from devrev_mcp.server import mcp


@mcp.prompt()
async def investigate_issue(ticket_id: str, depth: str = "standard") -> list[TextContent]:
    """Investigate a technical issue from a support ticket.

    Args:
        ticket_id: DevRev ticket ID.
        depth: Investigation depth — "shallow", "standard", or "deep" (default: "standard").
    """
    depth_instructions = {
        "shallow": (
            "- Quick review of ticket details and immediate context\n"
            "- Search for 2-3 similar tickets\n"
            "- Provide initial assessment and quick recommendations"
        ),
        "standard": (
            "- Thorough review of ticket details, comments, and timeline\n"
            "- Search for 5-7 similar tickets and their resolutions\n"
            "- Analyze patterns and common solutions\n"
            "- Provide detailed assessment with multiple solution options"
        ),
        "deep": (
            "- Comprehensive review of all ticket data and related context\n"
            "- Extensive search for similar tickets (10+) across all time periods\n"
            "- Deep pattern analysis and root cause investigation\n"
            "- Review account history for related issues\n"
            "- Provide detailed technical analysis with root cause hypothesis\n"
            "- Include preventive measures and long-term solutions"
        ),
    }

    investigation_steps = depth_instructions.get(depth, depth_instructions["standard"])

    return [
        TextContent(
            type="text",
            text=(
                f"You are a senior technical support engineer investigating ticket {ticket_id}.\n\n"
                f"**Investigation Depth**: {depth}\n\n"
                "**Steps**:\n"
                f"1. Use `devrev_works_get` to fetch ticket {ticket_id} with full details.\n"
                "2. Conduct investigation:\n"
                f"{investigation_steps}\n\n"
                "**Provide an investigation report including**:\n"
                "- **Issue Description**: Clear technical summary of the problem\n"
                "- **Symptoms**: Observable behaviors and error messages\n"
                "- **Similar Cases**: Summary of related tickets and their outcomes\n"
                "- **Root Cause Analysis**: Likely cause(s) of the issue\n"
                "- **Solution Options**: Ranked by likelihood of success\n"
                "- **Testing Steps**: How to verify the solution\n"
                "- **Prevention**: How to avoid this issue in the future\n"
                "- **Confidence Level**: High/Medium/Low and why\n\n"
                "Format as a technical investigation report."
            ),
        )
    ]


@mcp.prompt()
async def find_similar_tickets(description: str, limit: int = 5) -> list[TextContent]:
    """Find similar past tickets and their resolutions.

    Args:
        description: Description of the issue to search for.
        limit: Maximum number of similar tickets to find (default: 5).
    """
    return [
        TextContent(
            type="text",
            text=(
                "You are a support knowledge specialist finding similar past tickets.\n\n"
                f"**Search Query**: {description}\n"
                f"**Result Limit**: {limit} most relevant tickets\n\n"
                "**Steps**:\n"
                f"1. Use `devrev_search_hybrid` to search for tickets matching: {description}\n"
                f"2. Retrieve the top {limit} most similar tickets.\n"
                "3. For each ticket, use `devrev_works_get` to get full details.\n"
                "4. Focus on resolved tickets with documented solutions.\n\n"
                "**Provide a summary including**:\n"
                "- **Search Summary**: What you searched for and how many results found\n"
                "- **Similar Tickets**: For each ticket:\n"
                "  - Ticket ID and title\n"
                "  - Similarity to current issue (High/Medium/Low)\n"
                "  - Resolution status\n"
                "  - Solution applied (if resolved)\n"
                "  - Time to resolution\n"
                "  - Key learnings\n"
                "- **Common Patterns**: Recurring themes across similar tickets\n"
                "- **Recommended Approach**: Best solution based on past successes\n"
                "- **Warnings**: Solutions that didn't work or caused issues\n\n"
                "Format as a knowledge base search report."
            ),
        )
    ]


@mcp.prompt()
async def onboard_customer(
    account_id: str, product_part_id: str | None = None
) -> list[TextContent]:
    """Generate a customer onboarding checklist and setup guide.

    Args:
        account_id: DevRev account ID for the new customer.
        product_part_id: Optional product part ID to customize onboarding.
    """
    product_context = ""
    if product_part_id:
        product_context = (
            f"\n2. Use `devrev_product_parts_get` to fetch details for product part {product_part_id}.\n"
            "3. Customize the onboarding based on the specific product features."
        )

    return [
        TextContent(
            type="text",
            text=(
                f"You are a customer success specialist creating an onboarding plan for account {account_id}.\n\n"
                "**Steps**:\n"
                f"1. Use `devrev_accounts_get` to fetch account {account_id} details."
                f"{product_context}\n"
                f"{'4' if product_part_id else '2'}. Use `devrev_search_hybrid` to find successful onboarding examples.\n"
                f"{'5' if product_part_id else '3'}. Review best practices from similar customer onboardings.\n\n"
                "**Generate an onboarding plan including**:\n"
                "- **Customer Profile**:\n"
                "  - Account name and tier\n"
                "  - Industry and use case\n"
                "  - Team size and key contacts\n"
                f"{'  - Product parts being deployed' if product_part_id else ''}\n"
                "- **Onboarding Checklist**:\n"
                "  - [ ] Initial kickoff call scheduled\n"
                "  - [ ] Account setup and configuration\n"
                "  - [ ] User access and permissions configured\n"
                "  - [ ] Integration setup (if applicable)\n"
                "  - [ ] Training sessions scheduled\n"
                "  - [ ] Documentation shared\n"
                "  - [ ] Success criteria defined\n"
                "  - [ ] First milestone achieved\n"
                "- **Timeline**: Week-by-week plan for first 30-60 days\n"
                "- **Key Resources**: Documentation, training materials, contacts\n"
                "- **Success Metrics**: How to measure successful onboarding\n"
                "- **Risk Mitigation**: Common pitfalls and how to avoid them\n"
                "- **Next Steps**: Immediate actions for the CSM\n\n"
                "Format as an actionable onboarding playbook."
            ),
        )
    ]
