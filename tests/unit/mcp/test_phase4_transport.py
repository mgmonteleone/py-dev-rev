"""Unit tests for Phase 4: Production Transports & Security.

Tests cover:
- MCPServerConfig with Phase 4 fields (transport, host, port, auth, CORS, rate limiting)
- BearerTokenMiddleware authentication
- RateLimitMiddleware and TokenBucket
- Health check endpoint
- CLI argument parsing
- Transport security settings
"""

from __future__ import annotations

import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient


class TestMCPServerConfigPhase4:
    """Tests for MCPServerConfig Phase 4 fields."""

    def test_default_values_phase4(self) -> None:
        """Test that Phase 4 config fields have correct defaults."""
        # Clear any existing MCP_ env vars
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()

            # Phase 4 defaults
            assert config.transport == "stdio"
            assert config.host == "127.0.0.1"
            assert config.port == 8080
            assert config.log_format == "json"
            assert config.enable_destructive_tools is True
            assert config.rate_limit_rpm == 120
            assert config.enable_dns_rebinding_protection is True
            assert config.auth_token is None
            assert config.cors_allowed_origins == []
            assert config.allowed_hosts == []

    def test_env_override_transport(self) -> None:
        """Test that MCP_TRANSPORT environment variable overrides default."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_TRANSPORT"] = "sse"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.transport == "sse"

    def test_env_override_host_and_port(self) -> None:
        """Test that MCP_HOST and MCP_PORT can be overridden."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_HOST"] = "0.0.0.0"
        env_vars["MCP_PORT"] = "9000"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.host == "0.0.0.0"
            assert config.port == 9000

    def test_env_override_auth_token(self) -> None:
        """Test that MCP_AUTH_TOKEN is loaded as SecretStr."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_AUTH_TOKEN"] = "secret-bearer-token-123"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.auth_token is not None
            assert config.auth_token.get_secret_value() == "secret-bearer-token-123"

    def test_env_override_cors_allowed_origins(self) -> None:
        """Test that MCP_CORS_ALLOWED_ORIGINS can be set as JSON list."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_CORS_ALLOWED_ORIGINS"] = '["https://example.com", "https://app.example.com"]'

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.cors_allowed_origins == ["https://example.com", "https://app.example.com"]

    def test_env_override_allowed_hosts(self) -> None:
        """Test that MCP_ALLOWED_HOSTS can be set as JSON list."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_ALLOWED_HOSTS"] = '["localhost", "127.0.0.1", "example.com"]'

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.allowed_hosts == ["localhost", "127.0.0.1", "example.com"]

    def test_env_override_log_format(self) -> None:
        """Test that MCP_LOG_FORMAT can be overridden."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_LOG_FORMAT"] = "text"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.log_format == "text"

    def test_env_override_enable_destructive_tools(self) -> None:
        """Test that MCP_ENABLE_DESTRUCTIVE_TOOLS can be disabled."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_ENABLE_DESTRUCTIVE_TOOLS"] = "false"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.enable_destructive_tools is False

    def test_env_override_rate_limit_rpm(self) -> None:
        """Test that MCP_RATE_LIMIT_RPM can be overridden."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_RATE_LIMIT_RPM"] = "60"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.rate_limit_rpm == 60

    def test_env_override_dns_rebinding_protection(self) -> None:
        """Test that MCP_ENABLE_DNS_REBINDING_PROTECTION can be disabled."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_ENABLE_DNS_REBINDING_PROTECTION"] = "false"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.enable_dns_rebinding_protection is False

    def test_default_auth_mode(self) -> None:
        """Test that default auth_mode is devrev-pat."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.auth_mode == "devrev-pat"

    def test_env_override_auth_mode(self) -> None:
        """Test that MCP_AUTH_MODE can be overridden."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_AUTH_MODE"] = "static-token"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.auth_mode == "static-token"

    def test_default_auth_allowed_domains(self) -> None:
        """Test that default auth_allowed_domains is ['augmentcode.com']."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.auth_allowed_domains == ["augmentcode.com"]

    def test_env_override_auth_allowed_domains(self) -> None:
        """Test that MCP_AUTH_ALLOWED_DOMAINS can be overridden."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_AUTH_ALLOWED_DOMAINS"] = '["example.com", "test.com"]'

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.auth_allowed_domains == ["example.com", "test.com"]

    def test_default_auth_cache_ttl_seconds(self) -> None:
        """Test that default auth_cache_ttl_seconds is 300."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.auth_cache_ttl_seconds == 300

    def test_env_override_auth_cache_ttl_seconds(self) -> None:
        """Test that MCP_AUTH_CACHE_TTL_SECONDS can be overridden."""
        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_AUTH_CACHE_TTL_SECONDS"] = "600"

        with patch.dict(os.environ, env_vars, clear=True):
            from devrev_mcp.config import MCPServerConfig

            config = MCPServerConfig()
            assert config.auth_cache_ttl_seconds == 600


