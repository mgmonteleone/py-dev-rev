"""Recommendations service for DevRev SDK.

This module provides the RecommendationsService for AI-powered recommendations.
"""

from __future__ import annotations

from devrev.models.recommendations import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    GetReplyRequest,
    GetReplyResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class RecommendationsService(BaseService):
    """Synchronous service for AI-powered recommendations.

    Provides methods for chat completions and reply recommendations.
    """

    def chat_completions(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Get chat completion recommendations.

        Args:
            request: Chat completion request

        Returns:
            Chat completion response with AI-generated messages
        """
        return self._post("/recommendations.chat.completions", request, ChatCompletionResponse)

    def get_reply(self, request: GetReplyRequest) -> GetReplyResponse:
        """Get a recommended reply for an object.

        Args:
            request: Get reply request

        Returns:
            Recommended reply response
        """
        return self._post("/recommendations.get-reply", request, GetReplyResponse)


class AsyncRecommendationsService(AsyncBaseService):
    """Asynchronous service for AI-powered recommendations.

    Provides async methods for chat completions and reply recommendations.
    """

    async def chat_completions(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Get chat completion recommendations."""
        return await self._post("/recommendations.chat.completions", request, ChatCompletionResponse)

    async def get_reply(self, request: GetReplyRequest) -> GetReplyResponse:
        """Get a recommended reply for an object."""
        return await self._post("/recommendations.get-reply", request, GetReplyResponse)

