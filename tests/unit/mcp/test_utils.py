"""Unit tests for MCP utility modules."""

from pydantic import BaseModel

from devrev.exceptions import (
    AuthenticationError,
    BetaAPIRequiredError,
    ConflictError,
    DevRevError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    TimeoutError,
    ValidationError,
)
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import (
    format_account_summary,
    format_user_summary,
    format_work_summary,
    serialize_model,
    serialize_models,
)
from devrev_mcp.utils.pagination import clamp_page_size, paginated_response


class TestPagination:
    """Tests for pagination utilities."""

    def test_clamp_page_size_none_returns_default(self) -> None:
        """Test that None returns the default page size."""
        assert clamp_page_size(None) == 25

    def test_clamp_page_size_within_bounds_returned_as_is(self) -> None:
        """Test that values within bounds are returned unchanged."""
        assert clamp_page_size(10) == 10
        assert clamp_page_size(50) == 50
        assert clamp_page_size(100) == 100

    def test_clamp_page_size_above_max_clamped_to_max(self) -> None:
        """Test that values above maximum are clamped to maximum."""
        assert clamp_page_size(150) == 100
        assert clamp_page_size(1000) == 100

    def test_clamp_page_size_zero_or_negative_clamped_to_one(self) -> None:
        """Test that zero or negative values are clamped to 1."""
        assert clamp_page_size(0) == 1
        assert clamp_page_size(-5) == 1
        assert clamp_page_size(-100) == 1

    def test_clamp_page_size_custom_default_and_maximum(self) -> None:
        """Test that custom default and maximum values work."""
        assert clamp_page_size(None, default=50, maximum=200) == 50
        assert clamp_page_size(75, default=50, maximum=200) == 75
        assert clamp_page_size(250, default=50, maximum=200) == 200
        assert clamp_page_size(0, default=50, maximum=200) == 1

    def test_paginated_response_basic(self) -> None:
        """Test basic paginated response without cursor."""
        items = [{"id": "1"}, {"id": "2"}]
        result = paginated_response(items)

        assert result["count"] == 2
        assert result["items"] == items
        assert "next_cursor" not in result

    def test_paginated_response_with_cursor(self) -> None:
        """Test paginated response includes next_cursor when provided."""
        items = [{"id": "1"}]
        result = paginated_response(items, next_cursor="cursor123")

        assert result["count"] == 1
        assert result["items"] == items
        assert result["next_cursor"] == "cursor123"

    def test_paginated_response_custom_total_label(self) -> None:
        """Test paginated response with custom total_label."""
        items = [{"id": "1"}, {"id": "2"}]
        result = paginated_response(items, total_label="works")

        assert result["count"] == 2
        assert result["works"] == items
        assert "items" not in result

    def test_paginated_response_empty_list(self) -> None:
        """Test paginated response with empty list."""
        result = paginated_response([])

        assert result["count"] == 0
        assert result["items"] == []


class TestErrors:
    """Tests for error formatting utilities."""

    def test_format_authentication_error(self) -> None:
        """Test formatting of AuthenticationError."""
        error = AuthenticationError("bad token")
        result = format_devrev_error(error)

        assert "Authentication failed" in result
        assert "bad token" in result
        assert "DEVREV_API_TOKEN" in result

    def test_format_forbidden_error(self) -> None:
        """Test formatting of ForbiddenError."""
        error = ForbiddenError("no access")
        result = format_devrev_error(error)

        assert "Permission denied" in result
        assert "no access" in result

    def test_format_not_found_error(self) -> None:
        """Test formatting of NotFoundError."""
        error = NotFoundError("missing")
        result = format_devrev_error(error)

        assert "Not found" in result
        assert "missing" in result

    def test_format_validation_error_with_field_errors(self) -> None:
        """Test formatting of ValidationError with field errors."""
        error = ValidationError("invalid", field_errors={"name": ["required"]})
        result = format_devrev_error(error)

        assert "Validation error" in result
        assert "invalid" in result
        assert "name" in result

    def test_format_validation_error_without_field_errors(self) -> None:
        """Test formatting of ValidationError without field errors."""
        error = ValidationError("invalid")
        result = format_devrev_error(error)

        assert "Validation error" in result
        assert "invalid" in result

    def test_format_conflict_error(self) -> None:
        """Test formatting of ConflictError."""
        error = ConflictError("duplicate")
        result = format_devrev_error(error)

        assert "Conflict" in result
        assert "duplicate" in result

    def test_format_rate_limit_error_with_retry_after(self) -> None:
        """Test formatting of RateLimitError with retry_after."""
        error = RateLimitError("slow down", retry_after=30)
        result = format_devrev_error(error)

        assert "Rate limited" in result
        assert "slow down" in result
        assert "30" in result

    def test_format_rate_limit_error_without_retry_after(self) -> None:
        """Test formatting of RateLimitError without retry_after."""
        error = RateLimitError("slow down")
        result = format_devrev_error(error)

        assert "Rate limited" in result
        assert "slow down" in result
        # Should not contain retry info
        assert "Retry after" not in result

    def test_format_server_error(self) -> None:
        """Test formatting of ServerError."""
        error = ServerError("crash")
        result = format_devrev_error(error)

        assert "server error" in result
        assert "crash" in result

    def test_format_service_unavailable_error(self) -> None:
        """Test formatting of ServiceUnavailableError."""
        error = ServiceUnavailableError("down")
        result = format_devrev_error(error)

        assert "unavailable" in result
        assert "down" in result

    def test_format_timeout_error(self) -> None:
        """Test formatting of TimeoutError."""
        error = TimeoutError("timeout")
        result = format_devrev_error(error)

        assert "timed out" in result
        assert "timeout" in result

    def test_format_beta_api_required_error(self) -> None:
        """Test formatting of BetaAPIRequiredError."""
        error = BetaAPIRequiredError("beta only")
        result = format_devrev_error(error)

        assert "Beta API required" in result
        assert "beta only" in result

    def test_format_generic_devrev_error(self) -> None:
        """Test formatting of generic DevRevError."""
        error = DevRevError("unknown")
        result = format_devrev_error(error)

        assert "API error" in result
        assert "unknown" in result


