"""DevRev MCP Server - Articles Tools.

This module provides MCP tools for managing DevRev articles.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.articles import (
    ArticlesCreateRequest,
    ArticlesDeleteRequest,
    ArticlesGetRequest,
    ArticlesListRequest,
    ArticleStatus,
    ArticlesUpdateRequest,
)
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size

logger = logging.getLogger(__name__)


@mcp.tool()
async def devrev_articles_list(
    ctx: Context[Any, Any, Any],
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """List articles in DevRev.

    Args:
        ctx: MCP context containing the DevRev client.
        cursor: Pagination cursor for fetching next page.
        limit: Maximum number of articles to return.

    Returns:
        Dictionary containing count and list of articles.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = ArticlesListRequest(
            cursor=cursor,
            limit=clamp_page_size(
                limit, default=app.config.default_page_size, maximum=app.config.max_page_size
            ),
        )
        articles = await app.get_client().articles.list(request)
        items = serialize_models(list(articles))
        return {"count": len(items), "articles": items}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_articles_get(ctx: Context[Any, Any, Any], id: str) -> dict[str, Any]:
    """Get a specific article by ID.

    Args:
        ctx: MCP context containing the DevRev client.
        id: The article ID.

    Returns:
        Dictionary containing the article details.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        request = ArticlesGetRequest(id=id)
        article = await app.get_client().articles.get(request)
        return serialize_model(article)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


# Destructive tools (only registered when enabled)
if _config.enable_destructive_tools:

    @mcp.tool()
    async def devrev_articles_create(
        ctx: Context[Any, Any, Any],
        title: str,
        description: str,
        owned_by: list[str],
        status: str | None = None,
    ) -> dict[str, Any]:
        """Create a new article in DevRev.

        Args:
            ctx: MCP context containing the DevRev client.
            title: The article title.
            description: The article description/body.
            owned_by: List of dev user IDs who own the article.
            status: Optional article status (draft, published, archived).

        Returns:
            Dictionary containing the created article details.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            article_status = None
            if status:
                try:
                    article_status = ArticleStatus[status.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid article status: {e.args[0]}. "
                        f"Valid statuses: {', '.join(s.name for s in ArticleStatus)}"
                    ) from e
            request = ArticlesCreateRequest(
                title=title,
                description=description,
                owned_by=owned_by,
                status=article_status,
            )
            article = await app.get_client().articles.create(request)
            return serialize_model(article)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_articles_update(
        ctx: Context[Any, Any, Any],
        id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing article in DevRev.

        Args:
            ctx: MCP context containing the DevRev client.
            id: The article ID to update.
            title: Optional new title.
            description: Optional new description/body.
            status: Optional new status (draft, published, archived).

        Returns:
            Dictionary containing the updated article details.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            article_status = None
            if status:
                try:
                    article_status = ArticleStatus[status.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid article status: {e.args[0]}. "
                        f"Valid statuses: {', '.join(s.name for s in ArticleStatus)}"
                    ) from e
            request = ArticlesUpdateRequest(
                id=id,
                title=title,
                description=description,
                status=article_status,
            )
            article = await app.get_client().articles.update(request)
            return serialize_model(article)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_articles_delete(ctx: Context[Any, Any, Any], id: str) -> dict[str, Any]:
        """Delete an article from DevRev.

        Args:
            ctx: MCP context containing the DevRev client.
            id: The article ID to delete.

        Returns:
            Dictionary confirming deletion.

        Raises:
            RuntimeError: If the DevRev API call fails.
        """
        app = ctx.request_context.lifespan_context
        try:
            request = ArticlesDeleteRequest(id=id)
            await app.get_client().articles.delete(request)
            return {"success": True, "id": id}
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_articles_count(
    ctx: Context[Any, Any, Any],
    status: list[str] | None = None,
) -> dict[str, Any]:
    """Count articles in DevRev (beta).

    Args:
        ctx: MCP context containing the DevRev client.
        status: Optional list of status filters.

    Returns:
        Dictionary containing the count.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        count = await app.get_client().articles.count(status=status)
        return {"count": count}
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e
