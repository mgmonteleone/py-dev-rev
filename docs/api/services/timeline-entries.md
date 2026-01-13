# Timeline Entries Service

Manage timeline entries for activity tracking in DevRev.

## TimelineEntriesService

::: devrev.services.timeline_entries.TimelineEntriesService
    options:
      show_source: true

## AsyncTimelineEntriesService

::: devrev.services.timeline_entries.AsyncTimelineEntriesService
    options:
      show_source: true

## Usage Examples

### List Timeline Entries

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.timeline_entries.list(
    object="don:core:dvrv-us-1:devo/1:ticket/123"
)
for entry in response.timeline_entries:
    print(f"{entry.created_date}: {entry.type}")
```

### Create Timeline Entry

```python
response = client.timeline_entries.create(
    object="don:core:dvrv-us-1:devo/1:ticket/123",
    type="timeline_comment",
    body="Added a comment to track progress.",
)
print(f"Created: {response.timeline_entry.id}")
```

