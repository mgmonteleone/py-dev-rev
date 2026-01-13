# Works Service

Manage work items (issues, tickets, tasks, opportunities) in DevRev.

## WorksService

::: devrev.services.works.WorksService
    options:
      show_source: true
      members:
        - list
        - get
        - create
        - update
        - delete
        - export
        - count

## AsyncWorksService

::: devrev.services.works.AsyncWorksService
    options:
      show_source: true

## Usage Examples

### List Work Items

```python
from devrev import DevRevClient
from devrev.models import WorkType

client = DevRevClient()

# List all work items
response = client.works.list(limit=10)
for work in response.works:
    print(f"[{work.type}] {work.title}")

# Filter by type
response = client.works.list(
    type=[WorkType.TICKET, WorkType.ISSUE],
    limit=20,
)

# Filter by stage
response = client.works.list(
    stage_name=["open", "in_progress"],
)
```

### Get Work Item

```python
response = client.works.get(id="don:core:dvrv-us-1:devo/1:ticket/123")
work = response.work
print(f"Title: {work.title}")
print(f"Type: {work.type}")
print(f"Stage: {work.stage.name if work.stage else 'N/A'}")
```

### Create Ticket

```python
from devrev.models import WorkType, TicketSeverity

response = client.works.create(
    type=WorkType.TICKET,
    title="Customer cannot access dashboard",
    applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
    body="Customer reports 500 error when loading dashboard.",
    severity=TicketSeverity.HIGH,
)
print(f"Created: {response.work.display_id}")
```

### Create Issue

```python
from devrev.models import WorkType, IssuePriority

response = client.works.create(
    type=WorkType.ISSUE,
    title="Implement dark mode",
    applies_to_part="don:core:dvrv-us-1:devo/1:part/1",
    body="Add dark mode support to the UI.",
    priority=IssuePriority.P2,
)
```

### Update Work Item

```python
response = client.works.update(
    id="don:core:dvrv-us-1:devo/1:ticket/123",
    title="Updated title",
    body="Updated description",
)
```

### Delete Work Item

```python
client.works.delete(id="don:core:dvrv-us-1:devo/1:ticket/123")
```

### Count Work Items

```python
response = client.works.count(type=[WorkType.TICKET])
print(f"Total tickets: {response.count}")
```

### Export Work Items

```python
response = client.works.export(
    type=[WorkType.ISSUE],
    first=5000,
)
print(f"Exported {len(response.works)} issues")
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient

async def main():
    async with AsyncDevRevClient() as client:
        response = await client.works.list(limit=10)
        for work in response.works:
            print(f"[{work.type}] {work.title}")

asyncio.run(main())
```

## Related Models

- [`Work`](../models/works.md#work)
- [`WorkType`](../models/works.md#worktype)
- [`IssuePriority`](../models/works.md#issuepriority)
- [`TicketSeverity`](../models/works.md#ticketseverity)

