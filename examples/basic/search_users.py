#!/usr/bin/env python3
"""Search and list users.

This example demonstrates listing dev users (internal)
and rev users (external customers) using the DevRev SDK.

Usage:
    export DEVREV_API_TOKEN="your-token"
    python search_users.py
"""

from devrev import DevRevClient


def main() -> None:
    """List dev and rev users."""
    client = DevRevClient()

    # List dev users (internal team)
    print("Dev Users (Internal Team):")
    print("-" * 40)
    dev_response = client.dev_users.list(limit=10)
    for user in dev_response.dev_users:
        email = getattr(user, "email", "N/A")
        print(f"  • {user.display_name}")
        print(f"    Email: {email}")
        print()

    # List rev users (customers)
    print("\nRev Users (Customers):")
    print("-" * 40)
    rev_response = client.rev_users.list(limit=10)
    for user in rev_response.rev_users:
        print(f"  • {user.display_name}")
        print(f"    ID: {user.id}")
        print()


if __name__ == "__main__":
    main()
