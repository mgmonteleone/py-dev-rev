"""Unit tests for DevRev MCP Server - Groups Tools."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from devrev.exceptions import DevRevError, NotFoundError, ValidationError
from devrev_mcp.tools.groups import (
    devrev_groups_add_member,
    devrev_groups_create,
    devrev_groups_get,
    devrev_groups_list,
    devrev_groups_list_members,
    devrev_groups_members_count,
    devrev_groups_remove_member,
    devrev_groups_update,
)


def _make_mock_group(
    id: str = "grp_123",
    name: str = "Test Group",
    description: str | None = "Test description",
    type: str = "STATIC",
) -> MagicMock:
    """Create a mock Group object."""
    group = MagicMock()
    group.id = id
    group.name = name
    group.description = description
    group.type = type
    group.created_date = datetime(2024, 1, 1, 12, 0, 0)
    group.modified_date = datetime(2024, 1, 2, 12, 0, 0)
    group.model_dump.return_value = {
        "id": id,
        "name": name,
        "description": description,
        "type": type,
        "created_date": "2024-01-01T12:00:00",
        "modified_date": "2024-01-02T12:00:00",
    }
    return group


def _make_mock_group_member(
    member_id: str = "usr_123",
    member_name: str = "Test User",
) -> MagicMock:
    """Create a mock GroupMember object."""
    member_summary = MagicMock()
    member_summary.id = member_id
    member_summary.display_name = member_name
    member_summary.model_dump.return_value = {
        "id": member_id,
        "display_name": member_name,
    }

    group_member = MagicMock()
    group_member.member = member_summary
    group_member.member_rev_org = "rev_org_123"
    group_member.model_dump.return_value = {
        "member": member_summary.model_dump.return_value,
        "member_rev_org": "rev_org_123",
    }
    return group_member


@pytest.fixture
def mock_context():
    """Create a mock MCP context."""
    from devrev import APIVersion
    from devrev_mcp.config import MCPServerConfig
    from devrev_mcp.server import AppContext

    # Create a mock client
    mock_client = AsyncMock()
    mock_client.groups = AsyncMock()

    # Create AppContext with new signature
    config = MCPServerConfig()
    app_context = AppContext(
        config=config,
        _api_version=APIVersion.PUBLIC,
        _stdio_client=mock_client,
    )

    # Create mock MCP context
    ctx = MagicMock()
    ctx.request_context.lifespan_context = app_context
    return ctx


class TestGroupsListTool:
    """Tests for devrev_groups_list tool."""

    @pytest.mark.asyncio
    async def test_list_empty(self, mock_context):
        """Test listing groups when none exist."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.list.return_value = []

        result = await devrev_groups_list(mock_context)

        assert result == {"count": 0, "groups": []}
        mock_client.groups.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_with_results(self, mock_context):
        """Test listing groups with results."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        group1 = _make_mock_group(id="grp_1", name="Group 1")
        group2 = _make_mock_group(id="grp_2", name="Group 2")
        mock_client.groups.list.return_value = [group1, group2]

        result = await devrev_groups_list(mock_context)

        assert result["count"] == 2
        assert len(result["groups"]) == 2
        assert result["groups"][0]["id"] == "grp_1"
        assert result["groups"][1]["id"] == "grp_2"

    @pytest.mark.asyncio
    async def test_list_error(self, mock_context):
        """Test listing groups with API error."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.list.side_effect = DevRevError("API error")

        with pytest.raises(RuntimeError, match="API error"):
            await devrev_groups_list(mock_context)


class TestGroupsGetTool:
    """Tests for devrev_groups_get tool."""

    @pytest.mark.asyncio
    async def test_get_success(self, mock_context):
        """Test getting a group successfully."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        group = _make_mock_group(id="grp_123", name="Test Group")
        mock_client.groups.get.return_value = group

        result = await devrev_groups_get(mock_context, id="grp_123")

        assert result["id"] == "grp_123"
        assert result["name"] == "Test Group"
        mock_client.groups.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_not_found(self, mock_context):
        """Test getting a non-existent group."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.get.side_effect = NotFoundError("Group not found")

        with pytest.raises(RuntimeError, match="Group not found"):
            await devrev_groups_get(mock_context, id="grp_999")


