"""Customer response drafting prompt for DevRev tickets."""

from __future__ import annotations

from mcp.types import TextContent

from devrev_mcp.server import mcp


@mcp.prompt()
async def draft_customer_response(
    ticket_id: str,
    tone: str = "professional",
    include_kb: bool = True,
) -> list[TextContent]:
    """Draft a customer response for a support ticket.

    Args:
        ticket_id: DevRev ticket ID.
        tone: Response tone — "formal", "friendly", or "technical" (default: "professional").
        include_kb: Whether to search knowledge base for relevant articles (default: True).
    """
    kb_instruction = ""
    if include_kb:
        kb_instruction = (
            "\n3. Search the knowledge base using `devrev_search_hybrid` for relevant articles "
            "that might help answer the customer's question."
        )

    tone_guidance = {
        "formal": "Use formal, business-appropriate language. Be respectful and professional.",
        "friendly": "Use warm, approachable language while remaining professional. Show empathy.",
        "technical": "Use precise technical terminology. Focus on technical details and accuracy.",
        "professional": "Use clear, professional language. Balance friendliness with formality.",
    }

    tone_desc = tone_guidance.get(tone, tone_guidance["professional"])

    return [
        TextContent(
            type="text",
            text=(
                f"You are a customer support specialist drafting a response for ticket {ticket_id}.\n\n"
                f"**Tone**: {tone} — {tone_desc}\n\n"
                "**Steps**:\n"
                f"1. Use `devrev_works_get` to fetch ticket {ticket_id} and understand the customer's issue.\n"
                "2. Review the ticket description, comments, and any attachments."
                f"{kb_instruction}\n"
                f"4. Draft a {tone} response that:\n"
                "   - Acknowledges the customer's issue\n"
                "   - Provides a clear solution or next steps\n"
                "   - References relevant KB articles if found\n"
                "   - Sets appropriate expectations for resolution time\n"
                "   - Ends with an offer to help further\n\n"
                "Format the response ready to send to the customer."
            ),
        )
    ]
