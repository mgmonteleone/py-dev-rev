#!/usr/bin/env python3
"""Async client usage example.

This example demonstrates using the async client for
concurrent API operations.

Usage:
    export DEVREV_API_TOKEN="your-token"
    python async_example.py
"""

import asyncio

from devrev import AsyncDevRevClient


async def main() -> None:
    """Demonstrate async client usage."""
    async with AsyncDevRevClient() as client:
        print("Fetching data concurrently...\n")

        # Run multiple requests concurrently
        accounts, works, dev_users, tags = await asyncio.gather(
            client.accounts.list(limit=5),
            client.works.list(limit=5),
            client.dev_users.list(limit=5),
            client.tags.list(),
        )

        print(f"Accounts: {len(accounts.accounts)}")
        for acc in accounts.accounts:
            print(f"  • {acc.display_name}")

        print(f"\nWorks: {len(works.works)}")
        for work in works.works:
            print(f"  • [{work.type}] {work.title}")

        print(f"\nDev Users: {len(dev_users.dev_users)}")
        for user in dev_users.dev_users:
            print(f"  • {user.display_name}")

        print(f"\nTags: {len(tags.tags)}")
        for tag in tags.tags:
            print(f"  • {tag.name}")


if __name__ == "__main__":
    asyncio.run(main())
