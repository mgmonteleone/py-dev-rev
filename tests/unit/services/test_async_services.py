"""Unit tests for async service classes."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from devrev.models.articles import Article, ArticlesCreateRequest, ArticleStatus
from devrev.models.conversations import (
    Conversation,
    ConversationsCreateRequest,
    ConversationsGetRequest,
)
from devrev.models.groups import (
    Group,
    GroupMember,
    GroupMembersListRequest,
    GroupsCreateRequest,
    GroupType,
)
from devrev.models.links import Link, LinksCreateRequest, LinkType
from devrev.models.question_answers import (
    QuestionAnswer,
    QuestionAnswersCreateRequest,
    QuestionAnswersDeleteRequest,
    QuestionAnswersGetRequest,
    QuestionAnswersUpdateRequest,
)
from devrev.models.tags import Tag, TagsCreateRequest
from devrev.models.webhooks import Webhook, WebhooksCreateRequest
from devrev.services.articles import AsyncArticlesService
from devrev.services.conversations import AsyncConversationsService
from devrev.services.groups import AsyncGroupsService
from devrev.services.links import AsyncLinksService
from devrev.services.question_answers import AsyncQuestionAnswersService
from devrev.services.tags import AsyncTagsService
from devrev.services.webhooks import AsyncWebhooksService

from .conftest import create_mock_response


@pytest.fixture
def mock_async_http_client() -> AsyncMock:
    """Create a mock async HTTP client."""
    return AsyncMock()


class TestAsyncConversationsService:
    """Tests for AsyncConversationsService."""

    @pytest.mark.asyncio
    async def test_create_conversation(
        self,
        mock_async_http_client: AsyncMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test creating a conversation asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"conversation": sample_conversation_data}
        )

        service = AsyncConversationsService(mock_async_http_client)
        request = ConversationsCreateRequest(type="support", title="Test")
        result = await service.create(request)

        assert isinstance(result, Conversation)
        assert result.id == "don:core:conversation:123"

    @pytest.mark.asyncio
    async def test_get_conversation(
        self,
        mock_async_http_client: AsyncMock,
        sample_conversation_data: dict[str, Any],
    ) -> None:
        """Test getting a conversation asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"conversation": sample_conversation_data}
        )

        service = AsyncConversationsService(mock_async_http_client)
        request = ConversationsGetRequest(id="don:core:conversation:123")
        result = await service.get(request)

        assert isinstance(result, Conversation)


class TestAsyncArticlesService:
    """Tests for AsyncArticlesService."""

    @pytest.mark.asyncio
    async def test_create_article(
        self,
        mock_async_http_client: AsyncMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test creating an article asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"article": sample_article_data}
        )

        service = AsyncArticlesService(mock_async_http_client)
        request = ArticlesCreateRequest(
            title="Test Article",
            content="Content",
            status=ArticleStatus.PUBLISHED,
        )
        result = await service.create(request)

        assert isinstance(result, Article)
        assert result.id == "don:core:article:123"

    @pytest.mark.asyncio
    async def test_list_articles(
        self,
        mock_async_http_client: AsyncMock,
        sample_article_data: dict[str, Any],
    ) -> None:
        """Test listing articles asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"articles": [sample_article_data]}
        )

        service = AsyncArticlesService(mock_async_http_client)
        result = await service.list()

        assert len(result) == 1
        assert isinstance(result[0], Article)


class TestAsyncTagsService:
    """Tests for AsyncTagsService."""

    @pytest.mark.asyncio
    async def test_create_tag(
        self,
        mock_async_http_client: AsyncMock,
        sample_tag_data: dict[str, Any],
    ) -> None:
        """Test creating a tag asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response({"tag": sample_tag_data})

        service = AsyncTagsService(mock_async_http_client)
        request = TagsCreateRequest(name="test-tag")
        result = await service.create(request)

        assert isinstance(result, Tag)
        assert result.id == "don:core:tag:123"


