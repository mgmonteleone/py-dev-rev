"""DevRev MCP Server — main server setup and lifecycle management."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from devrev import APIVersion, AsyncDevRevClient
from devrev_mcp import __version__
from devrev_mcp.config import MCPServerConfig
from devrev_mcp.middleware.auth import _current_devrev_client, _current_devrev_pat
from devrev_mcp.middleware.health import init_start_time

logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context shared across all MCP tool invocations.

    Attributes:
        config: The MCP server configuration.
        _api_version: The DevRev API version to use.
        _stdio_client: Shared client for stdio transport (None for HTTP with devrev-pat).
    """

    config: MCPServerConfig
    _api_version: APIVersion
    _stdio_client: AsyncDevRevClient | None = None

    def get_client(self) -> AsyncDevRevClient:
        """Get a DevRev client for the current request.

        For HTTP transports with devrev-pat auth: creates/returns a client
        using the user's PAT from the context variable (set by middleware).

        For stdio transport: returns the shared client (backward compat).
        For static-token auth: returns the shared client.

        Returns:
            AsyncDevRevClient configured for the current request.

        Raises:
            RuntimeError: If no client is available (missing PAT in devrev-pat mode).
        """
        # Stdio or static-token mode: use shared client
        if self._stdio_client is not None:
            return self._stdio_client

        # Check for cached per-request client first
        client = _current_devrev_client.get()
        if client is not None:
            return client

        # HTTP with devrev-pat mode: create per-request client from PAT
        pat = _current_devrev_pat.get()
        if pat:
            client = AsyncDevRevClient(api_token=pat, api_version=self._api_version)
            _current_devrev_client.set(client)
            return client

        raise RuntimeError(
            "No DevRev client available. For HTTP transports with devrev-pat mode, "
            "ensure a valid DevRev PAT is provided in the Authorization header."
        )


