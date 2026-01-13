"""Deprecation utilities.

This module provides a small, explicit deprecation mechanism for the public SDK.

See: DEPRECATIONS.md
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar
from warnings import warn

P = ParamSpec("P")
R = TypeVar("R")


def deprecated(
    version: str,
    reason: str,
    replacement: str | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Mark a callable as deprecated.

    Args:
        version: Version the symbol was deprecated in (e.g. "1.2.0").
        reason: Short explanation of why it is deprecated.
        replacement: Optional replacement symbol or guidance.

    Returns:
        A decorator that emits a DeprecationWarning on each call.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            msg = f"{func.__name__} is deprecated since {version}: {reason}"
            if replacement:
                msg += f". Use {replacement} instead."
            warn(msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["deprecated"]
