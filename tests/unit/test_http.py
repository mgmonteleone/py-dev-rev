"""Unit tests for HTTP client utilities."""

import httpx
import pytest
import respx
from pydantic import SecretStr

from devrev.exceptions import (
    AuthenticationError,
    CircuitBreakerError,
    DevRevError,
    NotFoundError,
    RateLimitError,
)
from devrev.utils.http import (
    DEFAULT_RETRY_STATUS_CODES,
    AsyncHTTPClient,
    CircuitBreakerConfig,
    CircuitState,
    ConnectionPoolConfig,
    HTTPClient,
    TimeoutConfig,
    _calculate_backoff,
    _extract_error_message,
    _raise_for_status,
)


class TestCalculateBackoff:
    """Tests for _calculate_backoff function."""

    def test_first_attempt(self) -> None:
        # Default backoff_factor is 0.5, so 0.5 * 2^0 = 0.5
        backoff = _calculate_backoff(0)
        assert backoff == 0.5

    def test_second_attempt(self) -> None:
        # 0.5 * 2^1 = 1.0
        backoff = _calculate_backoff(1)
        assert backoff == 1.0

    def test_third_attempt(self) -> None:
        # 0.5 * 2^2 = 2.0
        backoff = _calculate_backoff(2)
        assert backoff == 2.0

    def test_custom_backoff_factor(self) -> None:
        # 2.0 * 2^0 = 2.0
        backoff = _calculate_backoff(0, backoff_factor=2.0)
        assert backoff == 2.0


class TestExtractErrorMessage:
    """Tests for _extract_error_message function."""

    def test_json_error_with_message(self) -> None:
        response = httpx.Response(400, json={"message": "Bad request"})
        message, body = _extract_error_message(response)
        assert message == "Bad request"
        assert body == {"message": "Bad request"}

    def test_json_error_with_error_field(self) -> None:
        response = httpx.Response(400, json={"error": "Something went wrong"})
        message, body = _extract_error_message(response)
        assert message == "Something went wrong"
        assert body == {"error": "Something went wrong"}

    def test_non_json_response(self) -> None:
        response = httpx.Response(500, text="Internal Server Error")
        message, body = _extract_error_message(response)
        assert "HTTP 500" in message
        assert body is None


class TestRaiseForStatus:
    """Tests for _raise_for_status function."""

    def test_success_response(self) -> None:
        response = httpx.Response(200, json={"data": "ok"})
        _raise_for_status(response)

    def test_not_found_error(self) -> None:
        response = httpx.Response(404, json={"message": "Not found"})
        with pytest.raises(NotFoundError):
            _raise_for_status(response)

    def test_auth_error(self) -> None:
        response = httpx.Response(401, json={"message": "Unauthorized"})
        with pytest.raises(AuthenticationError):
            _raise_for_status(response)

    def test_rate_limit_error_with_retry_after(self) -> None:
        response = httpx.Response(
            429, json={"message": "Rate limited"}, headers={"Retry-After": "60"}
        )
        with pytest.raises(RateLimitError) as exc_info:
            _raise_for_status(response)
        assert exc_info.value.retry_after == 60

    def test_generic_error(self) -> None:
        response = httpx.Response(500, json={"message": "Server error"})
        with pytest.raises(DevRevError):
            _raise_for_status(response)


class TestHTTPClient:
    """Tests for HTTPClient class."""

    @pytest.fixture
    def api_token(self) -> SecretStr:
        return SecretStr("test-token")

    @pytest.fixture
    def client(self, api_token: SecretStr) -> HTTPClient:
        return HTTPClient(api_token=api_token, base_url="https://api.devrev.ai")

    def test_client_initialization(self, client: HTTPClient) -> None:
        assert client._base_url == "https://api.devrev.ai"

    def test_build_headers(self, client: HTTPClient) -> None:
        headers = client._build_headers()
        assert "Authorization" in headers
        assert headers["Content-Type"] == "application/json"

    def test_context_manager(self, api_token: SecretStr) -> None:
        with HTTPClient(api_token=api_token, base_url="https://api.devrev.ai") as client:
            assert client is not None

    def test_should_retry_for_retryable_codes(self, client: HTTPClient) -> None:
        for code in DEFAULT_RETRY_STATUS_CODES:
            response = httpx.Response(code)
            assert client._should_retry(response) is True

    def test_should_not_retry_for_success(self, client: HTTPClient) -> None:
        response = httpx.Response(200)
        assert client._should_retry(response) is False

    @respx.mock
    def test_successful_get_request(self, client: HTTPClient) -> None:
        respx.get("https://api.devrev.ai/test").mock(
            return_value=httpx.Response(200, json={"id": "123"})
        )
        response = client.get("/test")
        assert response.status_code == 200

    @respx.mock
    def test_successful_post_request(self, client: HTTPClient) -> None:
        respx.post("https://api.devrev.ai/test").mock(
            return_value=httpx.Response(200, json={"id": "123"})
        )
        response = client.post("/test", data={"name": "test"})
        assert response.status_code == 200

    @respx.mock
    def test_request_raises_on_error(self, client: HTTPClient) -> None:
        respx.get("https://api.devrev.ai/error").mock(
            return_value=httpx.Response(404, json={"message": "Not found"})
        )
        with pytest.raises(NotFoundError):
            client.get("/error")


