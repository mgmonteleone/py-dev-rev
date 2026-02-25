"""Regression tests for DevUserState and RevUserState enum values.

This module contains parametrized tests to verify that all API-returned user state
values are accepted by the Pydantic models without validation errors. These tests
prevent enum drift between the SDK and the DevRev API.

Created in response to code review feedback on PR #136 (issue #137).
Both DevUserState and RevUserState enums have 6 values: active, deactivated,
deleted, locked, shadow, unassigned.

References:
    - Issue: #137
    - Parent PR: #136
"""

from __future__ import annotations

import pytest

from devrev.models.dev_users import DevUser, DevUsersListResponse, DevUserState
from devrev.models.rev_users import RevUser, RevUsersListResponse, RevUserState


class TestDevUserStateRegression:
    """Regression tests for DevUserState enum values."""

    @pytest.mark.parametrize(
        "state_value",
        ["active", "deactivated", "deleted", "locked", "shadow", "unassigned"],
    )
    def test_dev_user_accepts_all_state_values(self, state_value: str) -> None:
        """Test that DevUser model accepts all valid state values.

        Args:
            state_value: User state string value from the API.

        This test ensures that the DevUser Pydantic model can parse all state
        values that the DevRev API may return, preventing validation errors
        when new states are added or when rarely-used states are encountered.
        """
        user_data = {"id": "don:identity:dvrv-us-1:devo/1:devu/123", "state": state_value}
        user = DevUser.model_validate(user_data)

        assert user.state == DevUserState(state_value)
        assert user.id == "don:identity:dvrv-us-1:devo/1:devu/123"

    @pytest.mark.parametrize(
        "state_value",
        ["active", "deactivated", "deleted", "locked", "shadow", "unassigned"],
    )
    def test_dev_users_list_response_accepts_all_states(self, state_value: str) -> None:
        """Test that DevUsersListResponse can parse users with all state values.

        Args:
            state_value: User state string value from the API.

        This test verifies that the list response model correctly handles users
        with any valid state value, ensuring pagination and list operations work
        regardless of user state.
        """
        response_data = {
            "dev_users": [
                {"id": "don:identity:dvrv-us-1:devo/1:devu/1", "state": state_value},
                {"id": "don:identity:dvrv-us-1:devo/1:devu/2", "state": "active"},
            ],
            "next_cursor": None,
        }
        response = DevUsersListResponse.model_validate(response_data)

        assert len(response.dev_users) == 2
        assert response.dev_users[0].state == DevUserState(state_value)
        assert response.dev_users[1].state == DevUserState.ACTIVE

    def test_dev_users_list_response_with_mixed_states(self) -> None:
        """Test DevUsersListResponse with users in various states.

        This test verifies that a single response can contain users with
        different states, which is the typical real-world scenario.
        """
        response_data = {
            "dev_users": [
                {"id": "don:identity:dvrv-us-1:devo/1:devu/1", "state": "active"},
                {"id": "don:identity:dvrv-us-1:devo/1:devu/2", "state": "deactivated"},
                {"id": "don:identity:dvrv-us-1:devo/1:devu/3", "state": "locked"},
                {"id": "don:identity:dvrv-us-1:devo/1:devu/4", "state": "shadow"},
                {"id": "don:identity:dvrv-us-1:devo/1:devu/5", "state": "deleted"},
                {"id": "don:identity:dvrv-us-1:devo/1:devu/6", "state": "unassigned"},
            ],
            "next_cursor": "cursor_abc123",
        }
        response = DevUsersListResponse.model_validate(response_data)

        assert len(response.dev_users) == 6
        assert response.dev_users[0].state == DevUserState.ACTIVE
        assert response.dev_users[1].state == DevUserState.DEACTIVATED
        assert response.dev_users[2].state == DevUserState.LOCKED
        assert response.dev_users[3].state == DevUserState.SHADOW
        assert response.dev_users[4].state == DevUserState.DELETED
        assert response.dev_users[5].state == DevUserState.UNASSIGNED
        assert response.next_cursor == "cursor_abc123"


class TestRevUserStateRegression:
    """Regression tests for RevUserState enum values."""

    @pytest.mark.parametrize(
        "state_value",
        ["active", "deactivated", "deleted", "locked", "shadow", "unassigned"],
    )
    def test_rev_user_accepts_all_state_values(self, state_value: str) -> None:
        """Test that RevUser model accepts all valid state values.

        Args:
            state_value: User state string value from the API.

        This test ensures that the RevUser Pydantic model can parse all state
        values that the DevRev API may return, preventing validation errors
        when new states are added or when rarely-used states are encountered.
        """
        user_data = {"id": "don:identity:dvrv-us-1:devo/1:revu/456", "state": state_value}
        user = RevUser.model_validate(user_data)

        assert user.state == RevUserState(state_value)
        assert user.id == "don:identity:dvrv-us-1:devo/1:revu/456"

    @pytest.mark.parametrize(
        "state_value",
        ["active", "deactivated", "deleted", "locked", "shadow", "unassigned"],
    )
    def test_rev_users_list_response_accepts_all_states(self, state_value: str) -> None:
        """Test that RevUsersListResponse can parse users with all state values.

        Args:
            state_value: User state string value from the API.

        This test verifies that the list response model correctly handles users
        with any valid state value, ensuring pagination and list operations work
        regardless of user state.
        """
        response_data = {
            "rev_users": [
                {"id": "don:identity:dvrv-us-1:devo/1:revu/1", "state": state_value},
                {"id": "don:identity:dvrv-us-1:devo/1:revu/2", "state": "active"},
            ],
            "next_cursor": None,
        }
        response = RevUsersListResponse.model_validate(response_data)

        assert len(response.rev_users) == 2
        assert response.rev_users[0].state == RevUserState(state_value)
        assert response.rev_users[1].state == RevUserState.ACTIVE

    def test_rev_users_list_response_with_mixed_states(self) -> None:
        """Test RevUsersListResponse with users in various states.

        This test verifies that a single response can contain users with
        different states, which is the typical real-world scenario.
        """
        response_data = {
            "rev_users": [
                {"id": "don:identity:dvrv-us-1:devo/1:revu/1", "state": "active"},
                {"id": "don:identity:dvrv-us-1:devo/1:revu/2", "state": "deactivated"},
                {"id": "don:identity:dvrv-us-1:devo/1:revu/3", "state": "locked"},
                {"id": "don:identity:dvrv-us-1:devo/1:revu/4", "state": "shadow"},
                {"id": "don:identity:dvrv-us-1:devo/1:revu/5", "state": "deleted"},
                {"id": "don:identity:dvrv-us-1:devo/1:revu/6", "state": "unassigned"},
            ],
            "next_cursor": "cursor_xyz789",
        }
        response = RevUsersListResponse.model_validate(response_data)

        assert len(response.rev_users) == 6
        assert response.rev_users[0].state == RevUserState.ACTIVE
        assert response.rev_users[1].state == RevUserState.DEACTIVATED
        assert response.rev_users[2].state == RevUserState.LOCKED
        assert response.rev_users[3].state == RevUserState.SHADOW
        assert response.rev_users[4].state == RevUserState.DELETED
        assert response.rev_users[5].state == RevUserState.UNASSIGNED
        assert response.next_cursor == "cursor_xyz789"
