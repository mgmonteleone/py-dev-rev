"""MCP tools for DevRev search operations (beta API)."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.search import SearchNamespace
from devrev_mcp.server import mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_models
from devrev_mcp.utils.pagination import clamp_page_size

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_search_hybrid(
    ctx: Context,
    query: str,
    namespaces: list[str] | None = None,
    semantic_weight: float | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Search DevRev using hybrid search combining keyword and semantic matching (beta).

    Combines traditional keyword matching with semantic understanding for
    intelligent results.

    Args:
        query: The search query string.
        namespaces: Limit search to specific types: ACCOUNT, ARTICLE, CONVERSATION,
            WORK, USER, TAG, PART, REV_USER, DEV_USER.
        semantic_weight: Weight for semantic vs keyword search (0.0-1.0).
            Higher values favor semantic matching.
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of results (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        # Convert namespace strings to enum, catching invalid values
        ns = None
        if namespaces:
            try:
                ns = [SearchNamespace(n.lower()) for n in namespaces]
            except ValueError as e:
                raise RuntimeError(
                    f"Invalid search namespace: {e.args[0]}. "
                    f"Valid namespaces: {', '.join(n.value for n in SearchNamespace)}"
                ) from e
        response = await app.client.search.hybrid(
            query,
            namespaces=ns,
            semantic_weight=semantic_weight,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        results = serialize_models(response.results)
        result: dict[str, Any] = {
            "count": len(results),
            "results": results,
        }
        if response.next_cursor:
            result["next_cursor"] = response.next_cursor
        if response.total_count is not None:
            result["total_count"] = response.total_count
        return result
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_search_core(
    ctx: Context,
    query: str,
    namespaces: list[str] | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Search DevRev using core search with query language (beta).

    Core search supports advanced DevRev query syntax for precise filtering.

    Args:
        query: The search query (supports DevRev query language).
        namespaces: Limit search to specific types: ACCOUNT, ARTICLE, CONVERSATION,
            WORK, USER, TAG, PART, REV_USER, DEV_USER.
        cursor: Pagination cursor from a previous response.
        limit: Maximum number of results (default: 25, max: 100).
    """
    app = ctx.request_context.lifespan_context
    try:
        # Convert namespace strings to enum, catching invalid values
        ns = None
        if namespaces:
            try:
                ns = [SearchNamespace(n.lower()) for n in namespaces]
            except ValueError as e:
                raise RuntimeError(
                    f"Invalid search namespace: {e.args[0]}. "
                    f"Valid namespaces: {', '.join(n.value for n in SearchNamespace)}"
                ) from e
        response = await app.client.search.core(
            query,
            namespaces=ns,
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        results = serialize_models(response.results)
        result: dict[str, Any] = {
            "count": len(results),
            "results": results,
        }
        if response.next_cursor:
            result["next_cursor"] = response.next_cursor
        if response.total_count is not None:
            result["total_count"] = response.total_count
        return result
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
