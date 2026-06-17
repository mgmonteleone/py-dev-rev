"""End-to-end integration tests for the Part move (re-parent) workaround.

Exercises ``client.parts.move`` against a real DevRev sandbox. The DevRev REST
API does not allow changing ``parent_part`` on ``parts.update``; ``parts.move``
implements a recreate-and-relink workaround (create a new part under the new
parent, relink dependents, delete the source). These tests verify that path
end-to-end:

- the dry-run reports a plan without mutating anything, and
- a real move re-parents a capability: a new part appears under the new parent
  and the original source part is deleted.

The tests are gated behind the same environment guards as the other write
integration tests, so they are SKIPPED (never failed) when sandbox credentials
are absent, keeping CI green.

To run these tests:
    export DEVREV_API_TOKEN="your-token"
    export DEVREV_WRITE_TESTS_ENABLED="true"
    pytest tests/integration/test_parts_move_e2e.py -v -m write

Related to CSS-846: Add ability to re-parent a Part (change parent_part).
"""

from __future__ import annotations

import logging
import os
from collections.abc import Generator
from typing import TYPE_CHECKING

import pytest

from devrev.exceptions import DevRevError, NotFoundError
from devrev.models.parts import (
    PartsCreateRequest,
    PartsDeleteRequest,
    PartsGetRequest,
    PartsMoveRequest,
    PartType,
)

if TYPE_CHECKING:
    from devrev.client import DevRevClient
    from tests.integration.utils import TestDataManager

logger = logging.getLogger(__name__)

# Mark all tests in this module.
# Check for either DEVREV_API_TOKEN or DEVREV_TEST_API_TOKEN (matches write_client fixture).
_has_api_token = bool(os.environ.get("DEVREV_API_TOKEN") or os.environ.get("DEVREV_TEST_API_TOKEN"))

pytestmark = [
    pytest.mark.integration,
    pytest.mark.write,
    pytest.mark.skipif(
        not _has_api_token,
        reason="DEVREV_API_TOKEN or DEVREV_TEST_API_TOKEN environment variable required",
    ),
    pytest.mark.skipif(
        os.environ.get("DEVREV_WRITE_TESTS_ENABLED", "").lower() not in ("true", "1", "yes"),
        reason="DEVREV_WRITE_TESTS_ENABLED must be set to 'true' for write tests",
    ),
]


def _delete_part_quietly(client: DevRevClient, part_id: str) -> None:
    """Best-effort delete of a part, swallowing not-found / already-deleted errors.

    ``TestDataManager`` registers parts for tracking but cannot delete them (its
    cleanup table has no ``part`` delete method), so part cleanup is done
    explicitly here. A move deletes the source part as part of its normal flow,
    so attempting to delete it again is expected to no-op/raise; that is ignored.
    """
    try:
        client.parts.delete(PartsDeleteRequest(id=part_id))
    except DevRevError as exc:  # NotFoundError is a DevRevError subclass.
        logger.debug("Cleanup: part %s already gone or undeletable: %s", part_id, exc)


@pytest.fixture
def created_parts(
    write_client: DevRevClient,
    skip_if_write_disabled: None,
) -> Generator[list[str], None, None]:
    """Track part IDs created by a test and delete them on teardown.

    Yields a mutable list; append every part ID the test creates (products,
    capabilities, and the NEW part id produced by a real move). Teardown deletes
    each one best-effort, in reverse creation order so children are removed
    before their parents.
    """
    part_ids: list[str] = []

    yield part_ids

    for part_id in reversed(part_ids):
        _delete_part_quietly(write_client, part_id)


def _create_product(
    client: DevRevClient,
    test_data: TestDataManager,
    created_parts: list[str],
    base_name: str,
) -> str:
    """Create a product part, register it for cleanup, and return its ID."""
    product = client.parts.create(
        PartsCreateRequest(
            name=test_data.generate_name(base_name),
            type=PartType.PRODUCT,
        )
    )
    created_parts.append(product.id)
    test_data.register("part", product.id)
    return product.id


