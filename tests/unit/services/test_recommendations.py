"""Unit tests for RecommendationsService.

Refs #92
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.models.recommendations import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    GetReplyRequest,
    GetReplyResponse,
    MessageRole,
)
from devrev.services.recommendations import (
    AsyncRecommendationsService,
    RecommendationsService,
)

from .conftest import create_mock_response


class TestRecommendationsService:
    """Tests for RecommendationsService."""

    def test_chat_completions(
        self,
        mock_http_client: MagicMock,
        sample_chat_completion_data: dict[str, Any],
    ) -> None:
        """Test chat completions."""
        mock_http_client.post.return_value = create_mock_response(sample_chat_completion_data)

        service = RecommendationsService(mock_http_client)
        request = ChatCompletionRequest(
            messages=[ChatMessage(role=MessageRole.USER, content="Hello, how can I help you?")],
            max_tokens=100,
            temperature=0.7,
        )
        result = service.chat_completions(request)

        assert isinstance(result, ChatCompletionResponse)
        assert result.id == "chatcmpl-123"
        assert len(result.choices) == 1
        assert result.choices[0].message.role == MessageRole.ASSISTANT
        assert result.choices[0].message.content == "I can help you with your DevRev questions!"
        assert result.choices[0].finish_reason == "stop"
        assert result.usage is not None
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 20
        assert result.usage.total_tokens == 30
        mock_http_client.post.assert_called_once_with(
            "/recommendations.chat.completions",
            data={
                "messages": [{"role": "user", "content": "Hello, how can I help you?"}],
                "max_tokens": 100,
                "temperature": 0.7,
            },
        )

    def test_chat_completions_minimal(
        self,
        mock_http_client: MagicMock,
        sample_chat_completion_data: dict[str, Any],
    ) -> None:
        """Test chat completions with minimal parameters."""
        mock_http_client.post.return_value = create_mock_response(sample_chat_completion_data)

        service = RecommendationsService(mock_http_client)
        request = ChatCompletionRequest(
            messages=[
                ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
                ChatMessage(role=MessageRole.USER, content="What is DevRev?"),
            ]
        )
        result = service.chat_completions(request)

        assert isinstance(result, ChatCompletionResponse)
        assert result.id == "chatcmpl-123"
        mock_http_client.post.assert_called_once_with(
            "/recommendations.chat.completions",
            data={
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is DevRev?"},
                ]
            },
        )

    def test_chat_completions_multiple_choices(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test chat completions with multiple choices."""
        response_data = {
            "id": "chatcmpl-456",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "First response"},
                    "finish_reason": "stop",
                },
                {
                    "index": 1,
                    "message": {"role": "assistant", "content": "Second response"},
                    "finish_reason": "stop",
                },
            ],
        }
        mock_http_client.post.return_value = create_mock_response(response_data)

        service = RecommendationsService(mock_http_client)
        request = ChatCompletionRequest(
            messages=[ChatMessage(role=MessageRole.USER, content="Test")]
        )
        result = service.chat_completions(request)

        assert isinstance(result, ChatCompletionResponse)
        assert len(result.choices) == 2
        assert result.choices[0].message.content == "First response"
        assert result.choices[1].message.content == "Second response"

    def test_get_reply(
        self,
        mock_http_client: MagicMock,
        sample_get_reply_data: dict[str, Any],
    ) -> None:
        """Test getting a recommended reply."""
        mock_http_client.post.return_value = create_mock_response(sample_get_reply_data)

        service = RecommendationsService(mock_http_client)
        request = GetReplyRequest(
            object_id="don:core:conversation:123",
            context="Customer is asking about billing",
        )
        result = service.get_reply(request)

        assert isinstance(result, GetReplyResponse)
        assert result.reply == "Thank you for contacting us. We'll look into this issue."
        assert result.confidence == 0.95
        mock_http_client.post.assert_called_once_with(
            "/recommendations.get-reply",
            data={
                "object_id": "don:core:conversation:123",
                "context": "Customer is asking about billing",
            },
        )

    def test_get_reply_minimal(
        self,
        mock_http_client: MagicMock,
        sample_get_reply_data: dict[str, Any],
    ) -> None:
        """Test getting a recommended reply with minimal parameters."""
        mock_http_client.post.return_value = create_mock_response(sample_get_reply_data)

        service = RecommendationsService(mock_http_client)
        request = GetReplyRequest(object_id="don:core:issue:456")
        result = service.get_reply(request)

        assert isinstance(result, GetReplyResponse)
        assert result.reply == "Thank you for contacting us. We'll look into this issue."
        mock_http_client.post.assert_called_once_with(
            "/recommendations.get-reply",
            data={"object_id": "don:core:issue:456"},
        )

    def test_get_reply_without_confidence(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test getting a recommended reply without confidence score."""
        response_data = {
            "reply": "We appreciate your feedback.",
        }
        mock_http_client.post.return_value = create_mock_response(response_data)

        service = RecommendationsService(mock_http_client)
        request = GetReplyRequest(object_id="don:core:ticket:789")
        result = service.get_reply(request)

        assert isinstance(result, GetReplyResponse)
        assert result.reply == "We appreciate your feedback."
        assert result.confidence is None

    def test_chat_completions_without_usage(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test chat completions without usage statistics."""
        response_data = {
            "id": "chatcmpl-789",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Response without usage"},
                    "finish_reason": "length",
                }
            ],
        }
        mock_http_client.post.return_value = create_mock_response(response_data)

        service = RecommendationsService(mock_http_client)
        request = ChatCompletionRequest(
            messages=[ChatMessage(role=MessageRole.USER, content="Test")]
        )
        result = service.chat_completions(request)

        assert isinstance(result, ChatCompletionResponse)
        assert result.usage is None
        assert result.choices[0].finish_reason == "length"

    def test_chat_completions_conversation_history(
        self,
        mock_http_client: MagicMock,
        sample_chat_completion_data: dict[str, Any],
    ) -> None:
        """Test chat completions with conversation history."""
        mock_http_client.post.return_value = create_mock_response(sample_chat_completion_data)

        service = RecommendationsService(mock_http_client)
        request = ChatCompletionRequest(
            messages=[
                ChatMessage(role=MessageRole.SYSTEM, content="You are a DevRev expert."),
                ChatMessage(role=MessageRole.USER, content="What is a work item?"),
                ChatMessage(
                    role=MessageRole.ASSISTANT,
                    content="A work item is a unit of work in DevRev.",
                ),
                ChatMessage(role=MessageRole.USER, content="Can you give me an example?"),
            ],
            max_tokens=150,
        )
        result = service.chat_completions(request)

        assert isinstance(result, ChatCompletionResponse)
        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert len(call_args[1]["data"]["messages"]) == 4


