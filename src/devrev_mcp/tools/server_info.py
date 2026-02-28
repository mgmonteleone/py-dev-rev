"""MCP tool for DevRev server information and version checking."""

from __future__ import annotations

import logging
import platform
import sys
import time
from typing import Any

import httpx
from mcp.server.fastmcp import Context

from devrev_mcp import __version__
from devrev_mcp.server import mcp

logger = logging.getLogger(__name__)

# PyPI package name for version lookups
_PYPI_PACKAGE_NAME = "devrev-Python-SDK"
_PYPI_URL = f"https://pypi.org/pypi/{_PYPI_PACKAGE_NAME}/json"
_PYPI_TIMEOUT = 5.0

# Static metadata
_GITHUB_URL = "https://github.com/mgmonteleone/py-dev-rev"
_DOCS_URL = "https://mgmonteleone.github.io/py-dev-rev/"


def _compare_versions(current: str, latest: str) -> bool | None:
    """Compare two version strings. Returns True if current >= latest."""
    try:
        from packaging.version import Version

        return Version(current) >= Version(latest)
    except Exception:
        # Catches ImportError (packaging not installed) and InvalidVersion (malformed version)
        pass
    # Fallback: simple tuple comparison
    try:
        current_parts = tuple(int(x) for x in current.split("."))
        latest_parts = tuple(int(x) for x in latest.split("."))
        return current_parts >= latest_parts
    except (ValueError, AttributeError):
        return None


async def _fetch_latest_pypi_version() -> str | None:
    """Fetch the latest version from PyPI. Returns None on failure."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(_PYPI_URL, timeout=_PYPI_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            version = data.get("info", {}).get("version")
            return str(version) if version is not None else None
    except Exception:
        logger.debug("Failed to fetch latest version from PyPI", exc_info=True)
        return None


@mcp.tool()
async def devrev_server_info(ctx: Context[Any, Any, Any]) -> dict[str, Any]:
    """Get DevRev MCP Server information including version, capabilities, and update status.

    Returns server version, enabled features, uptime, and checks PyPI for the
    latest published version so you can tell the user whether they are up to date.

    Use this tool when asked about the MCP server version, capabilities, or status.
    """
    from devrev_mcp.middleware.health import _start_time

    app = ctx.request_context.lifespan_context

    # Calculate uptime
    uptime_seconds = int(time.monotonic() - _start_time) if _start_time is not None else 0

    # Fetch latest version from PyPI
    latest_version = await _fetch_latest_pypi_version()
    is_latest = _compare_versions(__version__, latest_version) if latest_version else None

    return {
        "server": {
            "name": app.config.server_name,
            "version": __version__,
            "uptime_seconds": uptime_seconds,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
        },
        "capabilities": {
            "beta_tools_enabled": app.config.enable_beta_tools,
            "destructive_tools_enabled": app.config.enable_destructive_tools,
            "auth_mode": app.config.auth_mode,
            "transport": app.config.transport,
            "audit_logging": app.config.audit_log_enabled,
            "rate_limit_rpm": app.config.rate_limit_rpm,
        },
        "update_status": {
            "current_version": __version__,
            "latest_version": latest_version or "unknown",
            "is_latest": is_latest,
            "pypi_package": _PYPI_PACKAGE_NAME,
        },
        "links": {
            "github": _GITHUB_URL,
            "documentation": _DOCS_URL,
            "pypi": f"https://pypi.org/project/{_PYPI_PACKAGE_NAME}/",
        },
    }
