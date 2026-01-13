from __future__ import annotations

import pytest

from devrev.utils.deprecation import deprecated


def test_deprecated_emits_warning_with_replacement() -> None:
    @deprecated(version="1.2.0", reason="use new api", replacement="new_func")
    def old_func(x: int) -> int:
        return x + 1

    with pytest.warns(DeprecationWarning, match=r"old_func is deprecated since 1\.2\.0"):
        assert old_func(1) == 2


def test_deprecated_emits_warning_without_replacement() -> None:
    @deprecated(version="1.2.0", reason="no longer supported")
    def old_func() -> str:
        return "ok"

    with pytest.warns(DeprecationWarning, match=r"no longer supported"):
        assert old_func() == "ok"
