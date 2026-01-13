#!/usr/bin/env python3
"""Create work items (tickets and issues).

This example demonstrates creating different types of
work items using the DevRev SDK.

Usage:
    export DEVREV_API_TOKEN="your-token"
    python create_work.py
"""

from devrev import DevRevClient
from devrev.models import IssuePriority, TicketSeverity, WorkType


def create_ticket(client: DevRevClient, part_id: str) -> str:
    """Create a support ticket."""
    response = client.works.create(
        type=WorkType.TICKET,
        title="Customer cannot access dashboard",
        applies_to_part=part_id,
        body="""
Customer reports 500 error when loading dashboard.

Steps to reproduce:
1. Log in as customer
2. Click on Dashboard
3. See error message

Expected: Dashboard loads
Actual: 500 Internal Server Error
        """,
        severity=TicketSeverity.HIGH,
    )

    print(f"Created ticket: {response.work.display_id}")
    print(f"  ID: {response.work.id}")
    return response.work.id


def create_issue(client: DevRevClient, part_id: str) -> str:
    """Create an engineering issue."""
    response = client.works.create(
        type=WorkType.ISSUE,
        title="Implement dark mode support",
        applies_to_part=part_id,
        body="Add dark mode toggle to user preferences.",
        priority=IssuePriority.P2,
    )

    print(f"Created issue: {response.work.display_id}")
    print(f"  ID: {response.work.id}")
    return response.work.id


def main() -> None:
    """Create example work items."""
    client = DevRevClient()

    # Get a part to associate with
    parts_response = client.parts.list(limit=1)
    if not parts_response.parts:
        print("No parts found. Create a part first.")
        return

    part_id = parts_response.parts[0].id
    print(f"Using part: {part_id}\n")

    # Create work items
    print("Creating a ticket...")
    create_ticket(client, part_id)

    print("\nCreating an issue...")
    create_issue(client, part_id)


if __name__ == "__main__":
    main()

