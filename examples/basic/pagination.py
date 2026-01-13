#!/usr/bin/env python3
"""Pagination example.

This example demonstrates iterating through paginated results
using cursor-based pagination.

Usage:
    export DEVREV_API_TOKEN="your-token"
    python pagination.py
"""

from devrev import DevRevClient


def main() -> None:
    """Demonstrate pagination through all work items."""
    client = DevRevClient()

    print("Fetching all work items with pagination...\n")

    cursor = None
    total = 0
    page = 1

    while True:
        print(f"Fetching page {page}...")
        response = client.works.list(cursor=cursor, limit=100)

        for work in response.works:
            total += 1
            print(f"  {total}. [{work.type}] {work.title[:50]}")

        print(f"  → Got {len(response.works)} items\n")

        cursor = response.next_cursor
        if not cursor:
            break

        page += 1

    print(f"\nTotal: {total} work items")


if __name__ == "__main__":
    main()
