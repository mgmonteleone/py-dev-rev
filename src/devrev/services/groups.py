"""Groups service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.groups import (
    Group,
    GroupMember,
    GroupMembersAddRequest,
    GroupMembersAddResponse,
    GroupMembersListRequest,
    GroupMembersListResponse,
    GroupMembersRemoveRequest,
    GroupMembersRemoveResponse,
    GroupsCreateRequest,
    GroupsCreateResponse,
    GroupsGetRequest,
    GroupsGetResponse,
    GroupsListRequest,
    GroupsListResponse,
    GroupsMembersCountRequest,
    GroupsMembersCountResponse,
    GroupsUpdateRequest,
    GroupsUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class GroupsService(BaseService):
    """Service for managing DevRev Groups."""

    def create(self, request: GroupsCreateRequest) -> Group:
        """Create a new group."""
        response = self._post("/groups.create", request, GroupsCreateResponse)
        return response.group

    def get(self, request: GroupsGetRequest) -> Group:
        """Get a group by ID."""
        response = self._post("/groups.get", request, GroupsGetResponse)
        return response.group

    def list(self, request: GroupsListRequest | None = None) -> Sequence[Group]:
        """List groups."""
        if request is None:
            request = GroupsListRequest()
        response = self._post("/groups.list", request, GroupsListResponse)
        return response.groups

    def update(self, request: GroupsUpdateRequest) -> Group:
        """Update a group."""
        response = self._post("/groups.update", request, GroupsUpdateResponse)
        return response.group

    def add_member(self, request: GroupMembersAddRequest) -> None:
        """Add a member to a group."""
        self._post("/group-members.add", request, GroupMembersAddResponse)

    def remove_member(self, request: GroupMembersRemoveRequest) -> None:
        """Remove a member from a group."""
        self._post("/group-members.remove", request, GroupMembersRemoveResponse)

    def list_members(self, request: GroupMembersListRequest) -> Sequence[GroupMember]:
        """List members of a group."""
        response = self._post("/group-members.list", request, GroupMembersListResponse)
        return response.members

    def members_count(
        self,
        id: str,
    ) -> int:
        """Count members in a group (beta only).

        Args:
            id: Group ID

        Returns:
            Count of group members

        Raises:
            BetaAPIRequiredError: If not using beta API
        """
        request = GroupsMembersCountRequest(id=id)
        response = self._post("/groups.members.count", request, GroupsMembersCountResponse)
        return response.count


class AsyncGroupsService(AsyncBaseService):
    """Async service for managing DevRev Groups."""

    async def create(self, request: GroupsCreateRequest) -> Group:
        """Create a new group."""
        response = await self._post("/groups.create", request, GroupsCreateResponse)
        return response.group

    async def get(self, request: GroupsGetRequest) -> Group:
        """Get a group by ID."""
        response = await self._post("/groups.get", request, GroupsGetResponse)
        return response.group

    async def list(self, request: GroupsListRequest | None = None) -> Sequence[Group]:
        """List groups."""
        if request is None:
            request = GroupsListRequest()
        response = await self._post("/groups.list", request, GroupsListResponse)
        return response.groups

    async def update(self, request: GroupsUpdateRequest) -> Group:
        """Update a group."""
        response = await self._post("/groups.update", request, GroupsUpdateResponse)
        return response.group

    async def add_member(self, request: GroupMembersAddRequest) -> None:
        """Add a member to a group."""
        await self._post("/group-members.add", request, GroupMembersAddResponse)

    async def remove_member(self, request: GroupMembersRemoveRequest) -> None:
        """Remove a member from a group."""
        await self._post("/group-members.remove", request, GroupMembersRemoveResponse)

    async def list_members(self, request: GroupMembersListRequest) -> Sequence[GroupMember]:
        """List members of a group."""
        response = await self._post("/group-members.list", request, GroupMembersListResponse)
        return response.members

    async def members_count(
        self,
        id: str,
    ) -> int:
        """Count members in a group (beta only).

        Args:
            id: Group ID

        Returns:
            Count of group members

        Raises:
            BetaAPIRequiredError: If not using beta API
        """
        request = GroupsMembersCountRequest(id=id)
        response = await self._post("/groups.members.count", request, GroupsMembersCountResponse)
        return response.count
