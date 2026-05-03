"""Unit tests for SurveyResponsesService."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from devrev.models.survey_responses import (
    SurveyResponse,
    SurveyResponsesListMode,
    SurveyResponsesListResponse,
)
from devrev.services.survey_responses import AsyncSurveyResponsesService, SurveyResponsesService


def create_mock_response(data: dict[str, Any], status_code: int = 200) -> MagicMock:
    """Create a mock HTTP response."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.json.return_value = data
    return response


@pytest.fixture
def sample_survey_response_data() -> dict[str, Any]:
    """Sample survey response payload."""
    return {
        "id": "don:core:survey_response:123",
        "display_id": "SURVR-123",
        "created_date": "2024-01-15T10:00:00Z",
        "object": "don:core:ticket:456",
        "dispatch_id": "dispatch-123",
        "response": {"score": 5, "comment": "Great support"},
        "survey": "don:core:survey:789",
        "unexpected_api_field": "preserved",
    }


class TestSurveyResponsesService:
    """Tests for SurveyResponsesService."""

    def test_list_survey_responses_by_object(
        self,
        sample_survey_response_data: dict[str, Any],
    ) -> None:
        mock_http_client = MagicMock()
        mock_http_client.post.return_value = create_mock_response(
            {"survey_responses": [sample_survey_response_data], "next_cursor": "next"}
        )

        service = SurveyResponsesService(mock_http_client)
        result = service.list(object_id="don:core:ticket:456", limit=10)

        assert isinstance(result, SurveyResponsesListResponse)
        assert result.next_cursor == "next"
        assert len(result.survey_responses) == 1
        response = result.survey_responses[0]
        assert isinstance(response, SurveyResponse)
        assert response.object == "don:core:ticket:456"
        assert response.response == {"score": 5, "comment": "Great support"}
        assert response.model_extra is not None
        assert response.model_extra["unexpected_api_field"] == "preserved"
        mock_http_client.post.assert_called_once()
        (endpoint,) = mock_http_client.post.call_args.args
        _, kwargs = mock_http_client.post.call_args
        assert endpoint == "/surveys.responses.list"
        assert kwargs["data"] == {"limit": 10, "objects": ["don:core:ticket:456"]}

    def test_list_merges_object_filters_without_duplicates(self) -> None:
        mock_http_client = MagicMock()
        mock_http_client.post.return_value = create_mock_response({"survey_responses": []})

        service = SurveyResponsesService(mock_http_client)
        service.list(
            object_id="don:core:ticket:456",
            objects=["don:core:ticket:456", "don:core:ticket:789"],
            mode=SurveyResponsesListMode.AFTER,
        )

        _, kwargs = mock_http_client.post.call_args
        assert kwargs["data"]["objects"] == ["don:core:ticket:456", "don:core:ticket:789"]
        assert kwargs["data"]["mode"] == "after"


class TestAsyncSurveyResponsesService:
    """Tests for AsyncSurveyResponsesService."""

    @pytest.mark.asyncio
    async def test_async_list_survey_responses(
        self,
        sample_survey_response_data: dict[str, Any],
    ) -> None:
        mock_async_client = AsyncMock()
        mock_async_client.post.return_value = create_mock_response(
            {"survey_responses": [sample_survey_response_data]}
        )

        service = AsyncSurveyResponsesService(mock_async_client)
        result = await service.list(object_id="don:core:ticket:456")

        assert len(result.survey_responses) == 1
        assert result.survey_responses[0].id == "don:core:survey_response:123"
        _, kwargs = mock_async_client.post.call_args
        assert kwargs["data"] == {"objects": ["don:core:ticket:456"]}
