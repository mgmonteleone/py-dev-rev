"""Unit tests for QuestionAnswersService.

Refs #92
"""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.question_answers import (
    QuestionAnswer,
    QuestionAnswersCreateRequest,
    QuestionAnswersDeleteRequest,
    QuestionAnswersGetRequest,
    QuestionAnswersListRequest,
    QuestionAnswersListResponse,
    QuestionAnswersUpdateRequest,
)
from devrev.services.question_answers import QuestionAnswersService

from .conftest import create_mock_response


class TestQuestionAnswersService:
    """Tests for QuestionAnswersService."""

    def test_create_question_answer(
        self,
        mock_http_client: MagicMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test creating a question answer."""
        mock_http_client.post.return_value = create_mock_response(
            {"question_answer": sample_question_answer_data}
        )

        service = QuestionAnswersService(mock_http_client)
        request = QuestionAnswersCreateRequest(
            question="How do I reset my password?",
            answer="Click on the 'Forgot Password' link on the login page.",
        )
        result = service.create(request)

        assert isinstance(result, QuestionAnswer)
        assert result.id == "don:core:question_answer:123"
        assert result.question == "How do I reset my password?"
        assert result.answer == "Click on the 'Forgot Password' link on the login page."
        mock_http_client.post.assert_called_once()

    def test_get_question_answer(
        self,
        mock_http_client: MagicMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test getting a question answer by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"question_answer": sample_question_answer_data}
        )

        service = QuestionAnswersService(mock_http_client)
        request = QuestionAnswersGetRequest(id="don:core:question_answer:123")
        result = service.get(request)

        assert isinstance(result, QuestionAnswer)
        assert result.id == "don:core:question_answer:123"
        mock_http_client.post.assert_called_once()

    def test_list_question_answers(
        self,
        mock_http_client: MagicMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test listing question answers."""
        mock_http_client.post.return_value = create_mock_response(
            {"question_answers": [sample_question_answer_data]}
        )

        service = QuestionAnswersService(mock_http_client)
        result = service.list()

        assert isinstance(result, QuestionAnswersListResponse)
        assert len(result.question_answers) == 1
        assert isinstance(result.question_answers[0], QuestionAnswer)
        assert result.question_answers[0].id == "don:core:question_answer:123"
        mock_http_client.post.assert_called_once()

    def test_list_question_answers_with_request(
        self,
        mock_http_client: MagicMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test listing question answers with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"question_answers": [sample_question_answer_data], "next_cursor": "next-page"}
        )

        service = QuestionAnswersService(mock_http_client)
        request = QuestionAnswersListRequest(limit=50, cursor="current-cursor")
        result = service.list(request)

        assert isinstance(result, QuestionAnswersListResponse)
        assert len(result.question_answers) == 1
        assert result.next_cursor == "next-page"
        mock_http_client.post.assert_called_once()

    def test_update_question_answer(
        self,
        mock_http_client: MagicMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test updating a question answer."""
        updated_data = {**sample_question_answer_data, "answer": "Updated answer text"}
        mock_http_client.post.return_value = create_mock_response({"question_answer": updated_data})

        service = QuestionAnswersService(mock_http_client)
        request = QuestionAnswersUpdateRequest(
            id="don:core:question_answer:123",
            answer="Updated answer text",
        )
        result = service.update(request)

        assert isinstance(result, QuestionAnswer)
        assert result.answer == "Updated answer text"
        mock_http_client.post.assert_called_once()

    def test_delete_question_answer(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test deleting a question answer."""
        mock_http_client.post.return_value = create_mock_response({})

        service = QuestionAnswersService(mock_http_client)
        request = QuestionAnswersDeleteRequest(id="don:core:question_answer:123")
        result = service.delete(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_question_answers_empty(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing question answers returns empty list."""
        mock_http_client.post.return_value = create_mock_response({"question_answers": []})

        service = QuestionAnswersService(mock_http_client)
        result = service.list()

        assert isinstance(result, QuestionAnswersListResponse)
        assert len(result.question_answers) == 0
        mock_http_client.post.assert_called_once()
