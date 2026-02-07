"""Pagination utilities for DevRev MCP tools."""

from __future__ import annotations

from typing import Any

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100


def clamp_page_size(
    limit: int | None,
    *,
    default: int = DEFAULT_PAGE_SIZE,
    maximum: int = MAX_PAGE_SIZE,
) -> int:
    """Clamp a page size to valid bounds.

    Args:
        limit: Requested page size (None uses default).
        default: Default page size when limit is None.
        maximum: Maximum allowed page size.

    Returns:
        A valid page size within bounds.
    """
    if limit is None:
        return default
    return max(1, min(limit, maximum))


def paginated_response(
    items: list[dict[str, Any]],
    *,
    next_cursor: str | None = None,
    total_label: str = "items",
) -> dict[str, Any]:
    """Build a standardized paginated response dict.

    Args:
        items: List of serialized items.
        next_cursor: Cursor for the next page, if available.
        total_label: Label for the items count in the response.

    Returns:
        A dict with count, items, and optional next_cursor.
    """
    result: dict[str, Any] = {
        "count": len(items),
        total_label: items,
    }
    if next_cursor:
        result["next_cursor"] = next_cursor
    return result