class TestAsyncHTTPClient:
    """Tests for AsyncHTTPClient class."""

    @pytest.fixture
    def api_token(self) -> SecretStr:
        return SecretStr("test-token")

    @pytest.fixture
    def client(self, api_token: SecretStr) -> AsyncHTTPClient:
        return AsyncHTTPClient(api_token=api_token, base_url="https://api.devrev.ai")

    def test_async_client_initialization(self, client: AsyncHTTPClient) -> None:
        assert client._base_url == "https://api.devrev.ai"

    def test_async_build_headers(self, client: AsyncHTTPClient) -> None:
        headers = client._build_headers()
        assert "Authorization" in headers
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.asyncio
    async def test_async_context_manager(self, api_token: SecretStr) -> None:
        async with AsyncHTTPClient(api_token=api_token, base_url="https://api.devrev.ai") as client:
            assert client is not None

    def test_async_should_retry(self, client: AsyncHTTPClient) -> None:
        for code in DEFAULT_RETRY_STATUS_CODES:
            response = httpx.Response(code)
            assert client._should_retry(response) is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_successful_get(self, client: AsyncHTTPClient) -> None:
        respx.get("https://api.devrev.ai/test").mock(
            return_value=httpx.Response(200, json={"id": "123"})
        )
        response = await client.get("/test")
        assert response.status_code == 200

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_successful_post(self, client: AsyncHTTPClient) -> None:
        respx.post("https://api.devrev.ai/test").mock(
            return_value=httpx.Response(200, json={"id": "123"})
        )
        response = await client.post("/test", data={"name": "test"})
        assert response.status_code == 200

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_request_raises_on_error(self, client: AsyncHTTPClient) -> None:
        respx.get("https://api.devrev.ai/error").mock(
            return_value=httpx.Response(404, json={"message": "Not found"})
        )
        with pytest.raises(NotFoundError):
            await client.get("/error")


class TestTimeoutConfig:
    """Tests for TimeoutConfig dataclass."""

    def test_default_values(self) -> None:
        config = TimeoutConfig()
        assert config.connect == 5.0
        assert config.read == 30.0
        assert config.write == 30.0
        assert config.pool == 10.0

    def test_custom_values(self) -> None:
        config = TimeoutConfig(connect=10.0, read=60.0, write=60.0, pool=20.0)
        assert config.connect == 10.0
        assert config.read == 60.0

    def test_from_total(self) -> None:
        config = TimeoutConfig.from_total(60.0)
        # from_total distributes timeouts appropriately
        assert config.read == 60.0
        assert config.write == 60.0
        # connect is min(5.0, total/6)
        assert config.connect == 5.0  # min(5.0, 10.0)
        # pool is min(10.0, total/3)
        assert config.pool == 10.0  # min(10.0, 20.0)

    def test_to_httpx_timeout(self) -> None:
        config = TimeoutConfig(connect=5.0, read=30.0, write=30.0, pool=10.0)
        timeout = config.to_httpx_timeout()
        assert isinstance(timeout, httpx.Timeout)
        assert timeout.connect == 5.0
        assert timeout.read == 30.0
        assert timeout.write == 30.0
        assert timeout.pool == 10.0


class TestConnectionPoolConfig:
    """Tests for ConnectionPoolConfig dataclass."""

    def test_default_values(self) -> None:
        config = ConnectionPoolConfig()
        assert config.max_connections == 100
        assert config.max_keepalive_connections == 20
        assert config.keepalive_expiry == 30.0
        assert config.http2 is False

    def test_custom_values(self) -> None:
        config = ConnectionPoolConfig(
            max_connections=50,
            max_keepalive_connections=10,
            keepalive_expiry=60.0,
            http2=True,
        )
        assert config.max_connections == 50
        assert config.http2 is True


