"""Tests for the MCP server audit logging module."""

from __future__ import annotations

import logging
import os
from unittest.mock import MagicMock

import pytest

# Set DEVREV_API_TOKEN at module level before imports to prevent SDK config errors
# This is required because the import triggers config loading
os.environ.setdefault("DEVREV_API_TOKEN", "test-token")

from devrev_mcp.middleware.audit import AuditLogger, classify_tool
from devrev_mcp.middleware.auth import _extract_request_metadata


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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
        assert record.request["user_agent"] == ""
        assert record.request["x_forwarded_for"] == ""
        assert record.request["trace_id"] == ""
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
        assert record.request["user_agent"] == ""
        assert record.request["x_forwarded_for"] == ""
        assert record.request["trace_id"] == ""
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
            )
            audit.log_auth_failure(
                reason="invalid_token",
                client_ip="192.168.1.1",
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
            )
            audit.log_auth_failure(
                reason="invalid_token",
                client_ip="192.168.1.1",
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
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
                user_agent="",
                x_forwarded_for="",
                trace_id="",
            )

        assert len(caplog.records) == 2
        assert caplog.records[0].tool["name"] == "devrev_accounts_list"
        assert caplog.records[0].duration_ms == 250
        assert caplog.records[1].tool["name"] == "devrev_works_create"
        assert caplog.records[1].duration_ms == 500

    def test_enriched_request_metadata_in_auth_success(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify user_agent, x_forwarded_for, and trace_id appear in auth success events."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_success(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                client_ip="10.0.0.1",
                user_agent="mcp-client/1.0 Python/3.11",
                x_forwarded_for="203.0.113.42, 10.0.0.1",
                trace_id="abc123def456789",
            )

        record = caplog.records[0]
        assert record.request["user_agent"] == "mcp-client/1.0 Python/3.11"
        assert record.request["x_forwarded_for"] == "203.0.113.42, 10.0.0.1"
        assert record.request["trace_id"] == "abc123def456789"

    def test_enriched_request_metadata_in_auth_failure(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify user_agent, x_forwarded_for, and trace_id appear in auth failure events."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_failure(
                reason="invalid_token",
                client_ip="10.0.0.1",
                user_agent="curl/7.88.1",
                x_forwarded_for="198.51.100.5",
                trace_id="trace-failure-test",
            )

        record = caplog.records[0]
        assert record.request["user_agent"] == "curl/7.88.1"
        assert record.request["x_forwarded_for"] == "198.51.100.5"
        assert record.request["trace_id"] == "trace-failure-test"

    def test_enriched_request_metadata_in_tool_invocation(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify user_agent, x_forwarded_for, and trace_id appear in tool invocation events."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_tool_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                tool_name="devrev_works_list",
                tool_category="read",
                client_ip="10.0.0.1",
                session_id="session-xyz",
                outcome="success",
                duration_ms=100,
                user_agent="curl/7.88.1",
                x_forwarded_for="198.51.100.5",
                trace_id="trace-id-987",
            )

        record = caplog.records[0]
        assert record.request["user_agent"] == "curl/7.88.1"
        assert record.request["x_forwarded_for"] == "198.51.100.5"
        assert record.request["trace_id"] == "trace-id-987"

    def test_enriched_fields_default_to_empty_string(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify enriched fields default to empty string when not provided."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_auth_success(
                user_id="don:identity:dvrv-us-1:devo/1:devu/123",
                email="user@example.com",
                pat_hash="sha256:abc123",
                client_ip="192.168.1.1",
            )

        record = caplog.records[0]
        assert record.request["user_agent"] == ""
        assert record.request["x_forwarded_for"] == ""
        assert record.request["trace_id"] == ""

    def test_log_resource_access_success(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify resource access events are logged with correct structure."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_resource_access(
                user_id="don:identity:dvrv-us-1:devo/1:devu/1",
                email="user@example.com",
                pat_hash="sha256:abc123",
                resource_uri="devrev://account/123",
                client_ip="10.0.0.1",
                outcome="success",
                duration_ms=5,
                user_agent="mcp-client/1.0",
                x_forwarded_for="203.0.113.42",
                trace_id="trace-res-test",
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.event_type == "audit"
        assert record.action == "resource_access"
        assert record.resource == {"uri": "devrev://account/123"}
        assert record.user["id"] == "don:identity:dvrv-us-1:devo/1:devu/1"
        assert record.outcome == "success"
        assert record.duration_ms == 5
        assert record.request["user_agent"] == "mcp-client/1.0"
        assert record.request["x_forwarded_for"] == "203.0.113.42"
        assert record.request["trace_id"] == "trace-res-test"

    def test_log_resource_access_failure(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify resource access failure events include error message."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_resource_access(
                user_id="don:identity:dvrv-us-1:devo/1:devu/1",
                email="user@example.com",
                pat_hash="sha256:abc123",
                resource_uri="devrev://ticket/999",
                client_ip="10.0.0.1",
                outcome="failure",
                duration_ms=2,
                error_message="Resource not found",
            )

        record = caplog.records[0]
        assert record.action == "resource_access"
        assert record.outcome == "failure"
        assert record.error_message == "Resource not found"

    def test_log_prompt_invocation_success(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify prompt invocation events are logged with correct structure."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_prompt_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/1",
                email="user@example.com",
                pat_hash="sha256:abc123",
                prompt_name="triage_ticket",
                client_ip="10.0.0.1",
                outcome="success",
                duration_ms=3,
                user_agent="mcp-client/1.0",
                x_forwarded_for="203.0.113.42",
                trace_id="trace-prompt-test",
            )

        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.event_type == "audit"
        assert record.action == "prompt_invocation"
        assert record.prompt == {"name": "triage_ticket"}
        assert record.user["id"] == "don:identity:dvrv-us-1:devo/1:devu/1"
        assert record.outcome == "success"
        assert record.duration_ms == 3
        assert record.request["user_agent"] == "mcp-client/1.0"
        assert record.request["x_forwarded_for"] == "203.0.113.42"
        assert record.request["trace_id"] == "trace-prompt-test"

    def test_log_prompt_invocation_failure(
        self, audit: AuditLogger, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Verify prompt invocation failure events include error message."""
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            audit.log_prompt_invocation(
                user_id="don:identity:dvrv-us-1:devo/1:devu/1",
                email="user@example.com",
                pat_hash="sha256:abc123",
                prompt_name="triage_ticket",
                client_ip="10.0.0.1",
                outcome="failure",
                duration_ms=1,
                error_message="Invalid argument",
            )

        record = caplog.records[0]
        assert record.action == "prompt_invocation"
        assert record.outcome == "failure"
        assert record.error_message == "Invalid argument"

    def test_log_resource_access_disabled(self, caplog: pytest.LogCaptureFixture) -> None:
        """Verify resource access events are not logged when disabled."""
        disabled_audit = AuditLogger(enabled=False)
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            disabled_audit.log_resource_access(
                user_id="u1",
                email="e@e.com",
                pat_hash="h",
                resource_uri="devrev://account/1",
                client_ip="1.2.3.4",
                outcome="success",
                duration_ms=1,
            )
        assert len(caplog.records) == 0

    def test_log_prompt_invocation_disabled(self, caplog: pytest.LogCaptureFixture) -> None:
        """Verify prompt invocation events are not logged when disabled."""
        disabled_audit = AuditLogger(enabled=False)
        with caplog.at_level(logging.INFO, logger="devrev_mcp.audit"):
            disabled_audit.log_prompt_invocation(
                user_id="u1",
                email="e@e.com",
                pat_hash="h",
                prompt_name="triage_ticket",
                client_ip="1.2.3.4",
                outcome="success",
                duration_ms=1,
            )
        assert len(caplog.records) == 0


class TestExtractRequestMetadata:
    """Tests for the _extract_request_metadata helper function."""

    def _make_request(self, headers: dict[str, str] | None = None) -> MagicMock:
        """Create a mock Starlette Request with given headers."""
        request = MagicMock()
        _headers = headers or {}
        request.headers.get = lambda key, default="": _headers.get(key, default)
        return request

    def test_all_headers_present(self) -> None:
        """Test extraction when all headers are present."""
        request = self._make_request(
            {
                "user-agent": "mcp-client/1.0",
                "x-forwarded-for": "203.0.113.42, 10.0.0.1",
                "x-cloud-trace-context": "abc123def456789012345678901234ff/12345;o=1",
            }
        )
        meta = _extract_request_metadata(request)
        assert meta["user_agent"] == "mcp-client/1.0"
        assert meta["x_forwarded_for"] == "203.0.113.42, 10.0.0.1"
        assert meta["trace_id"] == "abc123def456789012345678901234ff"

    def test_missing_all_headers(self) -> None:
        """Test extraction when no headers are present."""
        request = self._make_request({})
        meta = _extract_request_metadata(request)
        assert meta["user_agent"] == ""
        assert meta["x_forwarded_for"] == ""
        assert meta["trace_id"] == ""

    def test_trace_context_without_span_id(self) -> None:
        """Test trace ID extraction when header has no slash."""
        request = self._make_request(
            {
                "x-cloud-trace-context": "abc123def456",
            }
        )
        meta = _extract_request_metadata(request)
        assert meta["trace_id"] == "abc123def456"

    def test_trace_context_with_full_format(self) -> None:
        """Test: 'abc123/def456;o=1' extracts 'abc123'."""
        request = self._make_request(
            {
                "x-cloud-trace-context": "abc123/def456;o=1",
            }
        )
        meta = _extract_request_metadata(request)
        assert meta["trace_id"] == "abc123"

    def test_trace_context_empty_string(self) -> None:
        """Test empty string trace context returns empty trace_id."""
        request = self._make_request(
            {
                "x-cloud-trace-context": "",
            }
        )
        meta = _extract_request_metadata(request)
        assert meta["trace_id"] == ""