class TestFormatting:
    """Tests for formatting and serialization utilities."""

    def test_serialize_model_basic(self) -> None:
        """Test serializing a basic Pydantic model."""

        class SampleModel(BaseModel):
            id: str
            name: str | None = None
            value: int = 0

        model = SampleModel(id="123", name="test", value=42)
        result = serialize_model(model)

        assert result == {"id": "123", "name": "test", "value": 42}

    def test_serialize_model_excludes_none(self) -> None:
        """Test that None fields are excluded from serialization."""

        class SampleModel(BaseModel):
            id: str
            name: str | None = None
            value: int = 0

        model = SampleModel(id="123", value=10)
        result = serialize_model(model)

        assert result == {"id": "123", "value": 10}
        assert "name" not in result

    def test_serialize_models_list(self) -> None:
        """Test serializing a list of models."""

        class SampleModel(BaseModel):
            id: str
            name: str | None = None

        models = [
            SampleModel(id="1", name="first"),
            SampleModel(id="2"),
            SampleModel(id="3", name="third"),
        ]
        result = serialize_models(models)

        assert len(result) == 3
        assert result[0] == {"id": "1", "name": "first"}
        assert result[1] == {"id": "2"}
        assert result[2] == {"id": "3", "name": "third"}

    def test_serialize_models_empty_list(self) -> None:
        """Test serializing an empty list."""
        result = serialize_models([])
        assert result == []

    def test_format_work_summary_complete(self) -> None:
        """Test formatting a complete work item summary."""
        work_data = {
            "display_id": "TKT-123",
            "title": "Bug",
            "type": "ticket",
            "stage": {"name": "open"},
        }
        result = format_work_summary(work_data)

        assert result == "[TKT-123] (ticket) Bug — stage: open"

    def test_format_work_summary_missing_fields(self) -> None:
        """Test formatting work summary with missing fields uses defaults."""
        work_data = {}
        result = format_work_summary(work_data)

        assert result == "[?] (unknown) Untitled — stage: unknown"

    def test_format_work_summary_partial_fields(self) -> None:
        """Test formatting work summary with some fields present."""
        work_data = {
            "display_id": "ISS-456",
            "type": "issue",
        }
        result = format_work_summary(work_data)

        assert result == "[ISS-456] (issue) Untitled — stage: unknown"

    def test_format_account_summary_complete(self) -> None:
        """Test formatting a complete account summary."""
        account_data = {
            "display_name": "Acme",
            "display_id": "ACC-1",
            "tier": "tier-1",
        }
        result = format_account_summary(account_data)

        assert result == "[ACC-1] Acme (tier: tier-1)"

    def test_format_account_summary_without_tier(self) -> None:
        """Test formatting account summary without tier."""
        account_data = {
            "display_name": "Acme",
            "display_id": "ACC-1",
        }
        result = format_account_summary(account_data)

        assert result == "[ACC-1] Acme"
        assert "tier" not in result

    def test_format_account_summary_missing_fields(self) -> None:
        """Test formatting account summary with missing fields uses defaults."""
        account_data = {}
        result = format_account_summary(account_data)

        assert result == "[?] Unnamed"

    def test_format_user_summary_complete(self) -> None:
        """Test formatting a complete user summary."""
        user_data = {
            "display_name": "Jane",
            "email": "jane@test.com",
            "state": "active",
        }
        result = format_user_summary(user_data)

        assert result == "Jane <jane@test.com> [active]"

    def test_format_user_summary_without_email(self) -> None:
        """Test formatting user summary without email."""
        user_data = {
            "display_name": "Jane",
            "state": "active",
        }
        result = format_user_summary(user_data)

        assert result == "Jane [active]"
        assert "@" not in result

    def test_format_user_summary_without_state(self) -> None:
        """Test formatting user summary without state."""
        user_data = {
            "display_name": "Jane",
            "email": "jane@test.com",
        }
        result = format_user_summary(user_data)

        assert result == "Jane <jane@test.com>"
        assert "[" not in result

    def test_format_user_summary_missing_fields(self) -> None:
        """Test formatting user summary with missing fields uses defaults."""
        user_data = {}
        result = format_user_summary(user_data)

        assert result == "Unknown"