class TestCircuitBreakerConfig:
    """Tests for CircuitBreakerConfig dataclass."""

    def test_default_values(self) -> None:
        config = CircuitBreakerConfig()
        assert config.enabled is True
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 30.0
        assert config.half_open_max_calls == 3

    def test_disabled(self) -> None:
        config = CircuitBreakerConfig(enabled=False)
        assert config.enabled is False

    def test_custom_thresholds(self) -> None:
        config = CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=60.0,
            half_open_max_calls=5,
        )
        assert config.failure_threshold == 10
        assert config.recovery_timeout == 60.0


class TestHTTPClientWithConfiguration:
    """Tests for HTTPClient with advanced configuration."""

    @pytest.fixture
    def api_token(self) -> SecretStr:
        return SecretStr("test-token")

    def test_client_with_timeout_config(self, api_token: SecretStr) -> None:
        timeout_config = TimeoutConfig(connect=10.0, read=60.0)
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
            timeout=timeout_config,
        )
        assert client._timeout_config.connect == 10.0
        assert client._timeout_config.read == 60.0
        client.close()

    def test_client_with_pool_config(self, api_token: SecretStr) -> None:
        # Test with http2=False (default) to avoid h2 package requirement
        pool_config = ConnectionPoolConfig(max_connections=50, http2=False)
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
            pool_config=pool_config,
        )
        assert client._pool_config.max_connections == 50
        assert client._pool_config.http2 is False
        client.close()

    def test_client_with_circuit_breaker_config(self, api_token: SecretStr) -> None:
        cb_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=10.0)
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
            circuit_breaker_config=cb_config,
        )
        assert client._circuit_breaker_config.failure_threshold == 3
        assert client.circuit_state == CircuitState.CLOSED
        client.close()

    def test_circuit_breaker_disabled(self, api_token: SecretStr) -> None:
        cb_config = CircuitBreakerConfig(enabled=False)
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
            circuit_breaker_config=cb_config,
        )
        # Should not raise even if we try to check circuit breaker
        client._check_circuit_breaker()  # No exception
        client.close()

    @respx.mock
    def test_etag_caching(self, api_token: SecretStr) -> None:
        """Test ETag caching functionality."""
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
        )
        # First request returns ETag
        respx.get("https://api.devrev.ai/resource").mock(
            return_value=httpx.Response(
                200, json={"data": "initial"}, headers={"ETag": '"abc123"'}
            )
        )
        response = client.get("/resource")
        assert response.status_code == 200
        assert "GET:/resource" in client._etag_cache
        assert client._etag_cache["GET:/resource"] == '"abc123"'
        client.close()

    def test_clear_etag_cache(self, api_token: SecretStr) -> None:
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
        )
        client._etag_cache["test"] = "value"
        client.clear_etag_cache()
        assert len(client._etag_cache) == 0
        client.close()

    def test_reset_circuit_breaker(self, api_token: SecretStr) -> None:
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
        )
        # Manually set circuit to open state
        client._circuit_breaker_state.state = CircuitState.OPEN
        client._circuit_breaker_state.failure_count = 10

        # Reset it
        client.reset_circuit_breaker()
        assert client.circuit_state == CircuitState.CLOSED
        assert client._circuit_breaker_state.failure_count == 0
        client.close()


class TestCircuitBreakerBehavior:
    """Tests for circuit breaker behavior."""

    @pytest.fixture
    def api_token(self) -> SecretStr:
        return SecretStr("test-token")

    def test_circuit_opens_after_threshold_failures(self, api_token: SecretStr) -> None:
        cb_config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=30.0)
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
            circuit_breaker_config=cb_config,
        )
        # Simulate failures
        client._circuit_breaker_state.record_failure(cb_config)
        assert client.circuit_state == CircuitState.CLOSED

        client._circuit_breaker_state.record_failure(cb_config)
        assert client.circuit_state == CircuitState.OPEN
        client.close()

    def test_circuit_breaker_error_when_open(self, api_token: SecretStr) -> None:
        import time

        cb_config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=60.0)
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
            circuit_breaker_config=cb_config,
        )
        # Force circuit open and set recent failure time
        client._circuit_breaker_state.state = CircuitState.OPEN
        client._circuit_breaker_state.last_failure_time = time.monotonic()

        with pytest.raises(CircuitBreakerError):
            client._check_circuit_breaker()
        client.close()

    def test_success_resets_failure_count(self, api_token: SecretStr) -> None:
        cb_config = CircuitBreakerConfig(failure_threshold=5)
        client = HTTPClient(
            api_token=api_token,
            base_url="https://api.devrev.ai",
            circuit_breaker_config=cb_config,
        )
        client._circuit_breaker_state.failure_count = 3
        client._circuit_breaker_state.record_success()
        assert client._circuit_breaker_state.failure_count == 0
        client.close()