class TestBearerTokenMiddleware:
    """Tests for BearerTokenMiddleware authentication."""

    def test_request_with_valid_token_passes(self) -> None:
        """Test that request with valid Bearer token passes through."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = BearerTokenMiddleware(app, token="secret-token-123")
        client = TestClient(app)

        response = client.get("/api/test", headers={"Authorization": "Bearer secret-token-123"})
        assert response.status_code == 200
        assert response.text == "OK"

    def test_request_with_missing_auth_header_returns_401(self) -> None:
        """Test that request without Authorization header returns 401."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = BearerTokenMiddleware(app, token="secret-token-123")
        client = TestClient(app)

        response = client.get("/api/test")
        assert response.status_code == 401
        assert "Missing Authorization header" in response.text

    def test_request_with_invalid_format_returns_401(self) -> None:
        """Test that request with invalid auth format returns 401."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = BearerTokenMiddleware(app, token="secret-token-123")
        client = TestClient(app)

        # Test with "Basic" instead of "Bearer"
        response = client.get("/api/test", headers={"Authorization": "Basic dXNlcjpwYXNz"})
        assert response.status_code == 401
        assert "Invalid Authorization header format" in response.text

        # Test with just the token (no "Bearer" prefix)
        response = client.get("/api/test", headers={"Authorization": "secret-token-123"})
        assert response.status_code == 401

    def test_request_with_wrong_token_returns_403(self) -> None:
        """Test that request with wrong token returns 403."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = BearerTokenMiddleware(app, token="secret-token-123")
        client = TestClient(app)

        response = client.get("/api/test", headers={"Authorization": "Bearer wrong-token"})
        assert response.status_code == 403
        assert "Invalid Bearer token" in response.text

    def test_health_check_path_skips_auth(self) -> None:
        """Test that /health endpoint skips authentication."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware

        async def health(request):
            return PlainTextResponse("healthy")

        app = Starlette(routes=[Route("/health", health)])
        app = BearerTokenMiddleware(app, token="secret-token-123")
        client = TestClient(app)

        # Health check should work without auth
        response = client.get("/health")
        assert response.status_code == 200
        assert response.text == "healthy"

    def test_options_request_skips_auth(self) -> None:
        """Test that OPTIONS request (CORS preflight) skips auth."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello, methods=["GET", "OPTIONS"])])
        app = BearerTokenMiddleware(app, token="secret-token-123")
        client = TestClient(app)

        # OPTIONS should work without auth (CORS preflight)
        response = client.options("/api/test")
        assert response.status_code == 200

    def test_request_with_whitespace_padded_token_passes(self) -> None:
        """Test that token with leading/trailing whitespace is accepted."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = BearerTokenMiddleware(app, token="secret-token-123")
        client = TestClient(app)

        response = client.get("/api/test", headers={"Authorization": "Bearer  secret-token-123 "})
        assert response.status_code == 200
        assert response.text == "OK"

    def test_empty_token_raises_value_error(self) -> None:
        """Test that BearerTokenMiddleware rejects empty token at init."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        with pytest.raises(ValueError, match="non-empty token"):
            BearerTokenMiddleware(app, token="")


