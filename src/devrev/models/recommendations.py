"""Recommendations models for DevRev SDK.

This module contains Pydantic models for Recommendations-related API operations.
"""

from __future__ import annotations

from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class MessageRole(str, Enum):
    """Message role enumeration."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(DevRevResponseModel):
    """Chat message model.

    Inherits from DevRevResponseModel to allow extra fields from API responses.
    """

    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class TokenUsage(DevRevResponseModel):
    """Token usage statistics.

    Inherits from DevRevResponseModel to allow extra fields from API responses.
    """

    prompt_tokens: int | None = Field(default=None, description="Number of prompt tokens")
    completion_tokens: int | None = Field(default=None, description="Number of completion tokens")
    total_tokens: int | None = Field(default=None, description="Total number of tokens")


class ChatChoice(DevRevResponseModel):
    """Chat completion choice.

    Inherits from DevRevResponseModel to allow extra fields from API responses.
    """

    index: int = Field(..., description="Choice index")
    message: ChatMessage = Field(..., description="Message content")
    finish_reason: str | None = Field(default=None, description="Reason for completion finish")


class ChatCompletionRequest(DevRevBaseModel):
    """Request model for chat completion."""

    messages: list[ChatMessage] = Field(..., description="List of chat messages")
    max_tokens: int | None = Field(default=None, description="Maximum tokens to generate")
    temperature: float | None = Field(default=None, description="Sampling temperature")


class ChatCompletionResponse(DevRevResponseModel):
    """Response model for chat completion."""

    id: str = Field(..., description="Completion ID")
    choices: list[ChatChoice] = Field(..., description="List of completion choices")
    usage: TokenUsage | None = Field(default=None, description="Token usage statistics")


class GetReplyRequest(DevRevBaseModel):
    """Request model for getting a reply recommendation."""

    object_id: str = Field(..., description="Object ID to get reply for")
    context: str | None = Field(default=None, description="Additional context")


class GetReplyResponse(DevRevResponseModel):
    """Response model for getting a reply recommendation."""

    reply: str = Field(..., description="Recommended reply text")
    confidence: float | None = Field(default=None, description="Confidence score")
