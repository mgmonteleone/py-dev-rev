"""Rate limiting middleware for the DevRev MCP Server HTTP transports."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket rate limiter for a single client.

    Args:
        rate: Tokens added per second.
        capacity: Maximum tokens in the bucket.
    """

    def __init__(self, rate: float, capacity: float) -> None:
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def consume(self) -> bool:
        """Try to consume one token.

        Returns:
            True if a token was consumed, False if rate limited.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False

    @property
    def retry_after(self) -> float:
        """Seconds until the next token is available."""
        if self.tokens >= 1.0:
            return 0.0
        return (1.0 - self.tokens) / self.rate


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces per-client rate limiting using token bucket algorithm.

    Rate limits are tracked per client IP address. The MCP session ID is used
    if available (from Mcp-Session-Id header), otherwise falls back to client IP.

    Args:
        app: The ASGI application.
        requests_per_minute: Maximum requests per minute per client.
        skip_paths: Paths to skip rate limiting for (e.g., /health).
    """

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 120,
        skip_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._rate = requests_per_minute / 60.0  # tokens per second
        self._capacity = float(requests_per_minute)
        self._buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(self._rate, self._capacity)
        )
        self._skip_paths = skip_paths or {"/health"}

    def _get_client_key(self, request: Request) -> str:
        """Get a unique key for the client.

        Uses MCP session ID if available, otherwise client IP.
        """
        session_id = request.headers.get("mcp-session-id")
        if session_id:
            return f"session:{session_id}"
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware/handler in the chain.

        Returns:
            The response from the next handler, or a 429 error response.
        """
        # Skip rate limiting for health checks and OPTIONS
        if request.url.path in self._skip_paths or request.method == "OPTIONS":
            return await call_next(request)

        client_key = self._get_client_key(request)
        bucket = self._buckets[client_key]

        if not bucket.consume():
            retry_after = int(bucket.retry_after) + 1
            logger.warning(
                "Rate limit exceeded for %s (retry_after=%ds)",
                client_key,
                retry_after,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)