class TestGroupsCreateTool:
    """Tests for devrev_groups_create tool."""

    @pytest.mark.asyncio
    async def test_create_minimal(self, mock_context):
        """Test creating a group with minimal parameters."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        group = _make_mock_group(id="grp_new", name="New Group")
        mock_client.groups.create.return_value = group

        result = await devrev_groups_create(mock_context, name="New Group")

        assert result["id"] == "grp_new"
        assert result["name"] == "New Group"
        mock_client.groups.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_with_type(self, mock_context):
        """Test creating a group with type specified."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        group = _make_mock_group(id="grp_new", name="New Group", type="DYNAMIC")
        mock_client.groups.create.return_value = group

        result = await devrev_groups_create(
            mock_context, name="New Group", description="Test", type="dynamic"
        )

        assert result["id"] == "grp_new"
        assert result["type"] == "DYNAMIC"
        mock_client.groups.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_error(self, mock_context):
        """Test creating a group with validation error."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.create.side_effect = ValidationError("Invalid name")

        with pytest.raises(RuntimeError, match="Invalid name"):
            await devrev_groups_create(mock_context, name="")


class TestGroupsUpdateTool:
    """Tests for devrev_groups_update tool."""

    @pytest.mark.asyncio
    async def test_update_success(self, mock_context):
        """Test updating a group successfully."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        group = _make_mock_group(id="grp_123", name="Updated Group")
        mock_client.groups.update.return_value = group

        result = await devrev_groups_update(mock_context, id="grp_123", name="Updated Group")

        assert result["id"] == "grp_123"
        assert result["name"] == "Updated Group"
        mock_client.groups.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_error(self, mock_context):
        """Test updating a group with error."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.update.side_effect = NotFoundError("Group not found")

        with pytest.raises(RuntimeError, match="Group not found"):
            await devrev_groups_update(mock_context, id="grp_999", name="New Name")


class TestGroupsAddMemberTool:
    """Tests for devrev_groups_add_member tool."""

    @pytest.mark.asyncio
    async def test_add_member_success(self, mock_context):
        """Test adding a member to a group successfully."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.add_member.return_value = None

        result = await devrev_groups_add_member(mock_context, group="grp_123", member="usr_456")

        assert result == {"added": True, "group": "grp_123", "member": "usr_456"}
        mock_client.groups.add_member.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_member_error(self, mock_context):
        """Test adding a member with error."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.add_member.side_effect = ValidationError("Invalid member")

        with pytest.raises(RuntimeError, match="Invalid member"):
            await devrev_groups_add_member(mock_context, group="grp_123", member="invalid")


class TestGroupsRemoveMemberTool:
    """Tests for devrev_groups_remove_member tool."""

    @pytest.mark.asyncio
    async def test_remove_member_success(self, mock_context):
        """Test removing a member from a group successfully."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.remove_member.return_value = None

        result = await devrev_groups_remove_member(mock_context, group="grp_123", member="usr_456")

        assert result == {"removed": True, "group": "grp_123", "member": "usr_456"}
        mock_client.groups.remove_member.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_member_error(self, mock_context):
        """Test removing a member with error."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.remove_member.side_effect = NotFoundError("Member not found")

        with pytest.raises(RuntimeError, match="Member not found"):
            await devrev_groups_remove_member(mock_context, group="grp_123", member="usr_999")


class TestGroupsListMembersTool:
    """Tests for devrev_groups_list_members tool."""

    @pytest.mark.asyncio
    async def test_list_members_success(self, mock_context):
        """Test listing group members successfully."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        member1 = _make_mock_group_member(member_id="usr_1", member_name="User 1")
        member2 = _make_mock_group_member(member_id="usr_2", member_name="User 2")
        mock_client.groups.list_members.return_value = [member1, member2]

        result = await devrev_groups_list_members(mock_context, group="grp_123")

        assert result["count"] == 2
        assert len(result["members"]) == 2
        assert result["members"][0]["member"]["id"] == "usr_1"
        assert result["members"][1]["member"]["id"] == "usr_2"
        mock_client.groups.list_members.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_members_empty(self, mock_context):
        """Test listing members when group is empty."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.list_members.return_value = []

        result = await devrev_groups_list_members(mock_context, group="grp_123")

        assert result == {"count": 0, "members": []}
        mock_client.groups.list_members.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_members_error(self, mock_context):
        """Test listing members with error."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.list_members.side_effect = NotFoundError("Group not found")

        with pytest.raises(RuntimeError, match="Group not found"):
            await devrev_groups_list_members(mock_context, group="grp_999")


class TestGroupsMembersCountTool:
    """Tests for devrev_groups_members_count tool."""

    @pytest.mark.asyncio
    async def test_members_count_success(self, mock_context):
        """Test getting member count successfully."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.members_count.return_value = 5

        result = await devrev_groups_members_count(mock_context, group_id="grp_123")

        assert result == {"count": 5}
        mock_client.groups.members_count.assert_called_once_with(group_id="grp_123")

    @pytest.mark.asyncio
    async def test_members_count_error(self, mock_context):
        """Test getting member count with error."""
        mock_client = mock_context.request_context.lifespan_context.get_client()
        mock_client.groups.members_count.side_effect = NotFoundError("Group not found")

        with pytest.raises(RuntimeError, match="Group not found"):
            await devrev_groups_members_count(mock_context, group_id="grp_999")
