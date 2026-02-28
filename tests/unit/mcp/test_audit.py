"""Tests for the MCP server audit logging module."""

from __future__ import annotations

import logging
import os

import pytest

# Set DEVREV_API_TOKEN at module level before imports to prevent SDK config errors
# This is required because the import triggers config loading
os.environ.setdefault("DEVREV_API_TOKEN", "test-token")

from devrev_mcp.middleware.audit import AuditLogger, classify_tool


@pytest.fixture(autouse=True)
def _mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set required environment variables for tests and ensure cleanup."""
    monkeypatch.setenv("DEVREV_API_TOKEN", "test-token-value")


class TestClassifyTool:
    """Tests for the classify_tool function."""

    def test_read_operations(self) -> None:
        """Verify tools ending in _list, _get, _count, _export are classified as read."""
        assert classify_tool("devrev_accounts_list") == "read"
        assert classify_tool("devrev_works_get") == "read"
        assert classify_tool("devrev_works_count") == "read"
        assert classify_tool("devrev_works_export") == "read"
        assert classify_tool("devrev_conversations_list") == "read"
        assert classify_tool("devrev_articles_get") == "read"

    def test_write_operations(self) -> None:
        """Verify tools ending in _create, _update, _merge, _transition are classified as write."""
        assert classify_tool("devrev_works_create") == "write"
        assert classify_tool("devrev_accounts_update") == "write"
        assert classify_tool("devrev_accounts_merge") == "write"
        assert classify_tool("devrev_slas_transition") == "write"
        assert classify_tool("devrev_articles_create") == "write"
        assert classify_tool("devrev_groups_update") == "write"

    def test_delete_operations(self) -> None:
        """Verify tools ending in _delete are classified as delete."""
        assert classify_tool("devrev_accounts_delete") == "delete"
        assert classify_tool("devrev_works_delete") == "delete"
        assert classify_tool("devrev_articles_delete") == "delete"

    def test_search_operations(self) -> None:
        """Verify tools containing 'search' or 'recommendations' are classified as search."""
        assert classify_tool("devrev_search_hybrid") == "search"
        assert classify_tool("devrev_search_core") == "search"
        assert classify_tool("devrev_recommendations_reply") == "search"
        assert classify_tool("devrev_recommendations_chat") == "search"

    def test_other_operations(self) -> None:
        """Verify unknown tools are classified as other."""
        assert classify_tool("devrev_unknown_tool") == "other"
        assert classify_tool("some_custom_tool") == "other"
        assert classify_tool("devrev_accounts") == "other"  # No suffix match


class TestAuditLogger:
    """Tests for the AuditLogger class."""

    @pytest.fixture
    def audit(self) -> AuditLogger:
        """Create a fresh AuditLogger instance for each test."""
        return AuditLogger(enabled=True)

    def test_log_auth_success_emits_structured_event(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify auth_success events contain all required structured fields."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_success(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                client_ip="192.168.1.1",
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]

        # Verify structured fields
        assert record.event_type == "audit"
        assert record.action == "auth_success"
        assert record.outcome == "success"
        assert record.user["id"] == "don:identity:dvrv-us-1:devo/1:devu/123"
        assert record.user["email"] == "user@example.com"
        assert record.user["pat_hash"] == "sha256:abc123"
        assert record.request["client_ip"] == "192.168.1.1"
        assert record.message == "Authentication successful"

    def test_log_auth_failure_emits_structured_event(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify auth_failure events contain all required structured fields."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_failure(
                reason="invalid_token",
                client_ip="192.168.1.1",
                email="user@example.com",
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]

        # Verify structured fields
        assert record.event_type == "audit"
        assert record.action == "auth_failure"
        assert record.outcome == "failure"
        assert record.error_message == "invalid_token"
        assert record.request["client_ip"] == "192.168.1.1"
        assert "Authentication failed: invalid_token" in record.message

    def test_log_auth_failure_includes_email_when_provided(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify email appears in user dict when provided to auth_failure."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_failure(
                reason="forbidden_domain",
                client_ip="192.168.1.1",
                email="user@badomain.com",
            )

        record = caplog.records[0]
        assert hasattr(record, "user")
        assert record.user["email"] == "user@badomain.com"

    def test_log_auth_failure_excludes_email_when_not_provided(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify no user dict when email is None in auth_failure."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_failure(
                reason="missing_token",
                client_ip="192.168.1.1",
                email=None,
            )

        record = caplog.records[0]
        assert not hasattr(record, "user")

    def test_log_tool_invocation_emits_structured_event(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify tool_invocation events contain all required structured fields."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_tool_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                tool_name="devrev_accounts_list",
                tool_category="read",
                client_ip="192.168.1.1",
                session_id="session-xyz",
                outcome="success",
                duration_ms=250,
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]

        # Verify structured fields
        assert record.event_type == "audit"
        assert record.action == "tool_invocation"
        assert record.outcome == "success"
        assert record.user["id"] == "don:identity:dvrv-us-1:devo/1:devu/123"
        assert record.user["email"] == "user@example.com"
        assert record.user["pat_hash"] == "sha256:abc123"
        assert record.tool["name"] == "devrev_accounts_list"
        assert record.tool["category"] == "read"
        assert record.request["client_ip"] == "192.168.1.1"
        assert record.request["session_id"] == "session-xyz"
        assert record.duration_ms == 250
        assert "Tool invocation: devrev_accounts_list (success)" in record.message

    def test_log_tool_invocation_includes_error_on_failure(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify error_message appears on tool invocation failure."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_tool_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                tool_name="devrev_works_create",
                tool_category="write",
                client_ip="192.168.1.1",
                session_id="session-xyz",
                outcome="failure",
                duration_ms=150,
                error_message="Validation error: missing required field 'title'",
            )

        record = caplog.records[0]
        assert record.outcome == "failure"
        assert record.error_message == "Validation error: missing required field 'title'"
        assert "Tool invocation: devrev_works_create (failure)" in record.message

    def test_disabled_logger_does_not_emit(self, caplog: pytest.LogCaptureFixture) -> None:
        """Verify disabled logger does not emit any log records."""
        audit = AuditLogger(enabled=False)

        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_success(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                client_ip="192.168.1.1",
            )
            audit.log_auth_failure(
                reason="invalid_token",
                client_ip="192.168.1.1",
            )
            audit.log_tool_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                tool_name="devrev_accounts_list",
                tool_category="read",
                client_ip="192.168.1.1",
                session_id="session-xyz",
                outcome="success",
                duration_ms=250,
            )

        # No logs should be emitted
        assert len(caplog.records) == 0

    def test_enabled_property(self) -> None:
        """Test enabled property getter and setter."""
        audit = AuditLogger(enabled=True)
        assert audit.enabled is True

        audit.enabled = False
        assert audit.enabled is False

        audit.enabled = True
        assert audit.enabled is True

    def test_event_type_is_always_audit(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify all event types have event_type='audit'."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_success(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                client_ip="192.168.1.1",
            )
            audit.log_auth_failure(
                reason="invalid_token",
                client_ip="192.168.1.1",
            )
            audit.log_tool_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                tool_name="devrev_accounts_list",
                tool_category="read",
                client_ip="192.168.1.1",
                session_id="session-xyz",
                outcome="success",
                duration_ms=250,
            )

        # All three records should have event_type="audit"
        assert len(caplog.records) == 3
        for record in caplog.records:
            assert record.event_type == "audit"

    def test_no_raw_token_in_logs(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify no raw token leaks into logs, only pat_hash is logged."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_success(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123def456",
                client_ip="192.168.1.1",
            )

        record = caplog.records[0]
        # Verify pat_hash is present
        assert record.user["pat_hash"] == "sha256:abc123def456"

        # Verify the log message and record don't contain raw token patterns
        # (This is a sanity check - the API doesn't expose raw tokens to this layer)
        log_text = record.getMessage()
        assert "pat_" not in log_text.lower() or "pat_hash" in log_text.lower()

    def test_multiple_tool_invocations_logged_separately(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify multiple tool invocations create separate log records."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_tool_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                tool_name="devrev_accounts_list",
                tool_category="read",
                client_ip="192.168.1.1",
                session_id="session-xyz",
                outcome="success",
                duration_ms=250,
            )
            audit.log_tool_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                tool_name="devrev_works_create",
                tool_category="write",
                client_ip="192.168.1.1",
                session_id="session-xyz",
                outcome="success",
                duration_ms=500,
            )

        assert len(caplog.records) == 2
        assert caplog.records[0].tool["name"] == "devrev_accounts_list"
        assert caplog.records[0].duration_ms == 250
        assert caplog.records[1].tool["name"] == "devrev_works_create"
        assert caplog.records[1].duration_ms == 500
