"""DevRev MCP Server - Articles Tools.

This module provides MCP tools for managing DevRev articles.
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.articles import (
    ArticleAccessLevel,
    ArticlesDeleteRequest,
    ArticlesGetRequest,
    ArticlesListRequest,
    ArticleStatus,
)
from devrev.models.base import SetTagWithValue
from devrev_mcp.server import _config, mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model, serialize_models
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response

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
        Dictionary containing count, list of articles, and optional next_cursor
        for pagination.

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
        response = await app.get_client().articles.list(request)
        items = serialize_models(response.articles)
        return paginated_response(items, next_cursor=response.next_cursor, total_label="articles")
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e


@mcp.tool()
async def devrev_articles_get(
    ctx: Context[Any, Any, Any], id: str, include_content: bool = False
) -> dict[str, Any]:
    """Get a specific article by ID.

    Args:
        ctx: MCP context containing the DevRev client.
        id: The article ID.
        include_content: If True, fetch and include article body content.

    Returns:
        Dictionary containing the article details. When include_content=True,
        returns ArticleWithContent including the content field.

    Raises:
        RuntimeError: If the DevRev API call fails.
    """
    app = ctx.request_context.lifespan_context
    try:
        if include_content:
            article_with_content = await app.get_client().articles.get_with_content(id)
            return serialize_model(article_with_content)
        else:
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
        content: str,
        owned_by: list[str],
        description: str | None = None,
        status: str | None = None,
        content_format: str = "text/html",
        applies_to_parts: list[str] | None = None,
        scope: int | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new article with content.

        Args:
            ctx: MCP context containing the DevRev client.
            title: Article title.
            content: The article body content (HTML, markdown, or plain text).
            owned_by: List of dev user IDs who own the article.
            description: Optional short metadata description (NOT the article body).
            status: Optional article status (draft, published, archived).
            content_format: Content MIME type (default: text/html).
            applies_to_parts: Optional list of part IDs (products, capabilities,
                features, enhancements) to associate the article with.
            scope: Optional visibility scope (1=internal, 2=external).
            tags: Optional list of tag IDs to apply to the article.

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

            # Convert tag IDs to SetTagWithValue objects
            tags_list = (
                [SetTagWithValue(id=tag_id) for tag_id in tags] if tags is not None else None
            )

            article = await app.get_client().articles.create_with_content(
                title=title,
                content=content,
                owned_by=owned_by,
                description=description,
                status=article_status,
                content_format=content_format,
                applies_to_parts=applies_to_parts,
                scope=scope,
                tags=tags_list,
            )
            return serialize_model(article)
        except DevRevError as e:
            raise RuntimeError(format_devrev_error(e)) from e

    @mcp.tool()
    async def devrev_articles_update(
        ctx: Context[Any, Any, Any],
        id: str,
        title: str | None = None,
        content: str | None = None,
        description: str | None = None,
        status: str | None = None,
        applies_to_parts: list[str] | None = None,
        access_level: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Update an existing article in DevRev.

        Args:
            ctx: MCP context containing the DevRev client.
            id: The article ID to update.
            title: Optional new title.
            content: Optional new article body content.
            description: Optional new metadata description (NOT the article body).
            status: Optional new status (draft, published, archived).
            applies_to_parts: Optional list of part IDs (products, capabilities,
                features, enhancements) to associate the article with.
                Pass an empty list to remove all associations.
            access_level: Optional access level (internal, external, private, public).
                Note: For updates, use ``access_level`` (string enum). For creation,
                use the ``scope`` parameter (integer: 1=internal, 2=external).
            tags: Optional list of tag IDs to apply to the article.
                Pass an empty list to remove all tags.

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

            # Convert access_level string to ArticleAccessLevel enum
            article_access_level = None
            if access_level:
                try:
                    article_access_level = ArticleAccessLevel[access_level.upper()]
                except KeyError as e:
                    raise RuntimeError(
                        f"Invalid access level: {e.args[0]}. "
                        f"Valid levels: {', '.join(a.name for a in ArticleAccessLevel)}"
                    ) from e

            # Convert tag IDs to SetTagWithValue objects
            tags_list = (
                [SetTagWithValue(id=tag_id) for tag_id in tags] if tags is not None else None
            )

            article = await app.get_client().articles.update_with_content(
                id=id,
                title=title,
                content=content,
                description=description,
                status=article_status,
                applies_to_parts=applies_to_parts,
                access_level=article_access_level,
                tags=tags_list,
            )
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
