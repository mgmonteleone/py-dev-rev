"""Unit tests for the parts move (re-parent) models.

Covers construction and validation of the SDK-level move models added for
CSS-846: PartsMoveRequest, PartsMovePlan, and PartsMoveResult.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from devrev.models.parts import (
    PartsMovePlan,
    PartsMoveRequest,
    PartsMoveResult,
)


class TestPartsMoveRequest:
    """Tests for PartsMoveRequest."""

    def test_construct_with_required_fields(self) -> None:
        """A request can be built with only the required fields."""
        request = PartsMoveRequest(id="PROD-1", new_parent_part="PROD-2")

        assert request.id == "PROD-1"
        assert request.new_parent_part == "PROD-2"

    def test_dry_run_defaults_to_false(self) -> None:
        """dry_run defaults to False when not provided."""
        request = PartsMoveRequest(id="PROD-1", new_parent_part="PROD-2")

        assert request.dry_run is False

    def test_dry_run_can_be_set(self) -> None:
        """dry_run can be explicitly enabled."""
        request = PartsMoveRequest(id="PROD-1", new_parent_part="PROD-2", dry_run=True)

        assert request.dry_run is True

    def test_id_is_required(self) -> None:
        """Omitting id raises a validation error."""
        with pytest.raises(ValidationError):
            PartsMoveRequest(new_parent_part="PROD-2")  # type: ignore[call-arg]

    def test_new_parent_part_is_required(self) -> None:
        """Omitting new_parent_part raises a validation error."""
        with pytest.raises(ValidationError):
            PartsMoveRequest(id="PROD-1")  # type: ignore[call-arg]


class TestPartsMovePlan:
    """Tests for PartsMovePlan."""

    def test_construct_with_required_fields(self) -> None:
        """A plan can be built with only the required fields."""
        plan = PartsMovePlan(source_part_id="CAPL-1", new_parent_part="PROD-2")

        assert plan.source_part_id == "CAPL-1"
        assert plan.new_parent_part == "PROD-2"

    def test_list_and_optional_defaults(self) -> None:
        """List fields default to empty and optionals/bools have sane defaults."""
        plan = PartsMovePlan(source_part_id="CAPL-1", new_parent_part="PROD-2")

        assert plan.source_part_type is None
        assert plan.work_items_to_relink == []
        assert plan.child_parts_to_reparent == []
        assert plan.will_delete_source is False

    def test_construct_with_all_fields(self) -> None:
        """All fields can be populated."""
        plan = PartsMovePlan(
            source_part_id="CAPL-1",
            source_part_type="capability",
            new_parent_part="PROD-2",
            work_items_to_relink=["ISS-1", "ISS-2"],
            child_parts_to_reparent=["FEAT-1"],
            will_delete_source=True,
        )

        assert plan.source_part_type == "capability"
        assert plan.work_items_to_relink == ["ISS-1", "ISS-2"]
        assert plan.child_parts_to_reparent == ["FEAT-1"]
        assert plan.will_delete_source is True

    def test_source_part_id_is_required(self) -> None:
        """Omitting source_part_id raises a validation error."""
        with pytest.raises(ValidationError):
            PartsMovePlan(new_parent_part="PROD-2")  # type: ignore[call-arg]


class TestPartsMoveResult:
    """Tests for PartsMoveResult."""

    def _plan(self) -> PartsMovePlan:
        return PartsMovePlan(source_part_id="CAPL-1", new_parent_part="PROD-2")

    def test_construct_with_required_fields(self) -> None:
        """A result can be built with required fields and a nested plan."""
        result = PartsMoveResult(
            new_part_id="CAPL-9",
            source_part_id="CAPL-1",
            plan=self._plan(),
        )

        assert result.new_part_id == "CAPL-9"
        assert result.source_part_id == "CAPL-1"

    def test_defaults(self) -> None:
        """List/bool fields default appropriately."""
        result = PartsMoveResult(
            new_part_id="CAPL-9",
            source_part_id="CAPL-1",
            plan=self._plan(),
        )

        assert result.relinked_work_items == []
        assert result.reparented_children == []
        assert result.source_deleted is False
        assert result.dry_run is False

    def test_nests_a_plan(self) -> None:
        """PartsMoveResult nests a PartsMovePlan instance."""
        plan = self._plan()
        result = PartsMoveResult(
            new_part_id="CAPL-9",
            source_part_id="CAPL-1",
            plan=plan,
        )

        assert isinstance(result.plan, PartsMovePlan)
        assert result.plan.source_part_id == "CAPL-1"
        assert result.plan.new_parent_part == "PROD-2"

    def test_plan_coerced_from_dict(self) -> None:
        """A nested plan can be provided as a dict and is coerced to PartsMovePlan."""
        result = PartsMoveResult(
            new_part_id="CAPL-9",
            source_part_id="CAPL-1",
            plan={"source_part_id": "CAPL-1", "new_parent_part": "PROD-2"},  # type: ignore[arg-type]
        )

        assert isinstance(result.plan, PartsMovePlan)

    def test_plan_is_required(self) -> None:
        """Omitting the nested plan raises a validation error."""
        with pytest.raises(ValidationError):
            PartsMoveResult(new_part_id="CAPL-9", source_part_id="CAPL-1")  # type: ignore[call-arg]
