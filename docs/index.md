# DevRev Python SDK

[![Built with Augment](https://img.shields.io/badge/Built%20with-Auggie-6366f1?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0xMiAyTDIgMTloMjBMMTIgMnptMCAzLjc1TDE4LjI1IDE3SDUuNzVMMTIgNS43NXoiLz48L3N2Zz4=)](https://www.augmentcode.com/)
[![PyPI Version](https://img.shields.io/pypi/v/devrev-python-sdk.svg)](https://pypi.org/project/devrev-Python-SDK/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A modern, type-safe Python SDK for the [DevRev API](https://devrev.ai).

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Quick to Install__

    ---

    Install with pip and get started in minutes

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

-   :material-code-json:{ .lg .middle } __Type Safe__

    ---

    Full type annotations with Pydantic v2 models

    [:octicons-arrow-right-24: API Reference](api/index.md)

-   :material-lightning-bolt:{ .lg .middle } __Async Ready__

    ---

    Native async/await support for high-performance apps

    [:octicons-arrow-right-24: Sync vs Async](guides/sync-vs-async.md)

-   :material-book-open-variant:{ .lg .middle } __Well Documented__

    ---

    Comprehensive guides and examples

    [:octicons-arrow-right-24: Guides](guides/index.md)

</div>

## Features

- ✅ **Full API Coverage** - All 209 DevRev public API endpoints
- ✅ **Type-Safe Models** - Pydantic v2 models for all request/response objects
- ✅ **Async Support** - Native async/await support
- ✅ **Automatic Retries** - Configurable retry logic with exponential backoff
- ✅ **Rate Limiting** - Built-in rate limit handling
- ✅ **Rich Exceptions** - Detailed, actionable error messages
- ✅ **Beautiful Logging** - Colored console output with configurable levels

## Quick Example

=== "Synchronous"

    ```python
    from devrev import DevRevClient

    # Initialize client (reads DEVREV_API_TOKEN from environment)
    client = DevRevClient()

    # List accounts
    accounts = client.accounts.list(limit=10)
    for account in accounts.accounts:
        print(f"{account.id}: {account.display_name}")

    # Create a ticket
    ticket = client.works.create(
        type="ticket",
        title="Bug Report: Login Issue",
        applies_to_part="don:core:...",
        body="Users cannot log in after password reset"
    )
    ```

=== "Asynchronous"

    ```python
    import asyncio
    from devrev import AsyncDevRevClient

    async def main():
        async with AsyncDevRevClient() as client:
            # List accounts
            accounts = await client.accounts.list(limit=10)
            for account in accounts.accounts:
                print(f"{account.id}: {account.display_name}")

    asyncio.run(main())
    ```

## Requirements

- **Python 3.11+** - Supports current stable Python and the two previous minor versions (N-2)
- **DevRev API Token** - Get one from your DevRev dashboard

## Installation

```bash
pip install devrev-python-sdk
```

See the [Installation Guide](getting-started/installation.md) for more options.

## Next Steps

<div class="grid cards" markdown>

-   :material-rocket-launch: [**Quick Start**](getting-started/quickstart.md)

    Get up and running with your first API call

-   :material-key: [**Authentication**](getting-started/authentication.md)

    Learn about authentication methods

-   :material-book: [**Guides**](guides/index.md)

    In-depth guides for common tasks

-   :material-api: [**API Reference**](api/index.md)

    Complete API documentation

</div>

