#!/usr/bin/env python3
"""List all customer accounts.

This example demonstrates basic usage of the DevRev SDK
to list customer accounts.

Usage:
    export DEVREV_API_TOKEN="your-token"
    python list_accounts.py
"""

from devrev import DevRevClient


def main() -> None:
    """List all accounts with basic information."""
    client = DevRevClient()

    print("Fetching accounts...\n")

    response = client.accounts.list(limit=20)

    print(f"Found {len(response.accounts)} accounts:\n")
    for account in response.accounts:
        print(f"  • {account.display_name}")
        print(f"    ID: {account.id}")
        if account.domains:
            print(f"    Domains: {', '.join(account.domains)}")
        print()


if __name__ == "__main__":
    main()
