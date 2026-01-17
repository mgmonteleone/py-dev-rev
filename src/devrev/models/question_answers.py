"""Question Answers models for DevRev SDK.

This module contains Pydantic models for Question Answers-related API operations.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class QuestionAnswer(DevRevResponseModel):
    """DevRev QuestionAnswer model.

    Represents a question-answer pair in DevRev.
    """

    id: str = Field(..., description="Question answer ID")
    display_id: str | None = Field(default=None, description="Human-readable display ID")
    question: str = Field(..., description="Question text")
    answer: str | None = Field(default=None, description="Answer text")
    status: str | None = Field(default=None, description="Question answer status")
    created_date: datetime | None = Field(
        default=None, alias="created_at", description="Creation timestamp"
    )
    modified_date: datetime | None = Field(
        default=None, alias="modified_at", description="Last modification timestamp"
    )


class QuestionAnswersCreateRequest(DevRevBaseModel):
    """Request model for creating a question answer."""

    question: str = Field(..., description="Question text")
    answer: str | None = Field(default=None, description="Answer text")


class QuestionAnswersCreateResponse(DevRevResponseModel):
    """Response model for creating a question answer."""

    question_answer: QuestionAnswer = Field(..., description="Created question answer")


class QuestionAnswersGetRequest(DevRevBaseModel):
    """Request model for getting a question answer."""

    id: str = Field(..., description="Question answer ID")


class QuestionAnswersGetResponse(DevRevResponseModel):
    """Response model for getting a question answer."""

    question_answer: QuestionAnswer = Field(..., description="Question answer")


class QuestionAnswersListRequest(DevRevBaseModel):
    """Request model for listing question answers."""

    cursor: str | None = Field(default=None, description="Pagination cursor")
    limit: int | None = Field(default=None, description="Maximum number of results")


class QuestionAnswersListResponse(DevRevResponseModel):
    """Response model for listing question answers."""

    question_answers: list[QuestionAnswer] = Field(..., description="List of question answers")
    next_cursor: str | None = Field(default=None, description="Next pagination cursor")


class QuestionAnswersUpdateRequest(DevRevBaseModel):
    """Request model for updating a question answer."""

    id: str = Field(..., description="Question answer ID")
    question: str | None = Field(default=None, description="Question text")
    answer: str | None = Field(default=None, description="Answer text")


class QuestionAnswersUpdateResponse(DevRevResponseModel):
    """Response model for updating a question answer."""

    question_answer: QuestionAnswer = Field(..., description="Updated question answer")


class QuestionAnswersDeleteRequest(DevRevBaseModel):
    """Request model for deleting a question answer."""

    id: str = Field(..., description="Question answer ID")
