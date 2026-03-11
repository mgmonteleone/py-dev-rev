"""Unit tests for DevRev MCP Server - Question Answers Tools.

Refs #189
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from devrev.exceptions import DevRevError, NotFoundError
from devrev.models.question_answers import (
    QuestionAnswer,
    QuestionAnswersListResponse,
)
from devrev_mcp.tools.question_answers import (
    devrev_question_answers_create,
    devrev_question_answers_delete,
    devrev_question_answers_get,
    devrev_question_answers_list,
    devrev_question_answers_update,
)


def _make_mock_qa(
    id: str = "don:core:dvrv-us-1:devo/1:qa/1",
    question: str = "How do I reset my password?",
    answer: str = "Click 'Forgot Password' on the login page.",
    status: str = "draft",
) -> MagicMock:
    """Create a mock QuestionAnswer object."""
    mock = MagicMock(spec=QuestionAnswer)
    mock.id = id
    mock.question = question
    mock.answer = answer
    mock.status = status
    mock.display_id = None
    mock.applies_to_parts = None
    mock.owned_by = None
    mock.created_date = None
    mock.modified_date = None
    # model_dump returns dict for serialize_model
    mock.model_dump.return_value = {
        "id": id,
        "question": question,
        "answer": answer,
        "status": status,
    }
    return mock


class TestQuestionAnswersListTool:
    """Tests for devrev_question_answers_list tool."""

    @pytest.mark.asyncio
    async def test_list_success(self, mock_ctx, mock_client):
        """Test listing Q&As with results."""
        mock_response = MagicMock(spec=QuestionAnswersListResponse)
        mock_response.question_answers = [
            _make_mock_qa(),
            _make_mock_qa(id="don:core:dvrv-us-1:devo/1:qa/2", question="What are support hours?"),
        ]
        mock_response.next_cursor = None
        mock_client.question_answers.list.return_value = mock_response

        result = await devrev_question_answers_list(mock_ctx)

        assert result["count"] == 2
        assert len(result["question_answers"]) == 2
        assert result["question_answers"][0]["id"] == "don:core:dvrv-us-1:devo/1:qa/1"
        assert result["question_answers"][1]["id"] == "don:core:dvrv-us-1:devo/1:qa/2"
        mock_client.question_answers.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_empty(self, mock_ctx, mock_client):
        """Test listing Q&As when none exist."""
        mock_response = MagicMock(spec=QuestionAnswersListResponse)
        mock_response.question_answers = []
        mock_response.next_cursor = None
        mock_client.question_answers.list.return_value = mock_response

        result = await devrev_question_answers_list(mock_ctx)

        assert result["count"] == 0
        assert result["question_answers"] == []
        assert "next_cursor" not in result

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, mock_ctx, mock_client):
        """Test listing Q&As returns pagination cursor."""
        mock_response = MagicMock(spec=QuestionAnswersListResponse)
        mock_response.question_answers = [_make_mock_qa()]
        mock_response.next_cursor = "cursor-abc-123"
        mock_client.question_answers.list.return_value = mock_response

        result = await devrev_question_answers_list(mock_ctx, cursor="prev-cursor", limit=10)

        assert result["count"] == 1
        assert result["next_cursor"] == "cursor-abc-123"
        mock_client.question_answers.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_api_error(self, mock_ctx, mock_client):
        """Test listing Q&As with API error."""
        mock_client.question_answers.list.side_effect = DevRevError("API error")

        with pytest.raises(RuntimeError, match="API error"):
            await devrev_question_answers_list(mock_ctx)


class TestQuestionAnswersGetTool:
    """Tests for devrev_question_answers_get tool."""

    @pytest.mark.asyncio
    async def test_get_success(self, mock_ctx, mock_client):
        """Test getting a Q&A successfully."""
        mock_qa = _make_mock_qa(
            id="don:core:dvrv-us-1:devo/1:qa/1",
            question="How do I reset my password?",
            answer="Click 'Forgot Password' on the login page.",
        )
        mock_client.question_answers.get.return_value = mock_qa

        result = await devrev_question_answers_get(mock_ctx, id="don:core:dvrv-us-1:devo/1:qa/1")

        assert result["id"] == "don:core:dvrv-us-1:devo/1:qa/1"
        assert result["question"] == "How do I reset my password?"
        assert result["answer"] == "Click 'Forgot Password' on the login page."
        mock_client.question_answers.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_ctx, mock_client):
        """Test getting a non-existent Q&A."""
        mock_client.question_answers.get.side_effect = NotFoundError("Q&A not found")

        with pytest.raises(RuntimeError, match="Q&A not found"):
            await devrev_question_answers_get(mock_ctx, id="don:core:dvrv-us-1:devo/1:qa/999")


class TestQuestionAnswersCreateTool:
    """Tests for devrev_question_answers_create tool."""

    @pytest.mark.asyncio
    async def test_create_success(self, mock_ctx, mock_client):
        """Test creating a Q&A with all required fields."""
        mock_qa = _make_mock_qa(
            question="How do I reset my password?",
            answer="Click 'Forgot Password' on the login page.",
            status="draft",
        )
        mock_client.question_answers.create.return_value = mock_qa

        result = await devrev_question_answers_create(
            mock_ctx,
            question="How do I reset my password?",
            answer="Click 'Forgot Password' on the login page.",
            applies_to_parts=["don:core:dvrv-us-1:devo/1:product/1"],
            owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
        )

        assert result["question"] == "How do I reset my password?"
        assert result["answer"] == "Click 'Forgot Password' on the login page."
        mock_client.question_answers.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_with_status(self, mock_ctx, mock_client):
        """Test creating a Q&A with explicit status."""
        mock_qa = _make_mock_qa(
            question="What are support hours?",
            answer="We provide 24/7 support.",
            status="published",
        )
        mock_client.question_answers.create.return_value = mock_qa

        result = await devrev_question_answers_create(
            mock_ctx,
            question="What are support hours?",
            answer="We provide 24/7 support.",
            applies_to_parts=["don:core:dvrv-us-1:devo/1:product/1"],
            owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
            status="published",
        )

        assert result["status"] == "published"
        call_args = mock_client.question_answers.create.call_args
        request = call_args[0][0]
        assert request.status == "published"

    @pytest.mark.asyncio
    async def test_create_api_error(self, mock_ctx, mock_client):
        """Test creating a Q&A with API error."""
        mock_client.question_answers.create.side_effect = DevRevError("Creation failed")

        with pytest.raises(RuntimeError, match="Creation failed"):
            await devrev_question_answers_create(
                mock_ctx,
                question="Test question?",
                answer="Test answer.",
                applies_to_parts=["don:core:dvrv-us-1:devo/1:product/1"],
                owned_by=["don:identity:dvrv-us-1:devo/1:devu/1"],
            )


class TestQuestionAnswersUpdateTool:
    """Tests for devrev_question_answers_update tool."""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_ctx, mock_client):
        """Test updating a Q&A question text successfully."""
        mock_qa = _make_mock_qa(
            id="don:core:dvrv-us-1:devo/1:qa/1",
            question="How do I change my password?",
            answer="Click 'Forgot Password' on the login page.",
        )
        mock_client.question_answers.update.return_value = mock_qa

        result = await devrev_question_answers_update(
            mock_ctx,
            id="don:core:dvrv-us-1:devo/1:qa/1",
            question="How do I change my password?",
        )

        assert result["id"] == "don:core:dvrv-us-1:devo/1:qa/1"
        assert result["question"] == "How do I change my password?"
        mock_client.question_answers.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_answer_only(self, mock_ctx, mock_client):
        """Test updating only the answer field of a Q&A."""
        updated_answer = "Visit account settings and click 'Change Password'."
        mock_qa = _make_mock_qa(
            id="don:core:dvrv-us-1:devo/1:qa/1",
            answer=updated_answer,
        )
        mock_client.question_answers.update.return_value = mock_qa

        result = await devrev_question_answers_update(
            mock_ctx,
            id="don:core:dvrv-us-1:devo/1:qa/1",
            answer=updated_answer,
        )

        assert result["answer"] == updated_answer
        call_args = mock_client.question_answers.update.call_args
        request = call_args[0][0]
        assert request.id == "don:core:dvrv-us-1:devo/1:qa/1"
        assert request.answer == updated_answer

    @pytest.mark.asyncio
    async def test_update_api_error(self, mock_ctx, mock_client):
        """Test updating a Q&A with API error."""
        mock_client.question_answers.update.side_effect = DevRevError("Update failed")

        with pytest.raises(RuntimeError, match="Update failed"):
            await devrev_question_answers_update(
                mock_ctx,
                id="don:core:dvrv-us-1:devo/1:qa/1",
                question="Updated question?",
            )


class TestQuestionAnswersDeleteTool:
    """Tests for devrev_question_answers_delete tool."""

    @pytest.mark.asyncio
    async def test_delete_success(self, mock_ctx, mock_client):
        """Test deleting a Q&A successfully."""
        mock_client.question_answers.delete.return_value = None

        result = await devrev_question_answers_delete(mock_ctx, id="don:core:dvrv-us-1:devo/1:qa/1")

        assert result["deleted"] is True
        assert result["id"] == "don:core:dvrv-us-1:devo/1:qa/1"
        mock_client.question_answers.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_api_error(self, mock_ctx, mock_client):
        """Test deleting a Q&A with API error."""
        mock_client.question_answers.delete.side_effect = DevRevError("Delete failed")

        with pytest.raises(RuntimeError, match="Delete failed"):
            await devrev_question_answers_delete(mock_ctx, id="don:core:dvrv-us-1:devo/1:qa/1")