@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage the MCP server lifecycle.

    Creates the DevRev client and configuration on startup,
    and ensures proper cleanup on shutdown.

    Args:
        _server: The FastMCP server instance (unused).

    Yields:
        AppContext with initialized client and config.
    """
    config = MCPServerConfig()
    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO))

    # Mark server start time for health endpoint uptime calculation
    init_start_time()

    logger.info(
        "Starting %s v%s (transport=%s, auth_mode=%s, beta_tools=%s)",
        config.server_name,
        __version__,
        config.transport,
        config.auth_mode,
        config.enable_beta_tools,
    )

    # Use beta API version only if beta tools are enabled
    api_version = APIVersion.BETA if config.enable_beta_tools else APIVersion.PUBLIC

    # For stdio or static-token mode, create a shared client
    if config.transport == "stdio" or config.auth_mode == "static-token":
        client = AsyncDevRevClient(api_version=api_version)
        try:
            yield AppContext(config=config, _api_version=api_version, _stdio_client=client)
        finally:
            await client.close()
            logger.info("DevRev MCP Server shut down.")
    else:
        # For devrev-pat mode, no shared client needed
        yield AppContext(config=config, _api_version=api_version)
        logger.info("DevRev MCP Server shut down.")


def _build_transport_security(config: MCPServerConfig) -> TransportSecuritySettings | None:
    """Build transport security settings from config.

    Only applies to HTTP transports (streamable-http, sse).
    Returns None for stdio transport.
    """
    if config.transport == "stdio":
        return None
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=config.enable_dns_rebinding_protection,
        allowed_hosts=config.allowed_hosts,
        allowed_origins=config.cors_allowed_origins,
    )


# Create the FastMCP server instance
_config = MCPServerConfig()
_transport_security = _build_transport_security(_config)

mcp = FastMCP(
    _config.server_name,
    lifespan=app_lifespan,
    host=_config.host,
    port=_config.port,
    transport_security=_transport_security,
)

# ----- Register HTTP middleware (only for non-stdio transports) -----
# FastMCP creates its Starlette app lazily inside streamable_http_app() and
# sse_app(). We wrap those methods so that after the Starlette app is created,
# we inject our health route and middleware into it.
#
# NOTE: The closures below capture `_config` (the module-level MCPServerConfig
# instance). This config is frozen at import time. Runtime config changes (e.g.,
# from CLI args in __main__.py that set env vars before importing this module)
# are picked up because __main__.py sets env vars *before* importing server.
if _config.transport != "stdio":
    import functools

    from devrev_mcp.middleware.auth import BearerTokenMiddleware
    from devrev_mcp.middleware.health import health_route
    from devrev_mcp.middleware.rate_limit import RateLimitMiddleware

    def _inject_middleware(starlette_app: Any) -> Any:
        """Add health route, auth, and rate limiting to a Starlette app."""
        logger.debug(
            "Injecting middleware: health_route=True, auth_mode=%s, rate_limit=%s (rpm=%d)",
            _config.auth_mode,
            _config.rate_limit_rpm > 0,
            _config.rate_limit_rpm,
        )
        # Insert health route at the beginning so it's matched first
        starlette_app.routes.insert(0, health_route())

        # Add rate limiting middleware (outermost — runs first)
        if _config.rate_limit_rpm > 0:
            starlette_app.add_middleware(
                RateLimitMiddleware,
                requests_per_minute=_config.rate_limit_rpm,
            )

        # Add auth middleware (inner — runs after rate limiting)
        if _config.auth_mode == "devrev-pat":
            from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

            starlette_app.add_middleware(
                DevRevPATAuthMiddleware,
                allowed_domains=_config.auth_allowed_domains,
                cache_ttl_seconds=_config.auth_cache_ttl_seconds,
                api_version="beta" if _config.enable_beta_tools else None,
            )
        elif _config.auth_token is not None:
            starlette_app.add_middleware(
                BearerTokenMiddleware,
                token=_config.auth_token.get_secret_value(),
            )

        return starlette_app

    # Wrap streamable_http_app
    _original_streamable_http_app = mcp.streamable_http_app

    @functools.wraps(_original_streamable_http_app)
    def _patched_streamable_http_app(*args: Any, **kwargs: Any) -> Any:
        app = _original_streamable_http_app(*args, **kwargs)
        return _inject_middleware(app)

    mcp.streamable_http_app = _patched_streamable_http_app  # type: ignore[method-assign]

    # Wrap sse_app
    _original_sse_app = mcp.sse_app

    @functools.wraps(_original_sse_app)
    def _patched_sse_app(*args: Any, **kwargs: Any) -> Any:
        app = _original_sse_app(*args, **kwargs)
        return _inject_middleware(app)

    mcp.sse_app = _patched_sse_app  # type: ignore[method-assign]


# ----- Register tool modules -----
# IMPORTANT: These imports MUST come after the middleware patching above.
# FastMCP tool registration happens at import time via `@mcp.tool()` decorators.
# The `mcp` instance must be fully configured (including middleware wrapping)
# before any tool modules are imported, otherwise tool registration could
# interact with an incompletely configured server.
#
# All tool modules are always imported. Each module internally guards
# destructive tools (create/update/delete) using `_config.enable_destructive_tools`.
# Beta tools check `_config.enable_beta_tools`.
from devrev_mcp.tools import accounts as _accounts_tools  # noqa: E402, F401
from devrev_mcp.tools import articles as _articles_tools  # noqa: E402, F401
from devrev_mcp.tools import conversations as _conversations_tools  # noqa: E402, F401
from devrev_mcp.tools import engagements as _engagements_tools  # noqa: E402, F401
from devrev_mcp.tools import groups as _groups_tools  # noqa: E402, F401
from devrev_mcp.tools import incidents as _incidents_tools  # noqa: E402, F401
from devrev_mcp.tools import links as _links_tools  # noqa: E402, F401
from devrev_mcp.tools import parts as _parts_tools  # noqa: E402, F401
from devrev_mcp.tools import slas as _slas_tools  # noqa: E402, F401
from devrev_mcp.tools import tags as _tags_tools  # noqa: E402, F401
from devrev_mcp.tools import timeline as _timeline_tools  # noqa: E402, F401
from devrev_mcp.tools import users as _users_tools  # noqa: E402, F401
from devrev_mcp.tools import works as _works_tools  # noqa: E402, F401

# Beta tools (only if beta tools are enabled)
if _config.enable_beta_tools:
    from devrev_mcp.tools import recommendations as _recommendations_tools  # noqa: E402, F401
    from devrev_mcp.tools import search as _search_tools  # noqa: E402, F401

# ----- Register resource modules -----
# ----- Register prompt modules -----
from devrev_mcp.prompts import escalation as _escalation_prompts  # noqa: E402, F401
from devrev_mcp.prompts import investigate as _investigate_prompts  # noqa: E402, F401
from devrev_mcp.prompts import response as _response_prompts  # noqa: E402, F401
from devrev_mcp.prompts import summarize as _summarize_prompts  # noqa: E402, F401
from devrev_mcp.prompts import triage as _triage_prompts  # noqa: E402, F401
from devrev_mcp.resources import account as _account_resources  # noqa: E402, F401
from devrev_mcp.resources import article as _article_resources  # noqa: E402, F401
from devrev_mcp.resources import conversation as _conversation_resources  # noqa: E402, F401
from devrev_mcp.resources import part as _part_resources  # noqa: E402, F401
from devrev_mcp.resources import ticket as _ticket_resources  # noqa: E402, F401
from devrev_mcp.resources import user as _user_resources  # noqa: E402, F401

# ----- Audit logging for tool invocations -----
if _config.audit_log_enabled:
    import functools
    import time as _time

    from devrev_mcp.middleware.audit import audit_logger, classify_tool
    from devrev_mcp.middleware.auth import _current_user_audit_info

    def _wrap_tool_with_audit(tool_name: str, original_fn: Any) -> Any:
        """Wrap an MCP tool function with audit logging."""

        @functools.wraps(original_fn)
        async def _audited_tool(*args: Any, **kwargs: Any) -> Any:
            audit_info = _current_user_audit_info.get()
            start_time = _time.monotonic()
            outcome = "success"
            error_msg = None
            try:
                result = await original_fn(*args, **kwargs)
                return result
            except Exception as e:
                outcome = "failure"
                error_msg = str(e)
                raise
            finally:
                duration_ms = int((_time.monotonic() - start_time) * 1000)
                if audit_info:
                    audit_logger.log_tool_invocation(
                        user_id=audit_info.get("user_id", "unknown"),
                        email=audit_info.get("email", "unknown"),
                        pat_hash=audit_info.get("pat_hash", "unknown"),
                        tool_name=tool_name,
                        tool_category=classify_tool(tool_name),
                        client_ip=audit_info.get("client_ip", "unknown"),
                        session_id="",  # Session ID is not easily available in this context
                        outcome=outcome,
                        duration_ms=duration_ms,
                        error_message=error_msg,
                    )

        return _audited_tool

    # Wrap all registered tools with audit logging
    if hasattr(mcp, "_tool_manager") and hasattr(mcp._tool_manager, "_tools"):
        for _tool_name, _tool in mcp._tool_manager._tools.items():
            if hasattr(_tool, "fn"):
                _tool.fn = _wrap_tool_with_audit(_tool_name, _tool.fn)
        logger.info("Audit logging enabled for %d tools", len(mcp._tool_manager._tools))
    else:
        logger.warning("Could not enable tool audit logging: tool manager not accessible")
