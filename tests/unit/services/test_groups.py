"""Unit tests for GroupsService."""

from typing import Any
from unittest.mock import MagicMock

from devrev.models.groups import (
    Group,
    GroupMember,
    GroupMembersAddRequest,
    GroupMembersListRequest,
    GroupMembersRemoveRequest,
    GroupsCreateRequest,
    GroupsGetRequest,
    GroupsListRequest,
    GroupsUpdateRequest,
    GroupType,
)
from devrev.services.groups import GroupsService

from .conftest import create_mock_response


class TestGroupsService:
    """Tests for GroupsService."""

    def test_create_group(
        self,
        mock_http_client: MagicMock,
        sample_group_data: dict[str, Any],
    ) -> None:
        """Test creating a group."""
        mock_http_client.post.return_value = create_mock_response(
            {"group": sample_group_data}
        )

        service = GroupsService(mock_http_client)
        request = GroupsCreateRequest(
            name="Test Group",
            description="Test group description",
            type=GroupType.STATIC,
        )
        result = service.create(request)

        assert isinstance(result, Group)
        assert result.id == "don:core:group:123"
        assert result.name == "Test Group"
        mock_http_client.post.assert_called_once()

    def test_get_group(
        self,
        mock_http_client: MagicMock,
        sample_group_data: dict[str, Any],
    ) -> None:
        """Test getting a group by ID."""
        mock_http_client.post.return_value = create_mock_response(
            {"group": sample_group_data}
        )

        service = GroupsService(mock_http_client)
        request = GroupsGetRequest(id="don:core:group:123")
        result = service.get(request)

        assert isinstance(result, Group)
        assert result.id == "don:core:group:123"
        mock_http_client.post.assert_called_once()

    def test_list_groups(
        self,
        mock_http_client: MagicMock,
        sample_group_data: dict[str, Any],
    ) -> None:
        """Test listing groups."""
        mock_http_client.post.return_value = create_mock_response(
            {"groups": [sample_group_data]}
        )

        service = GroupsService(mock_http_client)
        result = service.list()

        assert len(result) == 1
        assert isinstance(result[0], Group)
        assert result[0].id == "don:core:group:123"
        mock_http_client.post.assert_called_once()

    def test_list_groups_with_request(
        self,
        mock_http_client: MagicMock,
        sample_group_data: dict[str, Any],
    ) -> None:
        """Test listing groups with pagination."""
        mock_http_client.post.return_value = create_mock_response(
            {"groups": [sample_group_data]}
        )

        service = GroupsService(mock_http_client)
        request = GroupsListRequest(limit=50, cursor="next-cursor")
        result = service.list(request)

        assert len(result) == 1
        mock_http_client.post.assert_called_once()

    def test_update_group(
        self,
        mock_http_client: MagicMock,
        sample_group_data: dict[str, Any],
    ) -> None:
        """Test updating a group."""
        updated_data = {**sample_group_data, "name": "Updated Group"}
        mock_http_client.post.return_value = create_mock_response(
            {"group": updated_data}
        )

        service = GroupsService(mock_http_client)
        request = GroupsUpdateRequest(
            id="don:core:group:123",
            name="Updated Group",
        )
        result = service.update(request)

        assert isinstance(result, Group)
        assert result.name == "Updated Group"
        mock_http_client.post.assert_called_once()

    def test_add_member(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test adding a member to a group."""
        mock_http_client.post.return_value = create_mock_response({})

        service = GroupsService(mock_http_client)
        request = GroupMembersAddRequest(
            group="don:core:group:123",
            member="don:identity:user:456",
        )
        result = service.add_member(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_remove_member(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test removing a member from a group."""
        mock_http_client.post.return_value = create_mock_response({})

        service = GroupsService(mock_http_client)
        request = GroupMembersRemoveRequest(
            group="don:core:group:123",
            member="don:identity:user:456",
        )
        result = service.remove_member(request)

        assert result is None
        mock_http_client.post.assert_called_once()

    def test_list_members(
        self,
        mock_http_client: MagicMock,
    ) -> None:
        """Test listing members of a group."""
        member_data = {
            "id": "don:identity:user:456",
            "member": {"id": "don:identity:user:456", "display_name": "Test User"},
        }
        mock_http_client.post.return_value = create_mock_response(
            {"members": [member_data]}
        )

        service = GroupsService(mock_http_client)
        request = GroupMembersListRequest(group="don:core:group:123")
        result = service.list_members(request)

        assert len(result) == 1
        assert isinstance(result[0], GroupMember)
        mock_http_client.post.assert_called_once()

