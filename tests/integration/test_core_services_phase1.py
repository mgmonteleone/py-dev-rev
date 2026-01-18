"""Integration tests for Phase 1: Core Services completion.

This test suite adds coverage for:
- group-members.list
- group-members.count
- timeline-entries.list
- timeline-entries.get
- links.list
- links.get

Related to Issue #103: Achieve 100% Integration Test Coverage
"""

import logging
import os

import pytest

from devrev import DevRevClient
from devrev.models.groups import GroupMembersListRequest
from devrev.models.timeline_entries import TimelineEntriesListRequest, TimelineEntriesGetRequest
from devrev.models.links import LinksListRequest, LinksGetRequest

# Skip all integration tests if DEVREV_API_TOKEN is not set
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("DEVREV_API_TOKEN"),
        reason="DEVREV_API_TOKEN environment variable not set",
    ),
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def client() -> DevRevClient:
    """Create a DevRev client for integration tests."""
    return DevRevClient()


class TestGroupMembersEndpoints:
    """Tests for group-members endpoints."""

    def test_group_members_list(self, client: DevRevClient) -> None:
        """Test group-members.list endpoint."""
        # Get a valid group ID from list
        groups_result = client.groups.list()
        if not groups_result or len(groups_result) == 0:
            pytest.skip("No groups available for testing")
        
        group_id = groups_result[0].id
        
        # Test list members
        request = GroupMembersListRequest(group=group_id)
        result = client.groups.list_members(request)
        assert isinstance(result, list)
        logger.info(f"✅ group-members.list: {len(result)} members in group {group_id}")

    def test_group_members_count(self, client: DevRevClient) -> None:
        """Test group-members.count endpoint."""
        # Get a valid group ID from list
        groups_result = client.groups.list()
        if not groups_result or len(groups_result) == 0:
            pytest.skip("No groups available for testing")
        
        group_id = groups_result[0].id
        
        # Test count members
        result = client.groups.members_count(group_id)
        assert isinstance(result, int)
        assert result >= 0
        logger.info(f"✅ group-members.count: {result} members in group {group_id}")


class TestTimelineEntriesEndpoints:
    """Tests for timeline-entries endpoints."""

    def test_timeline_entries_list(self, client: DevRevClient) -> None:
        """Test timeline-entries.list endpoint."""
        # Get a valid object ID (use a work item)
        works_result = client.works.list(limit=1)
        if not works_result.works:
            pytest.skip("No works available for testing timeline entries")
        
        object_id = works_result.works[0].id
        
        # Test list timeline entries
        request = TimelineEntriesListRequest(object=object_id)
        result = client.timeline_entries.list(request)
        assert isinstance(result, list)
        logger.info(f"✅ timeline-entries.list: {len(result)} entries for {object_id}")

    def test_timeline_entries_get(self, client: DevRevClient) -> None:
        """Test timeline-entries.get endpoint."""
        # Get a valid object ID (use a work item)
        works_result = client.works.list(limit=1)
        if not works_result.works:
            pytest.skip("No works available for testing timeline entries")
        
        object_id = works_result.works[0].id
        
        # Get timeline entries to find a valid entry ID
        list_request = TimelineEntriesListRequest(object=object_id)
        list_result = client.timeline_entries.list(list_request)
        
        if not list_result or len(list_result) == 0:
            pytest.skip("No timeline entries available for testing")
        
        entry_id = list_result[0].id
        
        # Test get timeline entry
        request = TimelineEntriesGetRequest(id=entry_id)
        result = client.timeline_entries.get(request)
        assert result.id == entry_id
        logger.info(f"✅ timeline-entries.get: {result.id}")


class TestLinksEndpoints:
    """Tests for links endpoints."""

    def test_links_list(self, client: DevRevClient) -> None:
        """Test links.list endpoint."""
        # Test list links
        result = client.links.list()
        assert isinstance(result, list)
        logger.info(f"✅ links.list: {len(result)} links")

    def test_links_get(self, client: DevRevClient) -> None:
        """Test links.get endpoint."""
        # Get a valid link ID from list
        list_result = client.links.list()
        if not list_result or len(list_result) == 0:
            pytest.skip("No links available for testing")
        
        link_id = list_result[0].id
        
        # Test get link
        request = LinksGetRequest(id=link_id)
        result = client.links.get(request)
        assert result.id == link_id
        logger.info(f"✅ links.get: {result.id}")

