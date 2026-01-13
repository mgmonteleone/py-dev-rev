"""Unit tests for base service classes."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from devrev.services.base import AsyncBaseService, BaseService


class SampleRequest(BaseModel):
    """Sample request model for testing."""

    name: str
    value: int | None = None


class SampleResponse(BaseModel):
    """Sample response model for testing."""

    id: str
    name: str


class TestBaseService:
    """Tests for BaseService class."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def service(self, mock_http_client: MagicMock) -> BaseService:
        return BaseService(mock_http_client)

    def test_initialization(self, service: BaseService, mock_http_client: MagicMock) -> None:
        assert service._http is mock_http_client

    def test_post_with_response_type(
        self, service: BaseService, mock_http_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "123", "name": "Test"}
        mock_http_client.post.return_value = mock_response
        request = SampleRequest(name="Test", value=42)
        result = service._post("/test.endpoint", request, SampleResponse)
        assert isinstance(result, SampleResponse)
        assert result.id == "123"

    def test_post_without_response_type(
        self, service: BaseService, mock_http_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "123", "raw": "data"}
        mock_http_client.post.return_value = mock_response
        result = service._post("/test.endpoint")
        assert isinstance(result, dict)

    def test_post_excludes_none_values(
        self, service: BaseService, mock_http_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "123", "name": "Test"}
        mock_http_client.post.return_value = mock_response
        request = SampleRequest(name="Test", value=None)
        service._post("/test.endpoint", request, SampleResponse)
        call_args = mock_http_client.post.call_args
        data = call_args[1]["data"]
        assert "value" not in data

    def test_get_with_response_type(
        self, service: BaseService, mock_http_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "456", "name": "GetTest"}
        mock_http_client.get.return_value = mock_response
        result = service._get("/test.get", {"filter": "value"}, SampleResponse)
        assert isinstance(result, SampleResponse)
        assert result.id == "456"

    def test_get_without_response_type(
        self, service: BaseService, mock_http_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "raw"}
        mock_http_client.get.return_value = mock_response
        result = service._get("/test.get")
        assert isinstance(result, dict)


class TestAsyncBaseService:
    """Tests for AsyncBaseService class."""

    @pytest.fixture
    def mock_async_http_client(self) -> MagicMock:
        client = MagicMock()
        client.post = AsyncMock()
        client.get = AsyncMock()
        return client

    @pytest.fixture
    def async_service(self, mock_async_http_client: MagicMock) -> AsyncBaseService:
        return AsyncBaseService(mock_async_http_client)

    def test_initialization(
        self, async_service: AsyncBaseService, mock_async_http_client: MagicMock
    ) -> None:
        assert async_service._http is mock_async_http_client

    @pytest.mark.asyncio
    async def test_async_post_with_response_type(
        self, async_service: AsyncBaseService, mock_async_http_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "async123", "name": "AsyncTest"}
        mock_async_http_client.post.return_value = mock_response
        request = SampleRequest(name="AsyncTest")
        result = await async_service._post("/async.endpoint", request, SampleResponse)
        assert isinstance(result, SampleResponse)
        assert result.id == "async123"

    @pytest.mark.asyncio
    async def test_async_get_with_response_type(
        self, async_service: AsyncBaseService, mock_async_http_client: MagicMock
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "async456", "name": "AsyncGet"}
        mock_async_http_client.get.return_value = mock_response
        result = await async_service._get("/async.get", {"param": "val"}, SampleResponse)
        assert isinstance(result, SampleResponse)
        assert result.name == "AsyncGet"
