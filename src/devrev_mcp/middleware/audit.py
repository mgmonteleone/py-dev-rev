"""Structured audit logging for the DevRev MCP Server.

Provides compliance-grade audit trails for authentication events
and MCP tool invocations. Audit events are emitted as structured
JSON log entries with event_type="audit" for downstream filtering.

All audit events include structured fields that are automatically
serialized by the JSONFormatter in src/devrev/utils/logging.py.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Tool category classification rules
_TOOL_CATEGORIES: dict[str, str] = {
    "list": "read",
    "get": "read",
    "count": "read",
    "export": "read",
    "create": "write",
    "update": "write",
    "merge": "write",
    "transition": "write",
    "delete": "delete",
}


def classify_tool(tool_name: str) -> str:
    """Classify an MCP tool name into an audit category.

    Categories are determined by tool name patterns:
    - Tools ending in _list, _get, _count, _export: "read"
    - Tools ending in _create: "write"
    - Tools ending in _update, _merge, _transition: "write"
    - Tools ending in _delete: "delete"
    - Tools containing "search" or "recommendations": "search"
    - Default: "other"

    Args:
        tool_name: The MCP tool name (e.g., "devrev_accounts_list").

    Returns:
        The audit category: "read", "write", "delete", "search", or "other".

    Example:
        >>> classify_tool("devrev_accounts_list")
        'read'
        >>> classify_tool("devrev_works_create")
        'write'
        >>> classify_tool("devrev_search_hybrid")
        'search'
    """
    # Check for search/recommendations first
    if "search" in tool_name.lower() or "recommendations" in tool_name.lower():
        return "search"

    # Check suffix patterns
    for suffix, category in _TOOL_CATEGORIES.items():
        if tool_name.endswith(f"_{suffix}"):
            return category

    return "other"


class AuditLogger:
    """Structured audit event logger for compliance tracking.

    Emits audit events as structured log entries with event_type="audit"
    for filtering by Cloud Logging sinks or other log aggregation systems.

    All log events are emitted at INFO level with structured extra fields
    that are automatically serialized to JSON by the JSONFormatter.

    Attributes:
        enabled: Whether audit logging is enabled (default: True).

    Example:
        >>> from devrev_mcp.middleware.audit import audit_logger
        >>> audit_logger.log_auth_success(
        ...     user_id="don:identity:...",
        ...     email="user@example.com",
        ...     pat_hash="abc123",
        ...     client_ip="192.168.1.1"
        ... )
    """

    def __init__(self, *, enabled: bool = True) -> None:
        """Initialize the audit logger.

        Args:
            enabled: Whether audit logging is enabled (default: True).
        """
        self._enabled = enabled
        self._logger = logging.getLogger("devrev_mcp.audit")

    @property
    def enabled(self) -> bool:
        """Whether audit logging is currently enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable audit logging.

        Args:
            value: True to enable, False to disable.
        """
        self._enabled = value

    def log_auth_success(
        self,
        user_id: str,
        email: str,
        pat_hash: str,
        client_ip: str,
        user_agent: str = "",
        x_forwarded_for: str = "",
        trace_id: str = "",
    ) -> None:
        """Log a successful authentication event.

        Args:
            user_id: DevRev user ID (DON format).
            email: User email address.
            pat_hash: Hash of the Personal Access Token used.
            client_ip: Client IP address.
            user_agent: User-Agent header from the request.
            x_forwarded_for: X-Forwarded-For header from the request.
            trace_id: Trace ID extracted from x-cloud-trace-context header.

        Example:
            >>> audit_logger.log_auth_success(
            ...     user_id="don:identity:dvrv-us-1:devo/1:devu/123",
            ...     email="user@example.com",
            ...     pat_hash="sha256:abc123...",
            ...     client_ip="192.168.1.1",
            ...     user_agent="mcp-client/1.0",
            ...     x_forwarded_for="203.0.113.42",
            ...     trace_id="abc123def456789"
            ... )
        """
        if not self._enabled:
            return

        extra: dict[str, Any] = {
            "event_type": "audit",
            "action": "auth_success",
            "user": {"id": user_id, "email": email, "pat_hash": pat_hash},
            "request": {
                "client_ip": client_ip,
                "user_agent": user_agent,
                "x_forwarded_for": x_forwarded_for,
                "trace_id": trace_id,
            },
            "outcome": "success",
        }

        self._logger.info(
            "Authentication successful",
            extra=extra,
        )

    def log_auth_failure(
        self,
        reason: str,
        client_ip: str,
        email: str | None = None,
        user_agent: str = "",
        x_forwarded_for: str = "",
        trace_id: str = "",
    ) -> None:
        """Log a failed authentication attempt.

        Args:
            reason: Reason for authentication failure (e.g., "invalid_token", "forbidden_domain").
            client_ip: Client IP address.
            email: User email address if available (optional).
            user_agent: User-Agent header from the request.
            x_forwarded_for: X-Forwarded-For header from the request.
            trace_id: Trace ID extracted from x-cloud-trace-context header.

        Example:
            >>> audit_logger.log_auth_failure(
            ...     reason="invalid_token",
            ...     client_ip="192.168.1.1",
            ...     email="user@example.com",
            ...     user_agent="curl/7.88.1",
            ...     x_forwarded_for="198.51.100.5",
            ...     trace_id="trace-id-987"
            ... )
        """
        if not self._enabled:
            return

        extra: dict[str, Any] = {
            "event_type": "audit",
            "action": "auth_failure",
            "request": {
                "client_ip": client_ip,
                "user_agent": user_agent,
                "x_forwarded_for": x_forwarded_for,
                "trace_id": trace_id,
            },
            "outcome": "failure",
            "error_message": reason,
        }

        # Only include user dict if email is provided
        if email:
            extra["user"] = {"email": email}

        self._logger.info(
            "Authentication failed: %s",
            reason,
            extra=extra,
        )

    def log_tool_invocation(
        self,
        user_id: str,
        email: str,
        pat_hash: str,
        tool_name: str,
        tool_category: str,
        client_ip: str,
        session_id: str,
        outcome: str,
        duration_ms: int,
        error_message: str | None = None,
        user_agent: str = "",
        x_forwarded_for: str = "",
        trace_id: str = "",
    ) -> None:
        """Log an MCP tool invocation.

        Args:
            user_id: DevRev user ID (DON format).
            email: User email address.
            pat_hash: Hash of the Personal Access Token used.
            tool_name: Name of the MCP tool invoked.
            tool_category: Tool category (read, write, delete, search, other).
            client_ip: Client IP address.
            session_id: MCP session ID.
            outcome: "success" or "failure".
            duration_ms: Tool execution duration in milliseconds.
            error_message: Error message if outcome is "failure" (optional).
            user_agent: User-Agent header from the request.
            x_forwarded_for: X-Forwarded-For header from the request.
            trace_id: Trace ID extracted from x-cloud-trace-context header.

        Example:
            >>> audit_logger.log_tool_invocation(
            ...     user_id="don:identity:dvrv-us-1:devo/1:devu/123",
            ...     email="user@example.com",
            ...     pat_hash="sha256:abc123...",
            ...     tool_name="devrev_accounts_list",
            ...     tool_category="read",
            ...     client_ip="192.168.1.1",
            ...     session_id="session-xyz",
            ...     outcome="success",
            ...     duration_ms=250,
            ...     user_agent="mcp-client/1.0",
            ...     x_forwarded_for="203.0.113.42",
            ...     trace_id="abc123def456789"
            ... )
        """
        if not self._enabled:
            return

        extra: dict[str, Any] = {
            "event_type": "audit",
            "action": "tool_invocation",
            "user": {"id": user_id, "email": email, "pat_hash": pat_hash},
            "tool": {"name": tool_name, "category": tool_category},
            "request": {
                "client_ip": client_ip,
                "session_id": session_id,
                "user_agent": user_agent,
                "x_forwarded_for": x_forwarded_for,
                "trace_id": trace_id,
            },
            "outcome": outcome,
            "duration_ms": duration_ms,
        }

        if error_message:
            extra["error_message"] = error_message

        self._logger.info(
            "Tool invocation: %s (%s)",
            tool_name,
            outcome,
            extra=extra,
        )

    def log_resource_access(
        self,
        user_id: str,
        email: str,
        pat_hash: str,
        resource_uri: str,
        client_ip: str,
        outcome: str,
        duration_ms: int,
        error_message: str | None = None,
        user_agent: str = "",
        x_forwarded_for: str = "",
        trace_id: str = "",
    ) -> None:
        """Log an MCP resource access.

        Args:
            user_id: DevRev user ID (DON format).
            email: User email address.
            pat_hash: Hash of the Personal Access Token used.
            resource_uri: URI of the resource accessed (e.g., "devrev://account/123").
            client_ip: Client IP address.
            outcome: "success" or "failure".
            duration_ms: Resource access duration in milliseconds.
            error_message: Error message if outcome is "failure" (optional).
            user_agent: User-Agent header from the request.
            x_forwarded_for: X-Forwarded-For header from the request.
            trace_id: Trace ID extracted from x-cloud-trace-context header.
        """
        if not self._enabled:
            return

        extra: dict[str, Any] = {
            "event_type": "audit",
            "action": "resource_access",
            "user": {"id": user_id, "email": email, "pat_hash": pat_hash},
            "resource": {"uri": resource_uri},
            "request": {
                "client_ip": client_ip,
                "user_agent": user_agent,
                "x_forwarded_for": x_forwarded_for,
                "trace_id": trace_id,
            },
            "outcome": outcome,
            "duration_ms": duration_ms,
        }

        if error_message:
            extra["error_message"] = error_message

        self._logger.info(
            "Resource access: %s (%s)",
            resource_uri,
            outcome,
            extra=extra,
        )

    def log_prompt_invocation(
        self,
        user_id: str,
        email: str,
        pat_hash: str,
        prompt_name: str,
        client_ip: str,
        outcome: str,
        duration_ms: int,
        error_message: str | None = None,
        user_agent: str = "",
        x_forwarded_for: str = "",
        trace_id: str = "",
    ) -> None:
        """Log an MCP prompt invocation.

        Args:
            user_id: DevRev user ID (DON format).
            email: User email address.
            pat_hash: Hash of the Personal Access Token used.
            prompt_name: Name of the prompt invoked.
            client_ip: Client IP address.
            outcome: "success" or "failure".
            duration_ms: Prompt invocation duration in milliseconds.
            error_message: Error message if outcome is "failure" (optional).
            user_agent: User-Agent header from the request.
            x_forwarded_for: X-Forwarded-For header from the request.
            trace_id: Trace ID extracted from x-cloud-trace-context header.
        """
        if not self._enabled:
            return

        extra: dict[str, Any] = {
            "event_type": "audit",
            "action": "prompt_invocation",
            "user": {"id": user_id, "email": email, "pat_hash": pat_hash},
            "prompt": {"name": prompt_name},
            "request": {
                "client_ip": client_ip,
                "user_agent": user_agent,
                "x_forwarded_for": x_forwarded_for,
                "trace_id": trace_id,
            },
            "outcome": outcome,
            "duration_ms": duration_ms,
        }

        if error_message:
            extra["error_message"] = error_message

        self._logger.info(
            "Prompt invocation: %s (%s)",
            prompt_name,
            outcome,
            extra=extra,
        )


# Module-level singleton for easy import
audit_logger = AuditLogger()
