# Works Service

Manage work items (issues, tickets, tasks, opportunities) in DevRev.

In DevRev, **works** is the umbrella type covering tickets (customer support),
issues (engineering), and tasks.

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
        - list_modified_since
        - list_created_since

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

### Sort Order

`list` and `export` accept a `sort_by` parameter. Both forms are accepted and
normalized to the server form before the request is sent:

- Canonical: `"modified_date:desc"`, `"created_date:asc"`
- Legacy shortcut: `"-modified_date"` (descending), `"created_date"` (ascending)

```python
# Canonical form
response = client.works.list(
    type=[WorkType.TICKET],
    sort_by=["modified_date:desc"],
)

# Legacy shortcut — normalized internally to "modified_date:desc"
response = client.works.list(
    type=[WorkType.TICKET],
    sort_by=["-modified_date"],
)
```

!!! note "Server requires `field:direction`"
    The DevRev server rejects bare `"-field"` entries. The SDK normalizes
    legacy shortcuts to the `field:direction` form on your behalf — you do not
    need to change existing call sites, but new code should prefer the
    canonical form.

### List Work Items Modified or Created Since

Use `list_modified_since` / `list_created_since` to stream work items that
changed within a recent window. Both helpers page server-side sorted
`{timestamp_field}:desc` and early-exit as soon as a record older than the
cutoff is seen.

```python
from datetime import datetime, timedelta, timezone
from devrev import DevRevClient
from devrev.models import WorkType

client = DevRevClient()

cutoff = datetime.now(timezone.utc) - timedelta(days=7)

# All works modified in the last 7 days
recent = client.works.list_modified_since(
    cutoff,
    type=[WorkType.TICKET, WorkType.ISSUE],
)

# Cap total items; page_size tunes per-request page size
recent_capped = client.works.list_created_since(
    cutoff,
    type=[WorkType.TICKET],
    limit=500,
    page_size=100,
)
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

        # Async variants of the time-based helpers
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        recent = await client.works.list_modified_since(cutoff)

asyncio.run(main())
```

## Related Models

- [`Work`](../models/works.md#work)
- [`WorkType`](../models/works.md#worktype)
- [`IssuePriority`](../models/works.md#issuepriority)
- [`TicketSeverity`](../models/works.md#ticketseverity)

