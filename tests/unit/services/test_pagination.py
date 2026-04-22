"""Unit tests for the shared pagination helper."""

from __future__ import annotations

import pytest

from devrev.services._pagination import _MAX_PAGE, resolve_page_limit


class TestResolvePageLimit:
    """Tight-clamping semantics for ``resolve_page_limit``."""

    def test_max_page_constant_is_one_hundred(self) -> None:
        """Server-side cap is exactly 100 items per page."""
        assert _MAX_PAGE == 100

    @pytest.mark.parametrize(
        ("overall_limit", "collected", "page_size", "expected"),
        [
            # No overall cap, no page size → defer entirely to server.
            (None, 0, None, None),
            # No overall cap, small page size → pass through.
            (None, 0, 50, 50),
            # No overall cap, page_size above MAX → clamp to MAX.
            (None, 0, 200, 100),
            # Overall cap below MAX, no page size → send remaining.
            (50, 0, None, 50),
            # Overall cap with some collected, no page size → send remaining.
            (50, 45, None, 5),
            # Overall cap above MAX, no page size → clamp to MAX.
            (500, 0, None, 100),
            # Tightest of {page_size=10, remaining=5, MAX=100} wins.
            (50, 45, 10, 5),
            # Tightest of {page_size=50, remaining=500, MAX=100} wins.
            (500, 0, 50, 50),
            # page_size > MAX with large remaining → MAX wins.
            (500, 0, 200, 100),
        ],
    )
    def test_resolve_page_limit_cases(
        self,
        overall_limit: int | None,
        collected: int,
        page_size: int | None,
        expected: int | None,
    ) -> None:
        """Exhaustive coverage of the clamping matrix from the ticket."""
        assert resolve_page_limit(overall_limit, collected, page_size) == expected
