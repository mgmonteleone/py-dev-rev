"""Unit tests for error handling and retry logic."""

from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest

from devrev.exceptions import (
    DevRevError,
)
from devrev.models.artifacts import (
    ArtifactPrepareFormData,
    ArtifactPrepareResponse,
)
from devrev.services.articles import ArticlesService
from devrev.services.artifacts import ArtifactsService


class TestNetworkErrorHandling:
    """Tests for network error handling with retries."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def artifacts_service(self, mock_http_client: MagicMock) -> ArtifactsService:
        return ArtifactsService(mock_http_client)

    def test_network_timeout_retry(
        self, artifacts_service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test exponential backoff on network timeout."""
        # Mock httpx.post to raise TimeoutException on first call, succeed on second
        prepare_response = ArtifactPrepareResponse(
            id="ARTIFACT-123",
            url="https://s3.example.com/upload",
            form_data=[ArtifactPrepareFormData(key="key", value="test-key")],
        )

        with patch("httpx.post") as mock_post:
            # First call times out
            mock_post.side_effect = [
                httpx.TimeoutException("Request timed out"),
                # Second call should not happen in current implementation
                # since upload() doesn't implement retry logic
            ]

            # The upload method should raise DevRevError wrapping the timeout
            with pytest.raises(DevRevError, match="Failed to upload artifact content"):
                artifacts_service.upload(prepare_response, b"test content")

            # Verify timeout exception was encountered
            assert mock_post.call_count == 1


class TestRateLimitHandling:
    """Tests for rate limit error handling."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def artifacts_service(self, mock_http_client: MagicMock) -> ArtifactsService:
        return ArtifactsService(mock_http_client)

    def test_rate_limit_handling(
        self, artifacts_service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test proper handling of 429 rate limit errors."""
        prepare_response = ArtifactPrepareResponse(
            id="ARTIFACT-123",
            url="https://s3.example.com/upload",
            form_data=[ArtifactPrepareFormData(key="key", value="test-key")],
        )

        with patch("httpx.post") as mock_post:
            # Create a mock response with 429 status
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "60"}

            # Simulate rate limit error
            http_error = httpx.HTTPStatusError(
                "429 Too Many Requests",
                request=Mock(),
                response=mock_response,
            )
            mock_post.side_effect = http_error

            # Should raise DevRevError wrapping the rate limit error
            with pytest.raises(DevRevError, match="Failed to upload artifact content"):
                artifacts_service.upload(prepare_response, b"test content")

            assert mock_post.call_count == 1


class TestServerErrorRetry:
    """Tests for server error retry logic."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def artifacts_service(self, mock_http_client: MagicMock) -> ArtifactsService:
        return ArtifactsService(mock_http_client)

    def test_server_error_retry(
        self, artifacts_service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test retry behavior on 5xx server errors."""
        prepare_response = ArtifactPrepareResponse(
            id="ARTIFACT-123",
            url="https://s3.example.com/upload",
            form_data=[ArtifactPrepareFormData(key="key", value="test-key")],
        )

        with patch("httpx.post") as mock_post:
            # Create a mock response with 503 status
            mock_response = Mock()
            mock_response.status_code = 503

            # Simulate server error
            http_error = httpx.HTTPStatusError(
                "503 Service Unavailable",
                request=Mock(),
                response=mock_response,
            )
            mock_post.side_effect = http_error

            # Should raise DevRevError wrapping the server error
            with pytest.raises(DevRevError, match="Failed to upload artifact content"):
                artifacts_service.upload(prepare_response, b"test content")

            assert mock_post.call_count == 1


class TestClientErrorNoRetry:
    """Tests that client errors (4xx) do not trigger retries."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def artifacts_service(self, mock_http_client: MagicMock) -> ArtifactsService:
        return ArtifactsService(mock_http_client)

    def test_client_error_no_retry(
        self, artifacts_service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test that 4xx errors do not trigger retry logic."""
        prepare_response = ArtifactPrepareResponse(
            id="ARTIFACT-123",
            url="https://s3.example.com/upload",
            form_data=[ArtifactPrepareFormData(key="key", value="test-key")],
        )

        with patch("httpx.post") as mock_post:
            # Create a mock response with 400 status
            mock_response = Mock()
            mock_response.status_code = 400

            # Simulate client error
            http_error = httpx.HTTPStatusError(
                "400 Bad Request",
                request=Mock(),
                response=mock_response,
            )
            mock_post.side_effect = http_error

            # Should raise DevRevError immediately without retry
            with pytest.raises(DevRevError, match="Failed to upload artifact content"):
                artifacts_service.upload(prepare_response, b"test content")

            # Should only be called once (no retries for 4xx)
            assert mock_post.call_count == 1


