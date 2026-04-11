"""MCP tools for DevRev question-answer operations (beta API)."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.question_answers import (
    QuestionAnswersCreateRequest,
    QuestionAnswersDeleteRequest,
    QuestionAnswersGetRequest,
    QuestionAnswersListRequest,
    QuestionAnswersUpdateRequest,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.don_id import validate_don_id
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_question_answers_list(
    ctx: Context[Any, Any, Any],
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List DevRev question answers.

    Args:
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of items to return (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        request = QuestionAnswersListRequest(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        response = await app.get_client().question_answers.list(request)
        items = serialize_models(response.question_answers)
        return paginated_response(
            items, next_cursor=response.next_cursor, total_label="question_answers"
        )
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_question_answers_get(
    ctx: Context[Any, Any, Any],
    id: str,
) -> dict[str, Any]:
    """Get a DevRev question answer by ID.

    Args:
        id: The question answer ID.
    """
    validate_don_id(id, "qa", "devrev_question_answers_get")
    app = ctx.request_context.lifespan_context
    try:
        request = QuestionAnswersGetRequest(id=id)
        qa = await app.get_client().question_answers.get(request)
        return serialize_model(qa)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_question_answers_create(
        ctx: Context[Any, Any, Any],
        question: str,
        answer: str,
        applies_to_parts: list[str],
        owned_by: list[str],
        status: str | None = None,
    ) -> dict[str, Any]:
        """Create a new DevRev question answer.

        Args:
            question: The question text.
            answer: The answer text.
            applies_to_parts: List of part IDs this Q&A applies to.
            owned_by: List of dev user IDs who own this Q&A.
            status: Optional status (draft, published). Defaults to draft.
        """
        app = ctx.request_context.lifespan_context
        try:
            kwargs: dict[str, Any] = {
                "question": question,
                "answer": answer,
                "applies_to_parts": applies_to_parts,
                "owned_by": owned_by,
            }
            if status is not None:
                kwargs["status"] = status
            request = QuestionAnswersCreateRequest(**kwargs)
            qa = await app.get_client().question_answers.create(request)
            return serialize_model(qa)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_question_answers_update(
        ctx: Context[Any, Any, Any],
        id: str,
        question: str | None = None,
        answer: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing DevRev question answer.

        Only provided fields will be updated; others remain unchanged.

        Args:
            id: The question answer ID to update.
            question: New question text.
            answer: New answer text.
        """
        validate_don_id(id, "qa", "devrev_question_answers_update")
        app = ctx.request_context.lifespan_context
        try:
            request = QuestionAnswersUpdateRequest(id=id, question=question, answer=answer)
            qa = await app.get_client().question_answers.update(request)
            return serialize_model(qa)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_question_answers_delete(
        ctx: Context[Any, Any, Any],
        id: str,
    ) -> dict[str, Any]:
        """Delete a DevRev question answer.

        Args:
            id: The question answer ID to delete.
        """
        validate_don_id(id, "qa", "devrev_question_answers_delete")
        app = ctx.request_context.lifespan_context
        try:
            request = QuestionAnswersDeleteRequest(id=id)
            await app.get_client().question_answers.delete(request)
            return {"deleted": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e