class TestAsyncRecommendationsService:
    """Tests for AsyncRecommendationsService."""

    @pytest.mark.asyncio
    async def test_chat_completions(
        self,
        mock_async_http_client: AsyncMock,
        sample_chat_completion_data: dict[str, Any],
    ) -> None:
        """Test async chat completions."""
        mock_async_http_client.post.return_value = create_mock_response(sample_chat_completion_data)

        service = AsyncRecommendationsService(mock_async_http_client)
        request = ChatCompletionRequest(
            messages=[ChatMessage(role=MessageRole.USER, content="Hello, how can I help you?")],
            max_tokens=100,
            temperature=0.7,
        )
        result = await service.chat_completions(request)

        assert isinstance(result, ChatCompletionResponse)
        assert result.id == "chatcmpl-123"
        assert len(result.choices) == 1
        assert result.choices[0].message.role == MessageRole.ASSISTANT
        assert result.choices[0].message.content == "I can help you with your DevRev questions!"
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_completions_minimal(
        self,
        mock_async_http_client: AsyncMock,
        sample_chat_completion_data: dict[str, Any],
    ) -> None:
        """Test async chat completions with minimal parameters."""
        mock_async_http_client.post.return_value = create_mock_response(sample_chat_completion_data)

        service = AsyncRecommendationsService(mock_async_http_client)
        request = ChatCompletionRequest(
            messages=[
                ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
                ChatMessage(role=MessageRole.USER, content="What is DevRev?"),
            ]
        )
        result = await service.chat_completions(request)

        assert isinstance(result, ChatCompletionResponse)
        assert result.id == "chatcmpl-123"
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reply(
        self,
        mock_async_http_client: AsyncMock,
        sample_get_reply_data: dict[str, Any],
    ) -> None:
        """Test async getting a recommended reply."""
        mock_async_http_client.post.return_value = create_mock_response(sample_get_reply_data)

        service = AsyncRecommendationsService(mock_async_http_client)
        request = GetReplyRequest(
            object_id="don:core:conversation:123",
            context="Customer is asking about billing",
        )
        result = await service.get_reply(request)

        assert isinstance(result, GetReplyResponse)
        assert result.reply == "Thank you for contacting us. We'll look into this issue."
        assert result.confidence == 0.95
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_reply_minimal(
        self,
        mock_async_http_client: AsyncMock,
        sample_get_reply_data: dict[str, Any],
    ) -> None:
        """Test async getting a recommended reply with minimal parameters."""
        mock_async_http_client.post.return_value = create_mock_response(sample_get_reply_data)

        service = AsyncRecommendationsService(mock_async_http_client)
        request = GetReplyRequest(object_id="don:core:issue:456")
        result = await service.get_reply(request)

        assert isinstance(result, GetReplyResponse)
        assert result.reply == "Thank you for contacting us. We'll look into this issue."
        mock_async_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_completions_multiple_choices(
        self,
        mock_async_http_client: AsyncMock,
    ) -> None:
        """Test async chat completions with multiple choices."""
        response_data = {
            "id": "chatcmpl-456",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "First response"},
                    "finish_reason": "stop",
                },
                {
                    "index": 1,
                    "message": {"role": "assistant", "content": "Second response"},
                    "finish_reason": "stop",
                },
            ],
        }
        mock_async_http_client.post.return_value = create_mock_response(response_data)

        service = AsyncRecommendationsService(mock_async_http_client)
        request = ChatCompletionRequest(
            messages=[ChatMessage(role=MessageRole.USER, content="Test")]
        )
        result = await service.chat_completions(request)

        assert isinstance(result, ChatCompletionResponse)
        assert len(result.choices) == 2
        assert result.choices[0].message.content == "First response"
        assert result.choices[1].message.content == "Second response"

    @pytest.mark.asyncio
    async def test_get_reply_without_confidence(
        self,
        mock_async_http_client: AsyncMock,
    ) -> None:
        """Test async getting a recommended reply without confidence score."""
        response_data = {
            "reply": "We appreciate your feedback.",
        }
        mock_async_http_client.post.return_value = create_mock_response(response_data)

        service = AsyncRecommendationsService(mock_async_http_client)
        request = GetReplyRequest(object_id="don:core:ticket:789")
        result = await service.get_reply(request)

        assert isinstance(result, GetReplyResponse)
        assert result.reply == "We appreciate your feedback."
        assert result.confidence is None