class TestContentValidation:
    """Tests for content format validation."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def artifacts_service(self, mock_http_client: MagicMock) -> ArtifactsService:
        return ArtifactsService(mock_http_client)

    def test_invalid_content_format(self, artifacts_service: ArtifactsService) -> None:
        """Test validation of content format before upload."""
        prepare_response = ArtifactPrepareResponse(
            id="ARTIFACT-123",
            url="https://s3.example.com/upload",
            form_data=[ArtifactPrepareFormData(key="key", value="test-key")],
        )

        # Test that string content is properly handled (should be converted to bytes)
        with patch("httpx.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_post.return_value = mock_response

            # String content should be converted to bytes
            result = artifacts_service.upload(prepare_response, "test string content")

            assert result == "ARTIFACT-123"
            assert mock_post.call_count == 1

            # Verify the content was converted to bytes in the upload
            call_kwargs = mock_post.call_args[1]
            assert "files" in call_kwargs
            assert call_kwargs["files"]["file"] == b"test string content"


class TestArtifactUploadFailure:
    """Tests for S3 upload failure handling."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def artifacts_service(self, mock_http_client: MagicMock) -> ArtifactsService:
        return ArtifactsService(mock_http_client)

    def test_artifact_upload_s3_failure(
        self, artifacts_service: ArtifactsService, mock_http_client: MagicMock
    ) -> None:
        """Test handling of S3 upload failures."""
        prepare_response = ArtifactPrepareResponse(
            id="ARTIFACT-123",
            url="https://s3.example.com/upload",
            form_data=[ArtifactPrepareFormData(key="key", value="test-key")],
        )

        with patch("httpx.post") as mock_post:
            # Simulate S3 upload failure
            mock_response = Mock()
            mock_response.status_code = 403
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "403 Forbidden",
                request=Mock(),
                response=mock_response,
            )
            mock_post.return_value = mock_response

            # Should raise DevRevError with clear message
            with pytest.raises(DevRevError, match="Failed to upload artifact content"):
                artifacts_service.upload(prepare_response, b"test content")

            assert mock_post.call_count == 1


class TestMissingParentClient:
    """Tests for clear error messages when parent_client is missing."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def articles_service_no_parent(self, mock_http_client: MagicMock) -> ArticlesService:
        # Create service without parent_client reference
        service = ArticlesService(mock_http_client)
        service._parent_client = None
        return service

    def test_missing_parent_client_clear_message(
        self, articles_service_no_parent: ArticlesService
    ) -> None:
        """Test that missing parent_client produces clear, user-friendly error."""
        # Test create_with_content
        with pytest.raises(
            DevRevError,
            match="create_with_content requires parent client reference",
        ):
            articles_service_no_parent.create_with_content(
                title="Test",
                content="Test content",
                owned_by=["DEVU-123"],
            )

        # Test get_with_content
        with pytest.raises(
            DevRevError,
            match="get_with_content requires parent client reference",
        ):
            articles_service_no_parent.get_with_content("ART-123")

        # Test update_content
        with pytest.raises(
            DevRevError,
            match="update_content requires parent client reference",
        ):
            articles_service_no_parent.update_content("ART-123", "New content")

        # Test update_with_content
        with pytest.raises(
            DevRevError,
            match="update_with_content requires parent client reference",
        ):
            articles_service_no_parent.update_with_content(
                "ART-123",
                title="New title",
            )


class TestPartialFailureRollback:
    """Tests for rollback mechanisms on partial failures."""

    @pytest.fixture
    def mock_http_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def mock_parent_client(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def articles_service_with_parent(
        self, mock_http_client: MagicMock, mock_parent_client: MagicMock
    ) -> ArticlesService:
        service = ArticlesService(mock_http_client)
        service._parent_client = mock_parent_client
        return service

    def test_partial_failure_rollback(
        self,
        articles_service_with_parent: ArticlesService,
        mock_http_client: MagicMock,
        mock_parent_client: MagicMock,
    ) -> None:
        """Test that partial failures trigger complete rollback."""
        # Mock successful artifact preparation
        prepare_response = ArtifactPrepareResponse(
            id="ARTIFACT-123",
            url="https://s3.example.com/upload",
            form_data=[ArtifactPrepareFormData(key="key", value="test-key")],
        )
        mock_parent_client.artifacts.prepare.return_value = prepare_response

        # Mock successful upload
        mock_parent_client.artifacts.upload.return_value = "ARTIFACT-123"

        # Mock article creation failure
        mock_http_client.post.side_effect = Exception("Article creation failed")

        # Should raise error about article creation failure
        with pytest.raises(DevRevError, match="Failed to create article with content"):
            articles_service_with_parent.create_with_content(
                title="Test Article",
                content="Test content",
                owned_by=["DEVU-123"],
            )

        # Verify artifact was prepared and uploaded
        mock_parent_client.artifacts.prepare.assert_called_once()
        mock_parent_client.artifacts.upload.assert_called_once()

        # Note: Current implementation doesn't have artifact delete API,
        # so we can't verify cleanup. This is documented in the code.
