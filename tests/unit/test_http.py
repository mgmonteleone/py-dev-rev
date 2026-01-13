"""Unit tests for HTTP client utilities."""

import httpx
import pytest
import respx
from pydantic import SecretStr

from devrev.exceptions import (
    AuthenticationError,
    DevRevError,
    NotFoundError,
    RateLimitError,
)
from devrev.utils.http import (
    DEFAULT_RETRY_STATUS_CODES,
    AsyncHTTPClient,
    HTTPClient,
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
