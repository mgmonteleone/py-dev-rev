"""MCP tools for DevRev AI recommendation operations (beta API)."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.recommendations import (
    ChatCompletionRequest,
    ChatMessage,
    GetReplyRequest,
    MessageRole,
)
from devrev_mcp.server import mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_recommendations_reply(
    ctx: Context,
    object_id: str,
    context: str | None = None,
) -> dict[str, Any]:
    """Get an AI-recommended reply for a DevRev object (beta).

    Generates a suggested reply for a conversation or work item.

    Args:
        object_id: The DevRev object ID to generate a reply for.
        context: Additional context to improve the recommendation.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = GetReplyRequest(object_id=object_id, context=context)
        response = await app.client.recommendations.get_reply(request)
        return serialize_model(response)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_recommendations_chat(
    ctx: Context,
    messages: list[dict[str, str]],
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> dict[str, Any]:
    """Get AI chat completions from DevRev (beta).

    Send a conversation and get an AI-generated response.

    Args:
        messages: List of messages, each a dict with 'role' (system/user/assistant)
            and 'content' keys.
        max_tokens: Maximum tokens to generate in the response.
        temperature: Sampling temperature (0.0-1.0). Lower is more deterministic.
    """
    app = ctx.request_context.lifespan_context
    try:
        # Build chat messages, catching missing keys or invalid values
        try:
            chat_messages = [
                ChatMessage(role=MessageRole(m["role"]), content=m["content"]) for m in messages
            ]
        except KeyError as e:
            raise RuntimeError(
                f"Invalid message format: missing required key {e.args[0]}. "
                "Each message must have 'role' and 'content' keys."
            ) from e
        except ValueError as e:
            raise RuntimeError(
                f"Invalid message role: {e.args[0]}. "
                f"Valid roles: {', '.join(r.value for r in MessageRole)}"
            ) from e

        request = ChatCompletionRequest(
            messages=chat_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        response = await app.client.recommendations.chat_completions(request)
        return serialize_model(response)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
