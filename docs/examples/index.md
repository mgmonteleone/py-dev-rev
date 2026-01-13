# Examples

Real-world examples demonstrating DevRev SDK usage.

## Overview

Browse examples from simple scripts to complete applications:

<div class="grid cards" markdown>

-   :material-code-tags:{ .lg .middle } **Basic Usage**

    Simple examples for common operations.

    [:octicons-arrow-right-24: Basic Examples](basic.md)

-   :material-rocket-launch:{ .lg .middle } **Advanced Patterns**

    Complex patterns and best practices.

    [:octicons-arrow-right-24: Advanced Examples](advanced.md)

-   :material-link:{ .lg .middle } **Framework Integrations**

    FastAPI, Flask, and cloud function examples.

    [:octicons-arrow-right-24: Integration Examples](integrations.md)

</div>

## Quick Examples

### List Accounts

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.accounts.list(limit=10)
for account in response.accounts:
    print(f"{account.id}: {account.display_name}")
```

### Create a Ticket

```python
from devrev import DevRevClient
from devrev.models import WorkType

client = DevRevClient()

response = client.works.create(
    type=WorkType.TICKET,
    title="Customer Issue",
    applies_to_part="don:core:...",
    body="Description of the issue...",
)
print(f"Created: {response.work.display_id}")
```

### Async Operations

```python
import asyncio
from devrev import AsyncDevRevClient

async def main():
    async with AsyncDevRevClient() as client:
        response = await client.accounts.list()
        print(f"Found {len(response.accounts)} accounts")

asyncio.run(main())
```

## Example Applications

| Example | Description | Complexity |
|---------|-------------|------------|
| [List Accounts](basic.md#list-accounts) | Simple account listing | Beginner |
| [Create Work Items](basic.md#create-work-items) | Creating tickets and issues | Beginner |
| [Pagination](basic.md#pagination) | Iterating large datasets | Beginner |
| [Error Handling](basic.md#error-handling) | Handling API errors | Beginner |
| [Concurrent Requests](advanced.md#concurrent-requests) | Parallel async operations | Intermediate |
| [Webhook Handler](advanced.md#webhook-handler) | Processing webhooks | Intermediate |
| [FastAPI Integration](integrations.md#fastapi) | Web application | Advanced |
| [Cloud Functions](integrations.md#cloud-functions) | Serverless deployment | Advanced |

## Standalone Examples

The `/examples` directory contains runnable examples:

```
examples/
├── basic/
│   ├── list_accounts.py
│   ├── create_work.py
│   ├── search_users.py
│   └── async_example.py
├── applications/
│   ├── support_dashboard/
│   ├── webhook_handler/
│   └── data_export/
└── integrations/
    ├── fastapi/
    ├── flask/
    └── cloud_functions/
```

Run examples:

```bash
# Set your API token
export DEVREV_API_TOKEN="your-token"

# Run an example
python examples/basic/list_accounts.py
```

