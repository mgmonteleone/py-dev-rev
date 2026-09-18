"""Regression guard for CSS-2275: changelog must not reference `async_hybrid`.

The v4.0.0 migration guide in ``docs/changelog.md`` previously described a
nonexistent ``client.search.async_hybrid()`` method. There is no such method:
``AsyncSearchService`` (and ``AsyncDevRevClient.search``) exposes the same
``hybrid`` method name as the sync client, invoked with ``await``. This test
fails against the old (buggy) changelog content and passes against the fix,
and cross-checks the documented shape against the real async API surface
(offline, no network calls).
"""

from __future__ import annotations

import inspect
from pathlib import Path

from devrev.services.search import AsyncSearchService

CHANGELOG_PATH = Path(__file__).resolve().parents[2] / "docs" / "changelog.md"


def test_changelog_does_not_reference_nonexistent_async_hybrid_method() -> None:
    """The v4.0.0 migration guide must not present `async_hybrid` as a
    callable method (e.g. `client.search.async_hybrid(...)`). Prose noting
    that no such method exists is fine; a call-shape reference to it is not.
    """
    content = CHANGELOG_PATH.read_text(encoding="utf-8")

    assert "search.async_hybrid(" not in content, (
        "docs/changelog.md references `client.search.async_hybrid(...)` as "
        "a callable, but no such method exists on AsyncSearchService/"
        "AsyncDevRevClient. The async client's hybrid search method is "
        "`hybrid`, called with `await`."
    )


def test_changelog_describes_await_client_search_hybrid_for_async_usage() -> None:
    """The migration guide must describe async usage as `await ...hybrid(...)`."""
    content = CHANGELOG_PATH.read_text(encoding="utf-8")

    assert (
        "await\n  client.search.hybrid()" in content or "await client.search.hybrid(" in content
    ), (
        "docs/changelog.md should show the async client's hybrid search "
        "being awaited (`await client.search.hybrid(...)`) to distinguish "
        "it from the synchronous `client.search.hybrid(...)` call shape."
    )


def test_async_search_service_has_no_async_hybrid_method() -> None:
    """Corroborate the doc claim against the real async API surface."""
    assert not hasattr(AsyncSearchService, "async_hybrid")


def test_async_search_service_hybrid_is_the_awaitable_public_method() -> None:
    """`AsyncSearchService.hybrid` is the real, awaitable public method."""
    assert hasattr(AsyncSearchService, "hybrid")
    assert inspect.iscoroutinefunction(AsyncSearchService.hybrid)
