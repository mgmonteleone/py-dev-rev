"""Unit tests for exception hierarchy."""

import pytest

from devrev.exceptions import (
    STATUS_CODE_TO_EXCEPTION,
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    DevRevError,
    ForbiddenError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)


class TestDevRevError:
    """Tests for base DevRevError class."""

    def test_basic_error(self) -> None:
        """Test basic error creation."""
        error = DevRevError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"

    def test_error_with_status_code(self) -> None:
        """Test error with status code."""
        error = DevRevError("Not found", status_code=404)
        assert "404" in str(error)
        assert error.status_code == 404

    def test_error_with_request_id(self) -> None:
        """Test error with request ID."""
        error = DevRevError("Error", request_id="req-123-abc")
        assert "req-123-abc" in str(error)
        assert error.request_id == "req-123-abc"

    def test_error_with_response_body(self) -> None:
        """Test error with response body."""
        body = {"error": "details"}
        error = DevRevError("Error", response_body=body)
        assert error.response_body == body

    def test_full_error_string(self) -> None:
        """Test error string with all components."""
        error = DevRevError(
            "Something went wrong",
            status_code=500,
            request_id="req-xyz",
        )
        error_str = str(error)
        assert "Something went wrong" in error_str
        assert "500" in error_str
        assert "req-xyz" in error_str


class TestValidationError:
    """Tests for ValidationError class."""

    def test_validation_error_with_field_errors(self) -> None:
        """Test validation error with field-level errors."""
        error = ValidationError(
            "Invalid request",
            field_errors={"email": ["Invalid format", "Required"]},
            status_code=400,
        )
        assert error.field_errors == {"email": ["Invalid format", "Required"]}
        assert error.status_code == 400

    def test_validation_error_default_field_errors(self) -> None:
        """Test that field_errors defaults to empty dict."""
        error = ValidationError("Invalid request")
        assert error.field_errors == {}


class TestRateLimitError:
    """Tests for RateLimitError class."""

    def test_rate_limit_error_with_retry_after(self) -> None:
        """Test rate limit error with retry-after header."""
        error = RateLimitError(
            "Rate limit exceeded",
            retry_after=60,
            status_code=429,
        )
        assert error.retry_after == 60
        assert error.status_code == 429

    def test_rate_limit_error_default_retry_after(self) -> None:
        """Test that retry_after defaults to None."""
        error = RateLimitError("Rate limit exceeded")
        assert error.retry_after is None


class TestExceptionHierarchy:
    """Tests for exception inheritance."""

    def test_all_exceptions_inherit_from_devrev_error(self) -> None:
        """Test that all exceptions inherit from DevRevError."""
        exceptions = [
            AuthenticationError,
            ForbiddenError,
            NotFoundError,
            ValidationError,
            ConflictError,
            RateLimitError,
            ServerError,
            ServiceUnavailableError,
            ConfigurationError,
            TimeoutError,
            NetworkError,
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, DevRevError)

    def test_catching_base_exception(self) -> None:
        """Test that DevRevError catches all SDK exceptions."""
        with pytest.raises(DevRevError):
            raise AuthenticationError("Auth failed")

        with pytest.raises(DevRevError):
            raise ValidationError("Invalid", field_errors={})


class TestStatusCodeMapping:
    """Tests for status code to exception mapping."""

    def test_status_code_mapping(self) -> None:
        """Test that status codes map to correct exceptions."""
        assert STATUS_CODE_TO_EXCEPTION[400] == ValidationError
        assert STATUS_CODE_TO_EXCEPTION[401] == AuthenticationError
        assert STATUS_CODE_TO_EXCEPTION[403] == ForbiddenError
        assert STATUS_CODE_TO_EXCEPTION[404] == NotFoundError
        assert STATUS_CODE_TO_EXCEPTION[409] == ConflictError
        assert STATUS_CODE_TO_EXCEPTION[429] == RateLimitError
        assert STATUS_CODE_TO_EXCEPTION[500] == ServerError
        assert STATUS_CODE_TO_EXCEPTION[503] == ServiceUnavailableError
