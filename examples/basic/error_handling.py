#!/usr/bin/env python3
"""Error handling example.

This example demonstrates proper error handling patterns
when using the DevRev SDK.

Usage:
    export DEVREV_API_TOKEN="your-token"
    python error_handling.py
"""

from devrev import DevRevClient
from devrev.exceptions import (
    AuthenticationError,
    DevRevError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


def safe_get_work(client: DevRevClient, work_id: str) -> None:
    """Safely get a work item with proper error handling."""
    try:
        response = client.works.get(id=work_id)
        print(f"Found: {response.work.title}")
        print(f"  Type: {response.work.type}")
        print(f"  ID: {response.work.id}")

    except NotFoundError:
        print(f"Work item {work_id} not found")

    except ValidationError as e:
        print(f"Invalid ID format: {e.message}")

    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")

    except AuthenticationError:
        print("Authentication failed. Check your API token.")

    except DevRevError as e:
        print(f"API error: {e.message}")


def main() -> None:
    """Demonstrate error handling."""
    client = DevRevClient()

    print("Testing error handling...\n")

    # Try a valid ID pattern but non-existent
    print("1. Testing NotFoundError:")
    safe_get_work(client, "don:core:dvrv-us-1:devo/1:ticket/99999999")

    # Try an invalid ID
    print("\n2. Testing ValidationError:")
    safe_get_work(client, "invalid-id")

    # Try getting a real work item
    print("\n3. Testing successful request:")
    works_response = client.works.list(limit=1)
    if works_response.works:
        safe_get_work(client, works_response.works[0].id)
    else:
        print("  No work items found")


if __name__ == "__main__":
    main()
