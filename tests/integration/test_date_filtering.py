"""Integration smoke tests for date-based listing helpers.

Verifies that ``list_modified_since`` on works and conversations returns
records whose ``modified_date`` is at or after the requested cutoff, and
respects the ``limit`` cap. Tests are read-only and gated on
``DEVREV_API_TOKEN`` being set.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest

from devrev import DevRevClient
from devrev.models.works import WorkType

logger = logging.getLogger(__name__)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.environ.get("DEVREV_API_TOKEN"),
        reason="DEVREV_API_TOKEN environment variable not set",
    ),
]


@pytest.fixture
def client() -> Iterator[DevRevClient]:
    """Create a DevRev client using the ambient DEVREV_API_TOKEN."""
    with DevRevClient() as c:
        yield c


def test_works_list_modified_since_returns_recent_tickets(client: DevRevClient) -> None:
    """Tickets modified in the last 24h are returned with modified_date >= cutoff."""
    after = datetime.now(tz=UTC) - timedelta(hours=24)

    result = client.works.list_modified_since(
        after=after,
        type=[WorkType.TICKET],
        limit=5,
    )

    assert len(result) <= 5

    for work in result:
        if work.modified_date is not None:
            assert work.modified_date >= after, (
                f"Work {work.id} modified_date {work.modified_date} is older than cutoff {after}"
            )
        else:
            logger.info("Work %s has no modified_date; skipping cutoff assertion", work.id)


def test_conversations_list_modified_since_returns_recent(client: DevRevClient) -> None:
    """Conversations modified in the last 24h are returned with modified_date >= cutoff."""
    after = datetime.now(tz=UTC) - timedelta(hours=24)

    result = client.conversations.list_modified_since(after=after, limit=5)

    assert len(result) <= 5

    for conversation in result:
        if conversation.modified_date is not None:
            assert conversation.modified_date >= after, (
                f"Conversation {conversation.id} modified_date "
                f"{conversation.modified_date} is older than cutoff {after}"
            )
        else:
            logger.info(
                "Conversation %s has no modified_date; skipping cutoff assertion",
                conversation.id,
            )
