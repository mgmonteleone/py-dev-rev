"""Health check endpoint for the DevRev MCP Server."""

from __future__ import annotations

import logging
import time

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

logger = logging.getLogger(__name__)

# Server start time — set when init_start_time() is called during server startup
_start_time: float | None = None


def init_start_time() -> None:
    """Initialize the server start time. Call this during server startup."""
    global _start_time  # noqa: PLW0603
    _start_time = time.monotonic()


async def health_check(request: Request) -> JSONResponse:  # noqa: ARG001
    """Health check endpoint.

    Returns server status, uptime, and version information.
    Does not check DevRev API connectivity (that would add latency
    and could cause cascading failures).

    Args:
        request: The incoming HTTP request (required by Starlette route signature).

    Returns:
        JSON response with health status.
    """
    from devrev_mcp import __version__

    uptime_seconds = int(time.monotonic() - _start_time) if _start_time is not None else 0

    return JSONResponse(
        {
            "status": "healthy",
            "server": "devrev-mcp-server",
            "version": __version__,
            "uptime_seconds": uptime_seconds,
        }
    )


def health_route() -> Route:
    """Create the health check route.

    Returns:
        A Starlette Route for the /health endpoint.
    """
    return Route("/health", health_check, methods=["GET"])