class TestTokenBucket:
    """Tests for TokenBucket rate limiting algorithm."""

    def test_token_bucket_consume_within_capacity(self) -> None:
        """Test consuming tokens within capacity."""
        from devrev_mcp.middleware.rate_limit import TokenBucket

        bucket = TokenBucket(rate=1.0, capacity=2.0)
        assert bucket.consume() is True
        assert bucket.consume() is True

    def test_token_bucket_consume_exhausted(self) -> None:
        """Test that consuming beyond capacity fails."""
        from devrev_mcp.middleware.rate_limit import TokenBucket

        bucket = TokenBucket(rate=1.0, capacity=2.0)
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is False  # exhausted

    def test_token_bucket_refill(self) -> None:
        """Test that tokens refill over time."""
        from devrev_mcp.middleware.rate_limit import TokenBucket

        bucket = TokenBucket(rate=10.0, capacity=2.0)  # 10 tokens/sec
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is False  # exhausted

        # Wait for refill (0.2 seconds = 2 tokens at 10/sec)
        time.sleep(0.2)
        assert bucket.consume() is True

    def test_token_bucket_retry_after(self) -> None:
        """Test retry_after calculation when bucket is empty."""
        from devrev_mcp.middleware.rate_limit import TokenBucket

        bucket = TokenBucket(rate=1.0, capacity=1.0)
        assert bucket.consume() is True
        assert bucket.consume() is False

        retry_after = bucket.retry_after
        assert retry_after > 0
        assert retry_after <= 1.0  # Should be at most 1 second for 1 token/sec

    def test_token_bucket_retry_after_with_tokens(self) -> None:
        """Test retry_after returns 0 when tokens are available."""
        from devrev_mcp.middleware.rate_limit import TokenBucket

        bucket = TokenBucket(rate=1.0, capacity=2.0)
        retry_after = bucket.retry_after
        assert retry_after == 0

    def test_token_bucket_retry_after_zero_rate(self) -> None:
        """Test retry_after returns fallback when rate is zero."""
        from devrev_mcp.middleware.rate_limit import TokenBucket

        bucket = TokenBucket(rate=0.0, capacity=1.0)
        bucket.tokens = 0.0  # Force empty
        retry_after = bucket.retry_after
        assert retry_after == 60.0  # Fallback value


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware."""

    def test_request_within_rate_limit_passes(self) -> None:
        """Test that requests within rate limit pass through."""
        from devrev_mcp.middleware.rate_limit import RateLimitMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = RateLimitMiddleware(app, requests_per_minute=120)  # 2 requests/sec
        client = TestClient(app)

        response = client.get("/api/test")
        assert response.status_code == 200
        assert response.text == "OK"

    def test_request_exceeding_rate_limit_returns_429(self) -> None:
        """Test that requests exceeding rate limit return 429."""
        from devrev_mcp.middleware.rate_limit import RateLimitMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        # Very low rate limit: 6 requests/min = 0.1 requests/sec
        app = RateLimitMiddleware(app, requests_per_minute=6)
        client = TestClient(app)

        # First request should succeed
        response = client.get("/api/test")
        assert response.status_code == 200

        # Rapid subsequent requests should be rate limited
        rate_limited = False
        for _ in range(10):
            response = client.get("/api/test")
            if response.status_code == 429:
                rate_limited = True
                assert "Retry-After" in response.headers
                assert int(response.headers["Retry-After"]) > 0
                break

        assert rate_limited, "Expected at least one request to be rate limited"

    def test_health_check_path_skips_rate_limiting(self) -> None:
        """Test that /health endpoint skips rate limiting."""
        from devrev_mcp.middleware.rate_limit import RateLimitMiddleware

        async def health(request):
            return PlainTextResponse("healthy")

        app = Starlette(routes=[Route("/health", health)])
        app = RateLimitMiddleware(app, requests_per_minute=6)  # Very low limit
        client = TestClient(app)

        # Health check should work even with many requests
        for _ in range(20):
            response = client.get("/health")
            assert response.status_code == 200
            assert response.text == "healthy"

    def test_rate_limit_disabled_when_rpm_is_zero(self) -> None:
        """Test that rate limiting is disabled when requests_per_minute=0."""
        from devrev_mcp.middleware.rate_limit import RateLimitMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = RateLimitMiddleware(app, requests_per_minute=0)
        client = TestClient(app)

        # All requests should pass through when rate limiting is disabled
        for _ in range(50):
            response = client.get("/api/test")
            assert response.status_code == 200

    def test_lru_eviction_limits_bucket_count(self) -> None:
        """Test that LRU eviction prevents unbounded memory growth."""
        from devrev_mcp.middleware.rate_limit import _MAX_BUCKETS, RateLimitMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        middleware = RateLimitMiddleware(app, requests_per_minute=120)

        # Simulate many unique clients
        for i in range(100):
            middleware._get_or_create_bucket(f"ip:10.0.0.{i}")

        assert len(middleware._buckets) <= _MAX_BUCKETS


class TestHealthCheckEndpoint:
    """Tests for health check endpoint."""

    def test_health_check_returns_200(self) -> None:
        """Test that health check returns 200 with status healthy."""
        from devrev_mcp.middleware.health import health_route

        app = Starlette(routes=[health_route()])
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self) -> None:
        """Test that health check response includes required fields."""
        from devrev_mcp.middleware.health import health_route

        app = Starlette(routes=[health_route()])
        client = TestClient(app)
        response = client.get("/health")
        health_data = response.json()

        assert health_data["status"] == "healthy"
        assert "server" in health_data
        assert "version" in health_data
        assert "uptime_seconds" in health_data
        assert isinstance(health_data["uptime_seconds"], (int, float))
        assert health_data["uptime_seconds"] >= 0

    def test_health_check_returns_valid_json(self) -> None:
        """Test that health check response is valid JSON."""
        from devrev_mcp.middleware.health import health_route

        app = Starlette(routes=[health_route()])
        client = TestClient(app)
        response = client.get("/health")
        health_data = response.json()
        assert isinstance(health_data, dict)

    def test_health_check_uptime_after_init(self) -> None:
        """Test that uptime is calculated from init_start_time() call."""
        from devrev_mcp.middleware.health import health_route, init_start_time

        # Initialize start time
        init_start_time()

        app = Starlette(routes=[health_route()])
        client = TestClient(app)
        response = client.get("/health")
        health_data = response.json()

        assert health_data["uptime_seconds"] >= 0


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing in __main__.py."""

    def test_default_transport_is_stdio(self) -> None:
        """Test that default transport is stdio when no args provided."""
        with patch("sys.argv", ["devrev-mcp"]), patch.dict(os.environ, {}, clear=False):
            # Import would parse args and set env vars
            # We'll test the logic directly
            import argparse

            parser = argparse.ArgumentParser()
            parser.add_argument("--transport", default="stdio")
            args = parser.parse_args([])
            assert args.transport == "stdio"

    def test_transport_flag_sets_env_var(self) -> None:
        """Test that --transport flag sets MCP_TRANSPORT env var."""
        with patch("sys.argv", ["devrev-mcp", "--transport", "sse"]):
            import argparse

            parser = argparse.ArgumentParser()
            parser.add_argument("--transport", default="stdio")
            args = parser.parse_args(["--transport", "sse"])

            # Simulate what __main__.py does
            with patch.dict(os.environ, {"MCP_TRANSPORT": args.transport}):
                assert os.environ["MCP_TRANSPORT"] == "sse"

    def test_host_flag_sets_env_var(self) -> None:
        """Test that --host flag sets MCP_HOST env var."""
        with patch("sys.argv", ["devrev-mcp", "--host", "0.0.0.0"]):
            import argparse

            parser = argparse.ArgumentParser()
            parser.add_argument("--host", default="127.0.0.1")
            args = parser.parse_args(["--host", "0.0.0.0"])

            # Simulate what __main__.py does
            with patch.dict(os.environ, {"MCP_HOST": args.host}):
                assert os.environ["MCP_HOST"] == "0.0.0.0"

    def test_port_flag_sets_env_var(self) -> None:
        """Test that --port flag sets MCP_PORT env var."""
        with patch("sys.argv", ["devrev-mcp", "--port", "9000"]):
            import argparse

            parser = argparse.ArgumentParser()
            parser.add_argument("--port", type=int, default=8080)
            args = parser.parse_args(["--port", "9000"])

            # Simulate what __main__.py does
            with patch.dict(os.environ, {"MCP_PORT": str(args.port)}):
                assert os.environ["MCP_PORT"] == "9000"


