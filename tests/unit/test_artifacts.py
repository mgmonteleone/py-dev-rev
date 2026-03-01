"""Unit tests for Artifacts service."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest

from devrev.exceptions import DevRevError, NotFoundError
from devrev.models.artifacts import (
    Artifact,
    ArtifactGetRequest,
    ArtifactLocateRequest,
    ArtifactPrepareFormData,
    ArtifactPrepareRequest,
    ArtifactPrepareResponse,
    ArtifactVersionsDeleteRequest,
    ArtifactVersionsPrepareRequest,
    ArtifactVersionsPrepareResponse,
)
from devrev.services.artifacts import ArtifactsService, AsyncArtifactsService


@pytest.fixture
def sample_artifact() -> Artifact:
    """Create a sample artifact for testing."""
    return Artifact(
        id="ARTIFACT-12345",
        created_by="DEVU-1",
        created_date=datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
        file_name="test.html",
        file_type="text/html",
        file_size=1024,
        version="v1",
    )


@pytest.fixture
def sample_prepare_response() -> ArtifactPrepareResponse:
    """Create a sample prepare response for testing."""
    return ArtifactPrepareResponse(
        id="ARTIFACT-12345",
        url="https://s3.example.com/upload",
        form_data=[
            ArtifactPrepareFormData(key="key", value="test-key"),
            ArtifactPrepareFormData(key="policy", value="test-policy"),
            ArtifactPrepareFormData(key="signature", value="test-signature"),
        ],
    )


class TestArtifactsService:
    """Tests for ArtifactsService class."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def service(self, mock_http_client: MagicMock) -> ArtifactsService:
        return ArtifactsService(mock_http_client)

    def test_prepare_artifact_success(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test successful artifact preparation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ARTIFACT-12345",
            "url": "https://s3.example.com/upload",
            "form_data": [
                {"key": "key", "value": "test-key"},
                {"key": "policy", "value": "test-policy"},
            ],
        }
        mock_http_client.post.return_value = mock_response

        request = ArtifactPrepareRequest(file_name="test.html", file_type="text/html")
        result = service.prepare(request)

        assert isinstance(result, ArtifactPrepareResponse)
        assert result.id == "ARTIFACT-12345"
        assert result.url == "https://s3.example.com/upload"
        assert len(result.form_data) == 2
        mock_http_client.post.assert_called_once()

    def test_prepare_artifact_with_configuration_set(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test artifact preparation with configuration_set parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ARTIFACT-12345",
            "url": "https://s3.example.com/upload",
            "form_data": [{"key": "key", "value": "test-key"}],
        }
        mock_http_client.post.return_value = mock_response

        request = ArtifactPrepareRequest(
            file_name="article.html",
            file_type="text/html",
            configuration_set="article_media",
        )
        result = service.prepare(request)

        assert result.id == "ARTIFACT-12345"
        # Verify configuration_set was included in request
        call_args = mock_http_client.post.call_args
        data = call_args[1]["data"]
        assert "configuration_set" in data
        assert data["configuration_set"] == "article_media"

    @patch("devrev.services.artifacts.httpx")
    def test_upload_artifact_success(
        self,
        mock_httpx: Mock,
        service: ArtifactsService,
        sample_prepare_response: ArtifactPrepareResponse,
    ) -> None:
        """Test successful artifact upload."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_httpx.post.return_value = mock_response

        content = b"<html>Test content</html>"
        artifact_id = service.upload(sample_prepare_response, content)

        assert artifact_id == "ARTIFACT-12345"
        mock_httpx.post.assert_called_once()
        call_args = mock_httpx.post.call_args
        assert call_args[0][0] == "https://s3.example.com/upload"
        assert "files" in call_args[1]
        assert call_args[1]["files"]["file"] == content

    @patch("devrev.services.artifacts.httpx")
    def test_upload_artifact_with_string_content(
        self,
        mock_httpx: Mock,
        service: ArtifactsService,
        sample_prepare_response: ArtifactPrepareResponse,
    ) -> None:
        """Test artifact upload with string content (should be converted to bytes)."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_httpx.post.return_value = mock_response

        content = "<html>Test content</html>"
        artifact_id = service.upload(sample_prepare_response, content)

        assert artifact_id == "ARTIFACT-12345"
        call_args = mock_httpx.post.call_args
        # Verify string was converted to bytes
        assert call_args[1]["files"]["file"] == content.encode("utf-8")

    def test_get_artifact_success(
        self,
        service: ArtifactsService,
        mock_http_client: MagicMock,
        sample_artifact: Artifact,
    ) -> None:
        """Test successful artifact retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifact": {
                "id": "ARTIFACT-12345",
                "created_by": "DEVU-1",
                "created_date": "2024-01-01T12:00:00Z",
                "file_name": "test.html",
                "file_type": "text/html",
                "file_size": 1024,
                "version": "v1",
            }
        }
        mock_http_client.post.return_value = mock_response

        request = ArtifactGetRequest(id="ARTIFACT-12345")
        result = service.get(request)

        assert isinstance(result, Artifact)
        assert result.id == "ARTIFACT-12345"
        assert result.file_name == "test.html"
        mock_http_client.post.assert_called_once()

    def test_get_artifact_with_version(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test artifact retrieval with specific version."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifact": {
                "id": "ARTIFACT-12345",
                "version": "v2",
                "file_name": "test.html",
            }
        }
        mock_http_client.post.return_value = mock_response

        request = ArtifactGetRequest(id="ARTIFACT-12345", version="v2")
        result = service.get(request)

        assert result.version == "v2"

    def test_get_artifact_not_found(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test artifact get raises NotFoundError for missing artifact."""
        mock_http_client.post.side_effect = NotFoundError(
            message="Artifact not found", status_code=404, response_body=None
        )

        request = ArtifactGetRequest(id="NONEXISTENT")
        with pytest.raises(NotFoundError):
            service.get(request)

    def test_locate_artifact_success(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test successful artifact location."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "url": "https://s3.example.com/download/test.html?signature=xyz"
        }
        mock_http_client.post.return_value = mock_response

        request = ArtifactLocateRequest(id="ARTIFACT-12345")
        url = service.locate(request)

        assert url == "https://s3.example.com/download/test.html?signature=xyz"
        mock_http_client.post.assert_called_once()

    @patch("devrev.services.artifacts.httpx")
    def test_download_artifact_success(
        self, mock_httpx: Mock, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test successful artifact download."""
        # Mock locate response
        locate_response = MagicMock()
        locate_response.json.return_value = {"url": "https://s3.example.com/download/test.html"}
        mock_http_client.post.return_value = locate_response

        # Mock download response
        download_response = MagicMock()
        download_response.content = b"<html>Downloaded content</html>"
        download_response.raise_for_status = MagicMock()
        mock_httpx.get.return_value = download_response

        content = service.download("ARTIFACT-12345")

        assert content == b"<html>Downloaded content</html>"
        mock_httpx.get.assert_called_once()
        mock_httpx.get.assert_called_with("https://s3.example.com/download/test.html", timeout=60.0)

    @patch("devrev.services.artifacts.httpx")
    def test_download_artifact_with_version(
        self, mock_httpx: Mock, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test artifact download with specific version."""
        locate_response = MagicMock()
        locate_response.json.return_value = {
            "url": "https://s3.example.com/download/test.html?version=v2"
        }
        mock_http_client.post.return_value = locate_response

        download_response = MagicMock()
        download_response.content = b"Version 2 content"
        download_response.raise_for_status = MagicMock()
        mock_httpx.get.return_value = download_response

        content = service.download("ARTIFACT-12345", version="v2")

        assert content == b"Version 2 content"
        # Verify version was passed to locate
        call_args = mock_http_client.post.call_args
        data = call_args[1]["data"]
        assert data["version"] == "v2"

    @patch("devrev.services.artifacts.httpx")
    def test_download_artifact_large_file(
        self, mock_httpx: Mock, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test downloading large artifact file."""
        locate_response = MagicMock()
        locate_response.json.return_value = {"url": "https://s3.example.com/download/large.bin"}
        mock_http_client.post.return_value = locate_response

        # Simulate large file (1MB)
        large_content = b"x" * (1024 * 1024)
        download_response = MagicMock()
        download_response.content = large_content
        download_response.raise_for_status = MagicMock()
        mock_httpx.get.return_value = download_response

        content = service.download("ARTIFACT-12345")

        assert len(content) == 1024 * 1024
        assert content == large_content

    def test_list_for_parent_success(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test listing artifacts for a parent object."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifacts": [
                {"id": "ARTIFACT-1", "file_name": "file1.html"},
                {"id": "ARTIFACT-2", "file_name": "file2.html"},
            ]
        }
        mock_http_client.post.return_value = mock_response

        artifacts = service.list_for_parent("ART-12345")

        assert len(artifacts) == 2
        assert artifacts[0].id == "ARTIFACT-1"
        assert artifacts[1].file_name == "file2.html"
        mock_http_client.post.assert_called_once()

    def test_list_for_parent_empty_result(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test listing artifacts when parent has no artifacts."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"artifacts": []}
        mock_http_client.post.return_value = mock_response

        artifacts = service.list_for_parent("ART-12345")

        assert len(artifacts) == 0

    def test_prepare_version_success(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test preparing a new artifact version."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ARTIFACT-12345",
            "url": "https://s3.example.com/upload-v2",
            "form_data": [{"key": "key", "value": "version-key"}],
        }
        mock_http_client.post.return_value = mock_response

        request = ArtifactVersionsPrepareRequest(id="ARTIFACT-12345")
        result = service.prepare_version(request)

        assert isinstance(result, ArtifactVersionsPrepareResponse)
        assert result.id == "ARTIFACT-12345"
        assert "upload-v2" in result.url
        mock_http_client.post.assert_called_once()

    def test_delete_version_success(
        self, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test deleting an artifact version."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_http_client.post.return_value = mock_response

        request = ArtifactVersionsDeleteRequest(id="ARTIFACT-12345", version="v2")
        # Should not raise an exception
        service.delete_version(request)

        mock_http_client.post.assert_called_once()

    @patch("devrev.services.artifacts.httpx.post")
    def test_upload_failure_handling(
        self,
        mock_post: Mock,
        service: ArtifactsService,
        sample_prepare_response: ArtifactPrepareResponse,
    ) -> None:
        """Test upload failure raises DevRevError."""
        mock_post.side_effect = httpx.ConnectError("Network error")

        content = b"Test content"
        with pytest.raises(DevRevError) as exc_info:
            service.upload(sample_prepare_response, content)

        assert "Failed to upload artifact content" in str(exc_info.value)

    @patch("devrev.services.artifacts.httpx.get")
    def test_download_failure_handling(
        self, mock_get: Mock, service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test download failure raises DevRevError."""
        locate_response = MagicMock()
        locate_response.json.return_value = {"url": "https://s3.example.com/file"}
        mock_http_client.post.return_value = locate_response

        mock_get.side_effect = httpx.ConnectError("Download failed")

        with pytest.raises(DevRevError) as exc_info:
            service.download("ARTIFACT-12345")

        assert "Failed to download artifact content" in str(exc_info.value)


class TestAsyncArtifactsService:
    """Tests for AsyncArtifactsService class."""

    @pytest.fixture
    def mock_async_http_client(self) -> MagicMock:
        client = MagicMock()
        client.post = AsyncMock()
        client.get = AsyncMock()
        return client

    @pytest.fixture
    def async_service(self, mock_async_http_client: MagicMock) -> AsyncArtifactsService:
        return AsyncArtifactsService(mock_async_http_client)

    @pytest.mark.asyncio
    async def test_async_prepare_artifact_success(
        self, async_service: AsyncArtifactsService, mock_async_http_client: MagicMock
    ) -> None:
        """Test async artifact preparation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ARTIFACT-12345",
            "url": "https://s3.example.com/upload",
            "form_data": [{"key": "key", "value": "test-key"}],
        }
        mock_async_http_client.post.return_value = mock_response

        request = ArtifactPrepareRequest(file_name="test.html")
        result = await async_service.prepare(request)

        assert isinstance(result, ArtifactPrepareResponse)
        assert result.id == "ARTIFACT-12345"

    @pytest.mark.asyncio
    async def test_async_prepare_with_configuration_set(
        self, async_service: AsyncArtifactsService, mock_async_http_client: MagicMock
    ) -> None:
        """Test async artifact preparation with configuration_set."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ARTIFACT-12345",
            "url": "https://s3.example.com/upload",
            "form_data": [{"key": "key", "value": "test-key"}],
        }
        mock_async_http_client.post.return_value = mock_response

        request = ArtifactPrepareRequest(
            file_name="article.html", configuration_set="article_media"
        )
        result = await async_service.prepare(request)

        assert result.id == "ARTIFACT-12345"

    @pytest.mark.asyncio
    async def test_async_upload_artifact_success(
        self, async_service: AsyncArtifactsService, sample_prepare_response: ArtifactPrepareResponse
    ) -> None:
        """Test async artifact upload."""
        with patch("devrev.services.artifacts.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            content = b"<html>Test content</html>"
            artifact_id = await async_service.upload(sample_prepare_response, content)

            assert artifact_id == "ARTIFACT-12345"
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_upload_with_string_content(
        self, async_service: AsyncArtifactsService, sample_prepare_response: ArtifactPrepareResponse
    ) -> None:
        """Test async upload with string content."""
        with patch("devrev.services.artifacts.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            content = "<html>String content</html>"
            artifact_id = await async_service.upload(sample_prepare_response, content)

            assert artifact_id == "ARTIFACT-12345"

    @pytest.mark.asyncio
    async def test_async_get_artifact_success(
        self,
        async_service: AsyncArtifactsService,
        mock_async_http_client: MagicMock,
        sample_artifact: Artifact,
    ) -> None:
        """Test async artifact retrieval."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifact": {
                "id": "ARTIFACT-12345",
                "file_name": "test.html",
            }
        }
        mock_async_http_client.post.return_value = mock_response

        request = ArtifactGetRequest(id="ARTIFACT-12345")
        result = await async_service.get(request)

        assert isinstance(result, Artifact)
        assert result.id == "ARTIFACT-12345"

    @pytest.mark.asyncio
    async def test_async_get_artifact_not_found(
        self, async_service: AsyncArtifactsService, mock_async_http_client: MagicMock
    ) -> None:
        """Test async artifact get raises NotFoundError."""
        mock_async_http_client.post.side_effect = NotFoundError(
            message="Not found", status_code=404, response_body=None
        )

        request = ArtifactGetRequest(id="NONEXISTENT")
        with pytest.raises(NotFoundError):
            await async_service.get(request)

    @pytest.mark.asyncio
    async def test_async_locate_artifact_success(
        self, async_service: AsyncArtifactsService, mock_async_http_client: MagicMock
    ) -> None:
        """Test async artifact location."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"url": "https://s3.example.com/download"}
        mock_async_http_client.post.return_value = mock_response

        request = ArtifactLocateRequest(id="ARTIFACT-12345")
        url = await async_service.locate(request)

        assert "s3.example.com" in url

    @pytest.mark.asyncio
    async def test_async_download_artifact_success(
        self, async_service: AsyncArtifactsService, mock_async_http_client: MagicMock
    ) -> None:
        """Test async artifact download."""
        locate_response = MagicMock()
        locate_response.json.return_value = {"url": "https://s3.example.com/file"}
        mock_async_http_client.post.return_value = locate_response

        with patch("devrev.services.artifacts.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            download_response = MagicMock()
            download_response.content = b"Downloaded content"
            download_response.raise_for_status = MagicMock()
            mock_client.get = AsyncMock(return_value=download_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            content = await async_service.download("ARTIFACT-12345")

            assert content == b"Downloaded content"

    @pytest.mark.asyncio
    async def test_async_download_large_file(
        self, async_service: AsyncArtifactsService, mock_async_http_client: MagicMock
    ) -> None:
        """Test async download of large file."""
        locate_response = MagicMock()
        locate_response.json.return_value = {"url": "https://s3.example.com/large"}
        mock_async_http_client.post.return_value = locate_response

        large_content = b"x" * (1024 * 1024)
        with patch("devrev.services.artifacts.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            download_response = MagicMock()
            download_response.content = large_content
            download_response.raise_for_status = MagicMock()
            mock_client.get = AsyncMock(return_value=download_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            content = await async_service.download("ARTIFACT-12345")

            assert len(content) == 1024 * 1024

    @pytest.mark.asyncio
    async def test_async_list_for_parent_success(
        self, async_service: AsyncArtifactsService, mock_async_http_client: MagicMock
    ) -> None:
        """Test async listing of artifacts."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "artifacts": [
                {"id": "ARTIFACT-1", "file_name": "file1.html"},
                {"id": "ARTIFACT-2", "file_name": "file2.html"},
            ]
        }
        mock_async_http_client.post.return_value = mock_response

        artifacts = await async_service.list_for_parent("ART-12345")

        assert len(artifacts) == 2
        assert artifacts[0].id == "ARTIFACT-1"

    @pytest.mark.asyncio
    async def test_async_prepare_version_success(
        self, async_service: AsyncArtifactsService, mock_async_http_client: MagicMock
    ) -> None:
        """Test async version preparation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ARTIFACT-12345",
            "url": "https://s3.example.com/upload-v2",
            "form_data": [{"key": "key", "value": "version-key"}],
        }
        mock_async_http_client.post.return_value = mock_response

        request = ArtifactVersionsPrepareRequest(id="ARTIFACT-12345")
        result = await async_service.prepare_version(request)

        assert result.id == "ARTIFACT-12345"

    @pytest.mark.asyncio
    async def test_async_upload_failure_handling(
        self, async_service: AsyncArtifactsService, sample_prepare_response: ArtifactPrepareResponse
    ) -> None:
        """Test async upload failure raises DevRevError."""
        with patch("devrev.services.artifacts.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client.post = AsyncMock(side_effect=httpx.HTTPError("Network error"))
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client_class.return_value = mock_client

            content = b"Test content"
            with pytest.raises(DevRevError) as exc_info:
                await async_service.upload(sample_prepare_response, content)

            assert "Failed to upload artifact content" in str(exc_info.value)
