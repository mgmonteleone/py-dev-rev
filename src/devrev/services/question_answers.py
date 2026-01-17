"""Question Answers service for DevRev SDK.

This module provides the QuestionAnswersService for managing DevRev question answers.
"""

from __future__ import annotations

from devrev.models.question_answers import (
    QuestionAnswer,
    QuestionAnswersCreateRequest,
    QuestionAnswersCreateResponse,
    QuestionAnswersDeleteRequest,
    QuestionAnswersGetRequest,
    QuestionAnswersGetResponse,
    QuestionAnswersListRequest,
    QuestionAnswersListResponse,
    QuestionAnswersUpdateRequest,
    QuestionAnswersUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class QuestionAnswersService(BaseService):
    """Synchronous service for managing DevRev question answers.

    Provides methods for creating, reading, updating, and deleting question answers.
    """

    def create(self, request: QuestionAnswersCreateRequest) -> QuestionAnswer:
        """Create a new question answer.

        Args:
            request: Question answer creation request

        Returns:
            The created QuestionAnswer
        """
        response = self._post("/question-answers.create", request, QuestionAnswersCreateResponse)
        return response.question_answer

    def get(self, request: QuestionAnswersGetRequest) -> QuestionAnswer:
        """Get a question answer by ID.

        Args:
            request: Question answer get request

        Returns:
            The QuestionAnswer
        """
        response = self._post("/question-answers.get", request, QuestionAnswersGetResponse)
        return response.question_answer

    def list(self, request: QuestionAnswersListRequest | None = None) -> QuestionAnswersListResponse:
        """List question answers.

        Args:
            request: Question answer list request

        Returns:
            Paginated list of question answers
        """
        if request is None:
            request = QuestionAnswersListRequest()
        return self._post("/question-answers.list", request, QuestionAnswersListResponse)

    def update(self, request: QuestionAnswersUpdateRequest) -> QuestionAnswer:
        """Update a question answer.

        Args:
            request: Question answer update request

        Returns:
            The updated QuestionAnswer
        """
        response = self._post("/question-answers.update", request, QuestionAnswersUpdateResponse)
        return response.question_answer

    def delete(self, request: QuestionAnswersDeleteRequest) -> None:
        """Delete a question answer.

        Args:
            request: Question answer delete request
        """
        self._post("/question-answers.delete", request, None)


class AsyncQuestionAnswersService(AsyncBaseService):
    """Asynchronous service for managing DevRev question answers.

    Provides async methods for creating, reading, updating, and deleting question answers.
    """

    async def create(self, request: QuestionAnswersCreateRequest) -> QuestionAnswer:
        """Create a new question answer."""
        response = await self._post("/question-answers.create", request, QuestionAnswersCreateResponse)
        return response.question_answer

    async def get(self, request: QuestionAnswersGetRequest) -> QuestionAnswer:
        """Get a question answer by ID."""
        response = await self._post("/question-answers.get", request, QuestionAnswersGetResponse)
        return response.question_answer

    async def list(self, request: QuestionAnswersListRequest | None = None) -> QuestionAnswersListResponse:
        """List question answers."""
        if request is None:
            request = QuestionAnswersListRequest()
        return await self._post("/question-answers.list", request, QuestionAnswersListResponse)

    async def update(self, request: QuestionAnswersUpdateRequest) -> QuestionAnswer:
        """Update a question answer."""
        response = await self._post("/question-answers.update", request, QuestionAnswersUpdateResponse)
        return response.question_answer

    async def delete(self, request: QuestionAnswersDeleteRequest) -> None:
        """Delete a question answer."""
        await self._post("/question-answers.delete", request, None)

