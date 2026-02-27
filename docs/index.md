# DevRev Python SDK & MCP Server

[![Built with Augment](https://img.shields.io/badge/Built%20with-Auggie-6366f1?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0xMiAyTDIgMTloMjBMMTIgMnptMCAzLjc1TDE4LjI1IDE3SDUuNzVMMTIgNS43NXoiLz48L3N2Zz4=)](https://www.augmentcode.com/)
[![PyPI Version](https://img.shields.io/pypi/v/devrev-python-sdk.svg)](https://pypi.org/project/devrev-Python-SDK/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

<div class="augment-hero" markdown>

A modern, type-safe Python SDK and **MCP Server** for the [DevRev API](https://devrev.ai).

<p class="hero-subtitle">Full API coverage with 78+ MCP tools for AI assistants. Built with Pydantic v2, async support, and production-ready deployment to Google Cloud Run.</p>

</div>

<div class="mcp-highlight" markdown>

### :material-robot: MCP Server — Connect DevRev to Your AI Assistant

The DevRev MCP Server exposes **78+ tools**, **7 resources**, and **8 workflow prompts** through the Model Context Protocol. Works with Augment Code, Claude Desktop, Cursor, and any MCP-compatible client.

[:octicons-arrow-right-24: Get Started with MCP](mcp/index.md){ .md-button .md-button--primary }
[:octicons-arrow-right-24: View Tools Reference](mcp/tools-reference.md){ .md-button }

</div>

<div class="grid cards" markdown>

-   :material-robot:{ .lg .middle } __MCP Server__

    ---

    78+ AI-accessible tools for tickets, accounts, articles, and more. Deploy locally or on Cloud Run.

    [:octicons-arrow-right-24: MCP Server](mcp/index.md)

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

-   :material-shield-check:{ .lg .middle } __Production Ready__

    ---

    Retries, rate limiting, circuit breaker, and Cloud Run deployment

    [:octicons-arrow-right-24: Deployment](mcp/deployment.md)

-   :material-book-open-variant:{ .lg .middle } __Well Documented__

    ---

    Comprehensive guides and examples

    [:octicons-arrow-right-24: Guides](guides/index.md)

</div>

## SDK Features

- ✅ **Full API Coverage** — All 209 DevRev public API endpoints + 74 beta endpoints
- ✅ **Type-Safe Models** — Pydantic v2 models for all request/response objects
- ✅ **Async Support** — Native async/await support
- ✅ **Automatic Retries** — Configurable retry logic with exponential backoff
- ✅ **Rate Limiting** — Built-in rate limit handling
- ✅ **Rich Exceptions** — Detailed, actionable error messages
- ✅ **Beautiful Logging** — Colored console output with configurable levels

## MCP Server Features

- ✅ **78+ MCP Tools** — Full CRUD for all DevRev resources
- ✅ **7 Resource Templates** — `devrev://` URI scheme for data browsing
- ✅ **8 Workflow Prompts** — Triage, respond, escalate, investigate, and more
- ✅ **3 Transports** — stdio, Streamable HTTP, SSE
- ✅ **Per-User Auth** — DevRev PAT authentication for teams
- ✅ **Cloud Run Ready** — One-command production deployment

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

- **Python 3.11+** — Supports current stable Python and the two previous minor versions (N-2)
- **DevRev API Token** — Get one from your DevRev dashboard

## Installation

```bash
pip install devrev-python-sdk
```

For MCP Server support:
```bash
pip install devrev-python-sdk[mcp]
```

See the [Installation Guide](getting-started/installation.md) for more options.

## Next Steps

<div class="grid cards" markdown>

-   :material-robot: [**MCP Server Quick Start**](mcp/quickstart.md)

    Connect your AI assistant to DevRev in 5 minutes

-   :material-rocket-launch: [**SDK Quick Start**](getting-started/quickstart.md)

    Get up and running with your first API call

-   :material-key: [**Authentication**](getting-started/authentication.md)

    Learn about authentication methods

-   :material-api: [**API Reference**](api/index.md)

    Complete API documentation

</div>

