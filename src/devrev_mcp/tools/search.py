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


def _parse_namespace(namespace: str) -> SearchNamespace:
    """Parse namespace string into SearchNamespace enum.

    Handles various input formats:
    - Strips whitespace
    - Strips surrounding quotes (single or double)
    - Tries matching by value (lowercase, e.g., "account")
    - Falls back to matching by name (uppercase, e.g., "ACCOUNT")

    Args:
        namespace: Namespace string to parse (e.g., "account", "WORK", '"ACCOUNT"').

    Returns:
        SearchNamespace enum value.

    Raises:
        RuntimeError: If namespace is invalid.

    Examples:
        >>> _parse_namespace("account")
        SearchNamespace.ACCOUNT
        >>> _parse_namespace("WORK")
        SearchNamespace.WORK
        >>> _parse_namespace('"ACCOUNT"')
        SearchNamespace.ACCOUNT
        >>> _parse_namespace("  'work'  ")
        SearchNamespace.WORK
    """
    # Strip whitespace
    cleaned = namespace.strip()

    # Strip surrounding quotes (both single and double)
    # Handle cases like '"account"' or "'ACCOUNT'" or "account" or 'account'
    while cleaned and cleaned[0] in ('"', "'") and cleaned[-1] in ('"', "'"):
        cleaned = cleaned[1:-1].strip()

    # Try matching by value first (e.g., "account" -> SearchNamespace.ACCOUNT)
    try:
        return SearchNamespace(cleaned.lower())
    except ValueError:
        pass

    # Try matching by name (e.g., "ACCOUNT" -> SearchNamespace.ACCOUNT)
    try:
        return SearchNamespace[cleaned.upper()]
    except KeyError as e:
        raise RuntimeError(
            f"Invalid search namespace: {namespace}. "
            f"Valid namespaces: account, article, capability, component, conversation, "
            f"custom_object, custom_part, custom_work, dashboard, dataset, dev_user, "
            f"enhancement, feature, group, incident, issue, linkable, microservice, "
            f"object_member, opportunity, part, product, project, question_answer, "
            f"rev_org, rev_user, runnable, service_account, sys_user, tag, task, "
            f"ticket, user, vista, widget, work"
        ) from e


def _rerank_results(results: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    """Re-rank search results by boosting items where the query is a substring of display_name or title.

    The DevRev search API does not expose relevance scores or support sort controls.
    This client-side re-ranking improves result quality by moving results whose
    display_name (or title for works) contains the query string to the top,
    preserving relative order within the matched and unmatched groups.

    Args:
        results: List of serialized search result dicts.
        query: The original search query string.

    Returns:
        Re-ranked list with name-matched results first.
    """
    if not query or not results:
        return results

    query_lower = query.lower()
    matched: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []

    for result in results:
        name = _extract_display_name(result)
        if name and query_lower in name.lower():
            matched.append(result)
        else:
            unmatched.append(result)

    return matched + unmatched


def _extract_display_name(result: dict[str, Any]) -> str | None:
    """Extract a display name from a search result for re-ranking.

    Uses the result's 'type' field to dynamically find the entity-specific dict,
    then looks for display_name, title, or name fields. This approach works for
    all 35+ namespace types without hardcoding entity keys.

    Args:
        result: A serialized search result dict.

    Returns:
        The display name string, or None if not found.
    """
    # Use the type field to dynamically locate the entity dict
    # e.g., {"type": "account", "account": {...}} -> result["account"]
    result_type = result.get("type")
    if result_type:
        entity = result.get(result_type)
        if isinstance(entity, dict):
            name = entity.get("display_name") or entity.get("title") or entity.get("name")
            if name:
                return name

    # Fallback: scan all dict values for name-like fields
    # Handles edge cases where type doesn't match the entity key
    for value in result.values():
        if isinstance(value, dict):
            name = value.get("display_name") or value.get("title") or value.get("name")
            if name:
                return name
    return None


@mcp.tool()
async def devrev_search_hybrid(
    ctx: Context,
    query: str,
    namespace: str,
    semantic_weight: float | None = None,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Search DevRev using hybrid search combining keyword and semantic matching (beta).

    Combines traditional keyword matching with semantic understanding for
    intelligent results. Results are client-side re-ranked to boost items
    where the query matches the display name.

    Args:
        query: The search query string.
        namespace: Object type to search in. Valid values: account, article, capability,
            component, conversation, custom_object, custom_part, custom_work, dashboard,
            dataset, dev_user, enhancement, feature, group, incident, issue, linkable,
            microservice, object_member, opportunity, part, product, project,
            question_answer, rev_org, rev_user, runnable, service_account, sys_user,
            tag, task, ticket, user, vista, widget, work.
        semantic_weight: Weight for semantic vs keyword search (0.0-1.0).
            Higher values favor semantic matching.
        cursor: Pagination cursor from a previous response.
        limit: Maximum results to return (default: 10, max: 50).
    """
    app = ctx.request_context.lifespan_context
    try:
        ns = _parse_namespace(namespace)
        response = await app.get_client().search.hybrid(
            query,
            namespace=ns,
            semantic_weight=semantic_weight,
            cursor=cursor,
            limit=clamp_page_size(limit, default=10, maximum=50),
        )
        results = serialize_models(response.results)
        results = _rerank_results(results, query)
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
    namespace: str,
    cursor: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Search DevRev using core search with query language (beta).

    Core search supports advanced DevRev query syntax for precise filtering.
    Unlike hybrid search, core search does not apply client-side re-ranking
    since queries use structured DevRev query language rather than natural language.

    Args:
        query: The search query (supports DevRev query language).
        namespace: Object type to search in. Valid values: account, article, capability,
            component, conversation, custom_object, custom_part, custom_work, dashboard,
            dataset, dev_user, enhancement, feature, group, incident, issue, linkable,
            microservice, object_member, opportunity, part, product, project,
            question_answer, rev_org, rev_user, runnable, service_account, sys_user,
            tag, task, ticket, user, vista, widget, work.
        cursor: Pagination cursor from a previous response.
        limit: Maximum results to return (default: 10, max: 50).
    """
    app = ctx.request_context.lifespan_context
    try:
        ns = _parse_namespace(namespace)
        response = await app.get_client().search.core(
            query,
            namespace=ns,
            cursor=cursor,
            limit=clamp_page_size(limit, default=10, maximum=50),
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
