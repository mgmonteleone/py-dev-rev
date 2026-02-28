"""Authentication middleware for the DevRev MCP Server HTTP transports."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import secrets
import time
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from devrev import AsyncDevRevClient
from devrev.exceptions import DevRevError
from devrev_mcp.middleware.audit import audit_logger

logger = logging.getLogger(__name__)


def _extract_request_metadata(request: Request) -> dict[str, str]:
    """Extract audit-relevant metadata from an HTTP request.

    Args:
        request: The incoming HTTP request.

    Returns:
        Dictionary containing user_agent, x_forwarded_for, and trace_id.
    """
    trace_context = request.headers.get("x-cloud-trace-context", "")
    # Extract trace ID (format: TRACE_ID/SPAN_ID;o=TRACE_TRUE)
    trace_id = trace_context.split("/")[0].strip() if trace_context else ""
    return {
        "user_agent": request.headers.get("user-agent", "")[:512],
        "x_forwarded_for": request.headers.get("x-forwarded-for", ""),
        "trace_id": trace_id,
    }


# Context variable for storing the current user's DevRev PAT
_current_devrev_pat: ContextVar[str | None] = ContextVar("_current_devrev_pat", default=None)

# Context variable for storing the current user's DevRev client (per-request)
_current_devrev_client: ContextVar[AsyncDevRevClient | None] = ContextVar(
    "_current_devrev_client", default=None
)

# Context variable for audit metadata (set by auth middleware, read by tool audit wrapper)
_current_user_audit_info: ContextVar[dict[str, str] | None] = ContextVar(
    "_current_user_audit_info", default=None
)


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
        if not token:
            raise ValueError("BearerTokenMiddleware requires a non-empty token")
        self._token = token
        self._skip_paths = skip_paths or {"/health"}

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Validate Bearer token on incoming requests.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware/handler in the chain.

        Returns:
            The response from the next handler, or a 401/403 error response.
        """
        # Skip auth for health checks and CORS preflight
        if request.url.path in self._skip_paths or request.method == "OPTIONS":
            response: Response = await call_next(request)
            return response

        meta = _extract_request_metadata(request)

        auth_header = request.headers.get("authorization", "")
        if not auth_header:
            logger.warning(
                "Missing Authorization header from %s",
                request.client.host if request.client else "unknown",
            )
            audit_logger.log_auth_failure(
                reason="missing_authorization_header",
                client_ip=request.client.host if request.client else "unknown",
                **meta,
            )
            return JSONResponse(
                status_code=401,
                content={"error": "Missing Authorization header"},
            )

        # Expect "Bearer <token>"
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("Invalid Authorization header format")
            audit_logger.log_auth_failure(
                reason="invalid_authorization_format",
                client_ip=request.client.host if request.client else "unknown",
                **meta,
            )
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid Authorization header format. Expected: Bearer <token>"},
            )

        provided_token = parts[1].strip()
        if not secrets.compare_digest(provided_token.encode("utf-8"), self._token.encode("utf-8")):
            logger.warning("Invalid Bearer token")
            audit_logger.log_auth_failure(
                reason="invalid_bearer_token",
                client_ip=request.client.host if request.client else "unknown",
                **meta,
            )
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid Bearer token"},
            )

        # Log successful authentication
        audit_logger.log_auth_success(
            user_id="static-token",
            email="static-token",
            pat_hash=f"sha256:{hashlib.sha256(provided_token.encode()).hexdigest()}",
            client_ip=request.client.host if request.client else "unknown",
            **meta,
        )

        # Set context var for tool audit logging
        pat_hash_prefixed = f"sha256:{hashlib.sha256(provided_token.encode()).hexdigest()}"
        audit_info_token = _current_user_audit_info.set(
            {
                "user_id": "static-token",
                "email": "static-token",
                "pat_hash": pat_hash_prefixed,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": meta["user_agent"],
                "x_forwarded_for": meta["x_forwarded_for"],
                "trace_id": meta["trace_id"],
            }
        )

        try:
            response = await call_next(request)
            return response
        finally:
            _current_user_audit_info.reset(audit_info_token)


@dataclass
class _CachedIdentity:
    """Cached user identity from DevRev PAT validation.

    Attributes:
        user_id: DevRev user ID.
        email: User email address.
        display_name: User display name.
        expires_at: Unix timestamp when this cache entry expires.
    """

    user_id: str
    email: str
    display_name: str
    expires_at: float


class DevRevPATAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that validates per-user DevRev PAT authentication.

    Validates the Authorization header by calling the DevRev API to verify
    the PAT and retrieve user identity. Caches validation results to reduce
    API calls.

    Args:
        app: The ASGI application.
        allowed_domains: List of allowed email domains (e.g., ["augmentcode.com"]).
                        If None or empty, all domains are allowed.
        cache_ttl_seconds: TTL for cached validation results (default: 300).
        api_version: DevRev API version to use (default: None for public API).
        skip_paths: Paths to skip authentication for (e.g., /health).
    """

    def __init__(
        self,
        app: Any,
        allowed_domains: list[str] | None = None,
        cache_ttl_seconds: int = 300,
        api_version: str | None = None,
        skip_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._allowed_domains = [d.lstrip("@").lower() for d in (allowed_domains or [])]
        self._cache_ttl_seconds = cache_ttl_seconds
        self._api_version = api_version
        self._skip_paths = skip_paths or {"/health"}
        self._cache: dict[str, _CachedIdentity] = {}
        self._cache_lock = asyncio.Lock()

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Validate DevRev PAT on incoming requests.

        Args:
            request: The incoming HTTP request.
            call_next: The next middleware/handler in the chain.

        Returns:
            The response from the next handler, or a 401/403 error response.
        """
        # Skip auth for health checks and CORS preflight
        if request.url.path in self._skip_paths or request.method == "OPTIONS":
            response: Response = await call_next(request)
            return response

        meta = _extract_request_metadata(request)

        auth_header = request.headers.get("authorization", "")
        if not auth_header:
            logger.warning(
                "Missing Authorization header from %s",
                request.client.host if request.client else "unknown",
            )
            audit_logger.log_auth_failure(
                reason="missing_authorization_header",
                client_ip=request.client.host if request.client else "unknown",
                **meta,
            )
            return JSONResponse(
                status_code=401,
                content={"error": "Missing Authorization header"},
            )

        # Expect "Bearer <token>"
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("Invalid Authorization header format")
            audit_logger.log_auth_failure(
                reason="invalid_authorization_format",
                client_ip=request.client.host if request.client else "unknown",
                **meta,
            )
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid Authorization header format. Expected: Bearer <token>"},
            )

        token = parts[1].strip()
        if not token:
            logger.warning("Empty Bearer token provided")
            audit_logger.log_auth_failure(
                reason="empty_bearer_token",
                client_ip=request.client.host if request.client else "unknown",
                **meta,
            )
            return JSONResponse(
                status_code=401,
                content={"error": "Empty Bearer token. Expected: Bearer <token>"},
            )
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Check cache first
        identity = await self._get_cached_identity(token_hash)

        if identity is None:
            # Validate token against DevRev API
            identity = await self._validate_token(token, token_hash)
            if identity is None:
                audit_logger.log_auth_failure(
                    reason="invalid_devrev_pat",
                    client_ip=request.client.host if request.client else "unknown",
                    **meta,
                )
                return JSONResponse(
                    status_code=403,
                    content={"error": "Invalid DevRev PAT"},
                )

        # Check domain restriction
        if self._allowed_domains and not any(
            identity.email.lower().endswith(f"@{domain}") for domain in self._allowed_domains
        ):
            logger.warning(
                "User %s from disallowed domain attempted access",
                identity.email,
            )
            audit_logger.log_auth_failure(
                reason="forbidden_domain",
                client_ip=request.client.host if request.client else "unknown",
                email=identity.email,
                **meta,
            )
            return JSONResponse(
                status_code=403,
                content={"error": "Email domain not allowed"},
            )

        # Store identity in request state (hash only — never expose raw PAT)
        request.state.devrev_pat_hash = token_hash
        request.state.devrev_user_id = identity.user_id
        request.state.devrev_user_email = identity.email
        request.state.devrev_user_display_name = identity.display_name

        # Set context vars for access from tools
        audit_info_token = _current_user_audit_info.set(
            {
                "user_id": identity.user_id,
                "email": identity.email,
                "pat_hash": f"sha256:{token_hash}",
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": meta["user_agent"],
                "x_forwarded_for": meta["x_forwarded_for"],
                "trace_id": meta["trace_id"],
            }
        )
        pat_token = _current_devrev_pat.set(token)

        logger.info(
            "Authenticated user: %s (%s)",
            identity.email,
            identity.display_name,
        )
        audit_logger.log_auth_success(
            user_id=identity.user_id,
            email=identity.email,
            pat_hash=f"sha256:{token_hash}",
            client_ip=request.client.host if request.client else "unknown",
            **meta,
        )

        try:
            response = await call_next(request)
            return response
        finally:
            # Close per-request client if one was created
            client = _current_devrev_client.get(None)
            if client is not None:
                await client.close()
            _current_devrev_client.set(None)
            _current_devrev_pat.reset(pat_token)
            _current_user_audit_info.reset(audit_info_token)

    async def _get_cached_identity(self, token_hash: str) -> _CachedIdentity | None:
        """Get cached identity if valid.

        Args:
            token_hash: SHA256 hash of the token.

        Returns:
            Cached identity if valid, None otherwise.
        """
        async with self._cache_lock:
            identity = self._cache.get(token_hash)
            if identity and identity.expires_at > time.time():
                return identity
            # Remove expired entry
            if identity:
                del self._cache[token_hash]
            return None

    async def _validate_token(self, token: str, token_hash: str) -> _CachedIdentity | None:
        """Validate token against DevRev API and cache result.

        Args:
            token: The DevRev PAT.
            token_hash: SHA256 hash of the token.

        Returns:
            Cached identity if validation succeeds, None otherwise.
        """
        client = None
        try:
            # Create temporary client with the user's PAT
            if self._api_version == "beta":
                from devrev import APIVersion

                client = AsyncDevRevClient(api_token=token, api_version=APIVersion.BETA)
            else:
                client = AsyncDevRevClient(api_token=token)

            # Call dev_users.self() to validate token and get user identity
            user = await client.dev_users.self()

            # Create cached identity
            identity = _CachedIdentity(
                user_id=user.id,
                email=user.email or "",
                display_name=user.display_name or "",
                expires_at=time.time() + self._cache_ttl_seconds,
            )

            # Store in cache with LRU eviction
            async with self._cache_lock:
                # Evict oldest entries if cache is too large
                if len(self._cache) >= 1000:
                    # Remove entries with earliest expiration
                    sorted_entries = sorted(
                        self._cache.items(),
                        key=lambda x: x[1].expires_at,
                    )
                    # Remove oldest 10%
                    for old_hash, _ in sorted_entries[:100]:
                        del self._cache[old_hash]

                self._cache[token_hash] = identity

            return identity

        except DevRevError as e:
            logger.warning("DevRev PAT validation failed: %s", str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error during PAT validation: %s", str(e))
            return None
        finally:
            if client:
                await client.close()
