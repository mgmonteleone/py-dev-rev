"""Unit tests for MCP recommendations tools.

Tests for devrev_mcp.tools.recommendations module covering reply and chat operations.
"""

from unittest.mock import MagicMock

import pytest

from devrev_mcp.tools.recommendations import (
    devrev_recommendations_chat,
    devrev_recommendations_reply,
)


class TestRecommendationsReplyTool:
    """Tests for devrev_recommendations_reply tool."""

    async def test_reply_basic(self, mock_ctx, mock_client):
        """Test basic reply recommendation without context."""
        response = MagicMock()
        response.model_dump.return_value = {"reply": "Hello, how can I help?", "confidence": 0.9}
        mock_client.recommendations.get_reply.return_value = response

        result = await devrev_recommendations_reply(mock_ctx, object_id="obj1")

        assert result["reply"] == "Hello, how can I help?"
        assert result["confidence"] == 0.9
        mock_client.recommendations.get_reply.assert_called_once()

    async def test_reply_with_context(self, mock_ctx, mock_client):
        """Test reply recommendation with additional context."""
        response = MagicMock()
        response.model_dump.return_value = {"reply": "Based on context..."}
        mock_client.recommendations.get_reply.return_value = response

        await devrev_recommendations_reply(
            mock_ctx, object_id="obj1", context="user has billing issue"
        )

        call_args = mock_client.recommendations.get_reply.call_args
        request = call_args.args[0]
        from devrev.models.recommendations import GetReplyRequest

        assert isinstance(request, GetReplyRequest)
        assert request.object_id == "obj1"
        assert request.context == "user has billing issue"

    async def test_reply_error(self, mock_ctx, mock_client):
        """Test reply recommendation error handling."""
        from devrev.exceptions import BetaAPIRequiredError

        mock_client.recommendations.get_reply.side_effect = BetaAPIRequiredError("beta only")

        with pytest.raises(RuntimeError, match="Beta API required"):
            await devrev_recommendations_reply(mock_ctx, object_id="obj1")


class TestRecommendationsChatTool:
    """Tests for devrev_recommendations_chat tool."""

    async def test_chat_basic(self, mock_ctx, mock_client):
        """Test basic chat completion with single message."""
        response = MagicMock()
        response.model_dump.return_value = {
            "id": "chat-1",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hi!"}}],
        }
        mock_client.recommendations.chat_completions.return_value = response

        result = await devrev_recommendations_chat(
            mock_ctx,
            messages=[{"role": "user", "content": "Hello"}],
        )

        assert result["id"] == "chat-1"
        assert len(result["choices"]) == 1
        mock_client.recommendations.chat_completions.assert_called_once()

    async def test_chat_with_parameters(self, mock_ctx, mock_client):
        """Test chat completion with max_tokens and temperature."""
        response = MagicMock()
        response.model_dump.return_value = {"id": "chat-2", "choices": []}
        mock_client.recommendations.chat_completions.return_value = response

        await devrev_recommendations_chat(
            mock_ctx,
            messages=[
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hi"},
            ],
            max_tokens=100,
            temperature=0.7,
        )

        call_args = mock_client.recommendations.chat_completions.call_args
        request = call_args.args[0]
        from devrev.models.recommendations import ChatCompletionRequest

        assert isinstance(request, ChatCompletionRequest)
        assert request.max_tokens == 100
        assert request.temperature == 0.7
        assert len(request.messages) == 2

    async def test_chat_error(self, mock_ctx, mock_client):
        """Test chat completion error handling."""
        from devrev.exceptions import AuthenticationError

        mock_client.recommendations.chat_completions.side_effect = AuthenticationError(
            "invalid token"
        )

        with pytest.raises(RuntimeError, match="Authentication failed"):
            await devrev_recommendations_chat(
                mock_ctx, messages=[{"role": "user", "content": "Hi"}]
            )
