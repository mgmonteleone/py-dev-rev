"""Rate limiting middleware for the DevRev MCP Server HTTP transports."""

from __future__ import annotations

import logging
import threading
import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# Maximum number of tracked client buckets before eviction
_MAX_BUCKETS = 10_000


class TokenBucket:
    """Thread-safe token bucket rate limiter for a single client.

    Args:
        rate: Tokens added per second.
        capacity: Maximum tokens in the bucket.
    """

    def __init__(self, rate: float, capacity: float) -> None:
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()

    def consume(self) -> bool:
        """Try to consume one token (thread-safe).

        Returns:
            True if a token was consumed, False if rate limited.
        """
        with self._lock:
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
        with self._lock:
            if self.tokens >= 1.0:
                return 0.0
            if self.rate <= 0:
                return 60.0  # Fallback: suggest 60s if rate is zero
            return (1.0 - self.tokens) / self.rate


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces per-client rate limiting using token bucket algorithm.

    Rate limits are tracked per client IP address. The MCP session ID is used
    if available (from Mcp-Session-Id header), otherwise falls back to client IP.

    When requests_per_minute is 0, rate limiting is disabled entirely.

    Args:
        app: The ASGI application.
        requests_per_minute: Maximum requests per minute per client. 0 to disable.
        skip_paths: Paths to skip rate limiting for (e.g., /health).
    """

    def __init__(
        self,
        app: Any,
        requests_per_minute: int = 120,
        skip_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._rpm = requests_per_minute
        self._rate = requests_per_minute / 60.0 if requests_per_minute > 0 else 0.0
        self._capacity = float(max(requests_per_minute, 1))
        self._buckets: OrderedDict[str, TokenBucket] = OrderedDict()
        self._buckets_lock = threading.Lock()
        self._skip_paths = skip_paths or {"/health"}

    def _get_or_create_bucket(self, key: str) -> TokenBucket:
        """Get or create a token bucket for the given client key.

        Uses LRU eviction to prevent unbounded memory growth.
        """
        with self._buckets_lock:
            if key in self._buckets:
                # Move to end (most recently used)
                self._buckets.move_to_end(key)
                return self._buckets[key]

            # Create new bucket
            bucket = TokenBucket(self._rate, self._capacity)
            self._buckets[key] = bucket

            # Evict oldest entries if over limit
            while len(self._buckets) > _MAX_BUCKETS:
                self._buckets.popitem(last=False)

            return bucket

    def _get_client_key(self, request: Request) -> str:
        """Get a unique key for the client.

        Uses MCP session ID if available, otherwise client IP.
        """
        session_id = request.headers.get("mcp-session-id")
        if session_id:
            return f"session:{session_id}"
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Check rate limit before processing request.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware/handler in the chain.

        Returns:
            The response from the next handler, or a 429 error response.
        """
        # Skip rate limiting for health checks, OPTIONS, and when disabled
        if request.url.path in self._skip_paths or request.method == "OPTIONS" or self._rpm <= 0:
            response: Response = await call_next(request)
            return response

        client_key = self._get_client_key(request)
        bucket = self._get_or_create_bucket(client_key)

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

        response = await call_next(request)
        return response