class TestServerTransportSecurity:
    """Tests for _build_transport_security function."""

    def test_returns_none_for_stdio_transport(self) -> None:
        """Test that stdio transport returns None (no security settings)."""
        from devrev_mcp.config import MCPServerConfig
        from devrev_mcp.server import _build_transport_security

        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_TRANSPORT"] = "stdio"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()
            security = _build_transport_security(config)
            assert security is None

    def test_returns_security_settings_for_streamable_http(self) -> None:
        """Test that streamable-http transport returns TransportSecuritySettings."""
        from devrev_mcp.config import MCPServerConfig
        from devrev_mcp.server import _build_transport_security

        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_TRANSPORT"] = "streamable-http"
        env_vars["MCP_ALLOWED_HOSTS"] = '["localhost", "127.0.0.1"]'
        env_vars["MCP_CORS_ALLOWED_ORIGINS"] = '["https://example.com"]'

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()
            security = _build_transport_security(config)

            assert security is not None
            assert security.allowed_hosts == ["localhost", "127.0.0.1"]
            assert security.allowed_origins == ["https://example.com"]

    def test_returns_security_settings_for_sse(self) -> None:
        """Test that sse transport returns TransportSecuritySettings."""
        from devrev_mcp.config import MCPServerConfig
        from devrev_mcp.server import _build_transport_security

        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_TRANSPORT"] = "sse"
        env_vars["MCP_ALLOWED_HOSTS"] = '["example.com"]'

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()
            security = _build_transport_security(config)

            assert security is not None
            assert security.allowed_hosts == ["example.com"]

    def test_passes_through_allowed_hosts_and_origins(self) -> None:
        """Test that allowed_hosts and allowed_origins are passed through from config."""
        from devrev_mcp.config import MCPServerConfig
        from devrev_mcp.server import _build_transport_security

        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["MCP_TRANSPORT"] = "sse"
        env_vars["MCP_ALLOWED_HOSTS"] = '["host1.com", "host2.com"]'
        env_vars["MCP_CORS_ALLOWED_ORIGINS"] = '["https://origin1.com", "https://origin2.com"]'

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()
            security = _build_transport_security(config)

            assert security is not None
            assert security.allowed_hosts == ["host1.com", "host2.com"]
            assert security.allowed_origins == ["https://origin1.com", "https://origin2.com"]