class TestAsyncWebhooksService:
    """Tests for AsyncWebhooksService."""

    @pytest.mark.asyncio
    async def test_create_webhook(
        self,
        mock_async_http_client: AsyncMock,
        sample_webhook_data: dict[str, Any],
    ) -> None:
        """Test creating a webhook asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"webhook": sample_webhook_data}
        )

        service = AsyncWebhooksService(mock_async_http_client)
        request = WebhooksCreateRequest(url="https://example.com/webhook")
        result = await service.create(request)

        assert isinstance(result, Webhook)
        assert result.id == "don:core:webhook:123"


class TestAsyncLinksService:
    """Tests for AsyncLinksService."""

    @pytest.mark.asyncio
    async def test_create_link(
        self,
        mock_async_http_client: AsyncMock,
        sample_link_data: dict[str, Any],
    ) -> None:
        """Test creating a link asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response({"link": sample_link_data})

        service = AsyncLinksService(mock_async_http_client)
        request = LinksCreateRequest(
            link_type=LinkType.IS_BLOCKED_BY,
            source="don:core:issue:456",
            target="don:core:issue:789",
        )
        result = await service.create(request)

        assert isinstance(result, Link)
        assert result.id == "don:core:link:123"

    @pytest.mark.asyncio
    async def test_list_links(
        self,
        mock_async_http_client: AsyncMock,
        sample_link_data: dict[str, Any],
    ) -> None:
        """Test listing links asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"links": [sample_link_data]}
        )

        service = AsyncLinksService(mock_async_http_client)
        result = await service.list()

        assert len(result) == 1
        assert isinstance(result[0], Link)


class TestAsyncGroupsService:
    """Tests for AsyncGroupsService."""

    @pytest.mark.asyncio
    async def test_create_group(
        self,
        mock_async_http_client: AsyncMock,
        sample_group_data: dict[str, Any],
    ) -> None:
        """Test creating a group asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"group": sample_group_data}
        )

        service = AsyncGroupsService(mock_async_http_client)
        request = GroupsCreateRequest(name="Test Group", type=GroupType.STATIC)
        result = await service.create(request)

        assert isinstance(result, Group)
        assert result.id == "don:core:group:123"

    @pytest.mark.asyncio
    async def test_list_members(
        self,
        mock_async_http_client: AsyncMock,
    ) -> None:
        """Test listing group members asynchronously."""
        member_data = {
            "id": "don:identity:user:456",
            "member": {"id": "don:identity:user:456", "display_name": "Test User"},
        }
        mock_async_http_client.post.return_value = create_mock_response({"members": [member_data]})

        service = AsyncGroupsService(mock_async_http_client)
        request = GroupMembersListRequest(group="don:core:group:123")
        result = await service.list_members(request)

        assert len(result) == 1
        assert isinstance(result[0], GroupMember)


class TestAsyncQuestionAnswersService:
    """Tests for AsyncQuestionAnswersService."""

    @pytest.mark.asyncio
    async def test_create_question_answer(
        self,
        mock_async_http_client: AsyncMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test creating a question answer asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"question_answer": sample_question_answer_data}
        )

        service = AsyncQuestionAnswersService(mock_async_http_client)
        request = QuestionAnswersCreateRequest(
            question="How do I reset my password?",
            answer="Click on the 'Forgot Password' link on the login page.",
        )
        result = await service.create(request)

        assert isinstance(result, QuestionAnswer)
        assert result.id == "don:core:question_answer:123"
        assert result.question == "How do I reset my password?"

    @pytest.mark.asyncio
    async def test_get_question_answer(
        self,
        mock_async_http_client: AsyncMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test getting a question answer asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"question_answer": sample_question_answer_data}
        )

        service = AsyncQuestionAnswersService(mock_async_http_client)
        request = QuestionAnswersGetRequest(id="don:core:question_answer:123")
        result = await service.get(request)

        assert isinstance(result, QuestionAnswer)
        assert result.id == "don:core:question_answer:123"

    @pytest.mark.asyncio
    async def test_list_question_answers(
        self,
        mock_async_http_client: AsyncMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test listing question answers asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response(
            {"question_answers": [sample_question_answer_data]}
        )

        service = AsyncQuestionAnswersService(mock_async_http_client)
        result = await service.list()

        assert len(result.question_answers) == 1
        assert isinstance(result.question_answers[0], QuestionAnswer)

    @pytest.mark.asyncio
    async def test_update_question_answer(
        self,
        mock_async_http_client: AsyncMock,
        sample_question_answer_data: dict[str, Any],
    ) -> None:
        """Test updating a question answer asynchronously."""
        updated_data = {**sample_question_answer_data, "answer": "Updated answer"}
        mock_async_http_client.post.return_value = create_mock_response(
            {"question_answer": updated_data}
        )

        service = AsyncQuestionAnswersService(mock_async_http_client)
        request = QuestionAnswersUpdateRequest(
            id="don:core:question_answer:123",
            answer="Updated answer",
        )
        result = await service.update(request)

        assert isinstance(result, QuestionAnswer)
        assert result.answer == "Updated answer"

    @pytest.mark.asyncio
    async def test_delete_question_answer(
        self,
        mock_async_http_client: AsyncMock,
    ) -> None:
        """Test deleting a question answer asynchronously."""
        mock_async_http_client.post.return_value = create_mock_response({})

        service = AsyncQuestionAnswersService(mock_async_http_client)
        request = QuestionAnswersDeleteRequest(id="don:core:question_answer:123")
        result = await service.delete(request)

        assert result is None