def _create_capability(
    client: DevRevClient,
    test_data: TestDataManager,
    created_parts: list[str],
    base_name: str,
    parent_id: str,
) -> str:
    """Create a capability part under ``parent_id`` and return its ID."""
    capability = client.parts.create(
        PartsCreateRequest(
            name=test_data.generate_name(base_name),
            type=PartType.CAPABILITY,
            parent_part=[parent_id],
        )
    )
    created_parts.append(capability.id)
    test_data.register("part", capability.id)
    return capability.id


class TestPartsMoveE2E:
    """End-to-end tests for the recreate-and-relink part move against a sandbox."""

    def test_parts_move_dry_run_reports_plan_without_mutating(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        created_parts: list[str],
    ) -> None:
        """A dry-run move returns a plan and leaves the source part untouched."""
        # Arrange: product P1 with capability C under it, plus a second product P2.
        p1 = _create_product(write_client, test_data, created_parts, "MoveDryRunP1")
        p2 = _create_product(write_client, test_data, created_parts, "MoveDryRunP2")
        c = _create_capability(write_client, test_data, created_parts, "MoveDryRunC", p1)

        # Act: dry-run move C -> P2.
        result = write_client.parts.move(PartsMoveRequest(id=c, new_parent_part=p2, dry_run=True))

        # Assert: result describes a no-op dry run.
        assert result.dry_run is True
        assert result.new_part_id == ""  # sentinel: no part created on a dry run
        assert result.source_part_id == c
        assert result.source_deleted is False
        assert result.relinked_work_items == []
        assert result.reparented_children == []

        # Assert: plan has the correct shape and targets.
        assert result.plan.source_part_id == c
        assert result.plan.new_parent_part == p2
        assert result.plan.source_part_type == PartType.CAPABILITY.value
        assert result.plan.will_delete_source is False
        assert isinstance(result.plan.work_items_to_relink, list)
        assert isinstance(result.plan.child_parts_to_reparent, list)

        # Assert: the source capability still exists (no mutation occurred).
        still_there = write_client.parts.get(PartsGetRequest(id=c))
        assert still_there.id == c
        logger.info("✅ Dry-run move reported plan without mutating source %s", c)

    def test_parts_move_reparents_capability(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
        created_parts: list[str],
    ) -> None:
        """A real move re-parents a capability: new part created, source deleted."""
        # Arrange: products P1 and P2, capability C under P1.
        p1 = _create_product(write_client, test_data, created_parts, "MoveRealP1")
        p2 = _create_product(write_client, test_data, created_parts, "MoveRealP2")
        c = _create_capability(write_client, test_data, created_parts, "MoveRealC", p1)

        # Act: real move C -> P2.
        result = write_client.parts.move(PartsMoveRequest(id=c, new_parent_part=p2, dry_run=False))

        # Track the newly created part for cleanup before any further assertions.
        assert result.new_part_id
        created_parts.append(result.new_part_id)
        test_data.register("part", result.new_part_id)

        # Assert: result reflects a completed real move.
        assert result.dry_run is False
        assert result.source_part_id == c
        assert result.new_part_id != c
        assert result.source_deleted is True
        assert result.plan.new_parent_part == p2
        assert result.plan.will_delete_source is True

        # Assert: the new part resolves and is a capability (same type as source).
        new_part = write_client.parts.get(PartsGetRequest(id=result.new_part_id))
        assert new_part.id == result.new_part_id
        assert new_part.type == PartType.CAPABILITY

        # Assert: the original source capability is gone.
        with pytest.raises((NotFoundError, DevRevError)):
            write_client.parts.get(PartsGetRequest(id=c))
        logger.info(
            "✅ Re-parented capability %s -> new part %s under %s; source deleted",
            c,
            result.new_part_id,
            p2,
        )