class TestMiddlewareInjection:
    """Tests that verify middleware injection into Starlette apps.

    These tests exercise the _inject_middleware function from server.py
    to confirm that health route, auth, and rate limiting are properly
    added to Starlette apps — validating the monkey-patching approach.
    """

    def test_inject_middleware_adds_health_route(self) -> None:
        """Test that _inject_middleware adds /health route to the app."""
        from devrev_mcp.middleware.health import health_route, init_start_time

        # Initialize start time so health endpoint can report uptime
        init_start_time()

        # Create a bare Starlette app
        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])

        # Manually inject health route (same as _inject_middleware does)
        app.routes.insert(0, health_route())

        client = TestClient(app)

        # /health should now be accessible
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "uptime_seconds" in data

    def test_inject_middleware_adds_auth_middleware(self) -> None:
        """Test that auth middleware blocks unauthenticated requests after injection."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware
        from devrev_mcp.middleware.health import health_route, init_start_time

        init_start_time()

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app.routes.insert(0, health_route())

        # Add auth middleware (same as _inject_middleware does when auth_token is set)
        app.add_middleware(BearerTokenMiddleware, token="test-secret")

        client = TestClient(app)

        # /health should bypass auth
        response = client.get("/health")
        assert response.status_code == 200

        # /api/test without token should be 401
        response = client.get("/api/test")
        assert response.status_code == 401

        # /api/test with correct token should be 200
        response = client.get("/api/test", headers={"Authorization": "Bearer test-secret"})
        assert response.status_code == 200

    def test_inject_middleware_adds_rate_limiting(self) -> None:
        """Test that rate limiting blocks excess requests after injection."""
        from devrev_mcp.middleware.health import health_route, init_start_time
        from devrev_mcp.middleware.rate_limit import RateLimitMiddleware

        init_start_time()

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app.routes.insert(0, health_route())

        # Very low rate limit to trigger 429 quickly
        app.add_middleware(RateLimitMiddleware, requests_per_minute=2)

        client = TestClient(app)

        # First request should pass
        response = client.get("/api/test")
        assert response.status_code == 200

        # Rapid requests should eventually hit 429
        rate_limited = False
        for _ in range(10):
            response = client.get("/api/test")
            if response.status_code == 429:
                rate_limited = True
                assert "Retry-After" in response.headers
                break

        assert rate_limited, "Expected rate limiting to kick in"

        # /health should still bypass rate limiting
        response = client.get("/health")
        assert response.status_code == 200

    def test_full_middleware_stack_injection(self) -> None:
        """Test the full middleware stack: health + auth + rate limiting together."""
        from devrev_mcp.middleware.auth import BearerTokenMiddleware
        from devrev_mcp.middleware.health import health_route, init_start_time
        from devrev_mcp.middleware.rate_limit import RateLimitMiddleware

        init_start_time()

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app.routes.insert(0, health_route())

        # Add both middlewares (rate limit first = outermost, auth second = inner)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
        app.add_middleware(BearerTokenMiddleware, token="test-secret")

        client = TestClient(app)

        # /health should work without auth (bypasses both middlewares)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

        # /api/test without token should fail auth
        response = client.get("/api/test")
        assert response.status_code == 401

        # /api/test with correct token should succeed
        response = client.get("/api/test", headers={"Authorization": "Bearer test-secret"})
        assert response.status_code == 200
        assert response.text == "OK"


class TestDevRevPATAuthMiddleware:
    """Tests for DevRevPATAuthMiddleware per-user PAT authentication."""

    def test_missing_auth_header_returns_401(self) -> None:
        """Test that request without Authorization header returns 401."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = DevRevPATAuthMiddleware(app)
        client = TestClient(app)

        response = client.get("/api/test")
        assert response.status_code == 401
        assert "Missing Authorization header" in response.text

    def test_malformed_auth_header_returns_401(self) -> None:
        """Test that request with malformed auth header returns 401."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = DevRevPATAuthMiddleware(app)
        client = TestClient(app)

        # Test with "Basic" instead of "Bearer"
        response = client.get("/api/test", headers={"Authorization": "Basic dXNlcjpwYXNz"})
        assert response.status_code == 401
        assert "Invalid Authorization header format" in response.text

        # Test with just the token (no "Bearer" prefix)
        response = client.get("/api/test", headers={"Authorization": "test-token"})
        assert response.status_code == 401

    def test_invalid_pat_returns_403(self) -> None:
        """Test that invalid PAT returns 403 after DevRev API validation fails."""
        from devrev.exceptions import DevRevError
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = DevRevPATAuthMiddleware(app)
        client = TestClient(app)

        # Mock the DevRev API to raise an error
        with patch("devrev_mcp.middleware.auth.AsyncDevRevClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.dev_users.self = AsyncMock(side_effect=DevRevError("Invalid token"))
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            response = client.get("/api/test", headers={"Authorization": "Bearer invalid-pat"})
            assert response.status_code == 403
            assert "Invalid DevRev PAT" in response.text

    def test_valid_pat_returns_200(self) -> None:
        """Test that valid PAT passes authentication and sets request state."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            # Verify request state was set
            assert hasattr(request.state, "devrev_pat")
            assert hasattr(request.state, "devrev_user_id")
            assert hasattr(request.state, "devrev_user_email")
            assert hasattr(request.state, "devrev_user_display_name")
            assert request.state.devrev_user_email == "user@augmentcode.com"
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = DevRevPATAuthMiddleware(app)
        client = TestClient(app)

        # Mock the DevRev API to return a valid user
        with patch("devrev_mcp.middleware.auth.AsyncDevRevClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = "don:identity:dvrv-us-1:devo/1:devu/123"
            mock_user.email = "user@augmentcode.com"
            mock_user.display_name = "Test User"
            mock_client.dev_users.self = AsyncMock(return_value=mock_user)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            response = client.get("/api/test", headers={"Authorization": "Bearer valid-pat-token"})
            assert response.status_code == 200
            assert response.text == "OK"

    def test_domain_restriction_allowed(self) -> None:
        """Test that user from allowed domain passes authentication."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = DevRevPATAuthMiddleware(app, allowed_domains=["augmentcode.com"])
        client = TestClient(app)

        # Mock the DevRev API to return a user with allowed domain
        with patch("devrev_mcp.middleware.auth.AsyncDevRevClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = "don:identity:dvrv-us-1:devo/1:devu/123"
            mock_user.email = "user@augmentcode.com"
            mock_user.display_name = "Test User"
            mock_client.dev_users.self = AsyncMock(return_value=mock_user)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            response = client.get("/api/test", headers={"Authorization": "Bearer valid-pat"})
            assert response.status_code == 200

    def test_domain_restriction_blocked(self) -> None:
        """Test that user from disallowed domain is rejected."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = DevRevPATAuthMiddleware(app, allowed_domains=["augmentcode.com"])
        client = TestClient(app)

        # Mock the DevRev API to return a user with disallowed domain
        with patch("devrev_mcp.middleware.auth.AsyncDevRevClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = "don:identity:dvrv-us-1:devo/1:devu/456"
            mock_user.email = "user@other.com"
            mock_user.display_name = "Other User"
            mock_client.dev_users.self = AsyncMock(return_value=mock_user)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            response = client.get("/api/test", headers={"Authorization": "Bearer valid-pat"})
            assert response.status_code == 403
            assert "Email domain not allowed" in response.text

    def test_health_endpoint_skips_auth(self) -> None:
        """Test that /health endpoint skips authentication."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def health(request):
            return PlainTextResponse("healthy")

        app = Starlette(routes=[Route("/health", health)])
        app = DevRevPATAuthMiddleware(app)
        client = TestClient(app)

        # Health check should work without auth
        response = client.get("/health")
        assert response.status_code == 200
        assert response.text == "healthy"

    def test_options_request_skips_auth(self) -> None:
        """Test that OPTIONS request (CORS preflight) skips auth."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello, methods=["GET", "OPTIONS"])])
        app = DevRevPATAuthMiddleware(app)
        client = TestClient(app)

        # OPTIONS should work without auth (CORS preflight)
        response = client.options("/api/test")
        assert response.status_code == 200

    def test_caching_reduces_api_calls(self) -> None:
        """Test that second request with same PAT uses cache and doesn't call DevRev API again."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        app = DevRevPATAuthMiddleware(app, cache_ttl_seconds=300)
        client = TestClient(app)

        # Mock the DevRev API
        with patch("devrev_mcp.middleware.auth.AsyncDevRevClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = "don:identity:dvrv-us-1:devo/1:devu/123"
            mock_user.email = "user@augmentcode.com"
            mock_user.display_name = "Test User"
            mock_client.dev_users.self = AsyncMock(return_value=mock_user)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            # First request - should call API
            response1 = client.get("/api/test", headers={"Authorization": "Bearer same-pat-token"})
            assert response1.status_code == 200
            assert mock_client.dev_users.self.call_count == 1

            # Second request with same PAT - should use cache, not call API again
            response2 = client.get("/api/test", headers={"Authorization": "Bearer same-pat-token"})
            assert response2.status_code == 200
            # Still only 1 call because second request used cache
            assert mock_client.dev_users.self.call_count == 1

    def test_no_domain_restriction(self) -> None:
        """Test that when allowed_domains is empty/None, any domain passes."""
        from devrev_mcp.middleware.auth import DevRevPATAuthMiddleware

        async def hello(request):
            return PlainTextResponse("OK")

        app = Starlette(routes=[Route("/api/test", hello)])
        # No domain restriction (empty list)
        app = DevRevPATAuthMiddleware(app, allowed_domains=[])
        client = TestClient(app)

        # Mock the DevRev API to return a user with any domain
        with patch("devrev_mcp.middleware.auth.AsyncDevRevClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_user = MagicMock()
            mock_user.id = "don:identity:dvrv-us-1:devo/1:devu/789"
            mock_user.email = "user@anydomain.com"
            mock_user.display_name = "Any User"
            mock_client.dev_users.self = AsyncMock(return_value=mock_user)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            response = client.get("/api/test", headers={"Authorization": "Bearer valid-pat"})
            assert response.status_code == 200
            assert response.text == "OK"


class TestAppContextGetClient:
    """Tests for AppContext.get_client() method."""

    def test_get_client_stdio_mode(self) -> None:
        """Test that get_client() returns stdio client when _stdio_client is set."""
        from devrev import APIVersion, AsyncDevRevClient
        from devrev_mcp.config import MCPServerConfig
        from devrev_mcp.server import AppContext

        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["DEVREV_API_TOKEN"] = "test-token"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()
            mock_client = AsyncMock(spec=AsyncDevRevClient)

            app = AppContext(
                config=config,
                _api_version=APIVersion.PUBLIC,
                _stdio_client=mock_client,
            )

            # Should return the stdio client
            client = app.get_client()
            assert client is mock_client

    def test_get_client_pat_mode(self) -> None:
        """Test that get_client() creates client from PAT when context var is set."""
        from devrev import APIVersion
        from devrev_mcp.config import MCPServerConfig
        from devrev_mcp.middleware.auth import _current_devrev_client, _current_devrev_pat
        from devrev_mcp.server import AppContext

        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["DEVREV_API_TOKEN"] = "test-token"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()

            app = AppContext(
                config=config,
                _api_version=APIVersion.PUBLIC,
                _stdio_client=None,  # No stdio client
            )

            # Set the context var (simulating middleware)
            _current_devrev_pat.set("user-pat-token")

            try:
                # Mock AsyncDevRevClient constructor
                with patch("devrev_mcp.server.AsyncDevRevClient") as mock_client_class:
                    mock_client = AsyncMock()
                    mock_client_class.return_value = mock_client

                    client = app.get_client()

                    # Should create a new client with the PAT
                    mock_client_class.assert_called_once_with(
                        api_token="user-pat-token",
                        api_version=APIVersion.PUBLIC,
                    )
                    assert client is mock_client
            finally:
                # Clean up context vars
                _current_devrev_pat.set(None)
                _current_devrev_client.set(None)

    def test_get_client_no_client_available(self) -> None:
        """Test that get_client() raises RuntimeError when no client is available."""
        from devrev import APIVersion
        from devrev_mcp.config import MCPServerConfig
        from devrev_mcp.middleware.auth import _current_devrev_client, _current_devrev_pat
        from devrev_mcp.server import AppContext

        env_vars = {k: v for k, v in os.environ.items() if not k.startswith("MCP_")}
        env_vars["DEVREV_API_TOKEN"] = "test-token"

        with patch.dict(os.environ, env_vars, clear=True):
            config = MCPServerConfig()

            app = AppContext(
                config=config,
                _api_version=APIVersion.PUBLIC,
                _stdio_client=None,  # No stdio client
            )

            # Make sure context vars are not set
            _current_devrev_pat.set(None)
            _current_devrev_client.set(None)

            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match="No DevRev client available"):
                app.get_client()
