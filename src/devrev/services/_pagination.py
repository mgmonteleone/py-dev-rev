"""Shared pagination helpers for cursor-streaming list helpers.

The DevRev ``*.list`` endpoints cap per-page responses at 100 items and the
corresponding ``*ListRequest.limit`` fields are pydantic-constrained to
``le=100``. Any service that drives cursor pagination from a user-supplied
``overall_limit`` / ``page_size`` pair must therefore clamp the value it puts
on the request body before construction, or the request will fail validation
locally before it is ever sent.

:func:`resolve_page_limit` centralises that clamping so every ``list_*_since``
helper resolves the per-page ``limit`` identically.
"""

from __future__ import annotations

from typing import Final

_MAX_PAGE: Final[int] = 100


def resolve_page_limit(
    overall_limit: int | None,
    collected: int,
    page_size: int | None,
) -> int | None:
    """Compute the ``limit`` to send for the next page request.

    The returned value is always clamped to :data:`_MAX_PAGE` so callers using
    an ``overall_limit`` greater than the server maximum (e.g. ``limit=200,
    page_size=None``) still paginate correctly. When both ``overall_limit`` and
    ``page_size`` are supplied the tightest of ``{page_size, remaining,
    _MAX_PAGE}`` wins.

    Args:
        overall_limit: Caller-supplied hard cap on total items to return across
            all pages, or ``None`` to stream until the server runs out of
            results.
        collected: Number of items already accumulated across prior pages.
        page_size: Caller-supplied per-page size, or ``None`` to defer to the
            server default (still clamped to :data:`_MAX_PAGE`).

    Returns:
        The ``limit`` to put on the next ``*ListRequest``, or ``None`` to omit
        it entirely (only when both ``overall_limit`` and ``page_size`` are
        ``None``).
    """
    if overall_limit is None:
        if page_size is None:
            return None
        return min(page_size, _MAX_PAGE)
    remaining = overall_limit - collected
    if page_size is None:
        return min(remaining, _MAX_PAGE)
    return min(page_size, remaining, _MAX_PAGE)
