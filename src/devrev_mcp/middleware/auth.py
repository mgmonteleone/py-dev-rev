"""Authentication middleware for the DevRev MCP Server HTTP transports."""

from __future__ import annotations

import logging
import secrets
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """Middleware that validates Bearer token authentication for HTTP transports.

    Validates the Authorization header against a configured token.
    Skips authentication for health check and OPTIONS (CORS preflight) requests.

    Args:
        app: The ASGI application.
        token: The expected Bearer token value.
        skip_paths: Paths to skip authentication for (e.g., /health).
    """

    def __init__(
        self,
        app: Any,
        token: str,
        skip_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._token = token
        self._skip_paths = skip_paths or {"/health"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate Bearer token on incoming requests.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware/handler in the chain.

        Returns:
            The response from the next handler, or a 401/403 error response.
        """
        # Skip auth for health checks and CORS preflight
        if request.url.path in self._skip_paths or request.method == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get("authorization", "")
        if not auth_header:
            logger.warning(
                "Missing Authorization header from %s",
                request.client.host if request.client else "unknown",
            )
            return JSONResponse(
                status_code=401,
                content={"error": "Missing Authorization header"},
            )

        # Expect "Bearer <token>"
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("Invalid Authorization header format")
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid Authorization header format. Expected: Bearer <token>"},
            )

        provided_token = parts[1].strip()
        if not secrets.compare_digest(provided_token.encode("utf-8"), self._token.encode("utf-8")):
            logger.warning("Invalid Bearer token")
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid Bearer token"},
            )

        return await call_next(request)
