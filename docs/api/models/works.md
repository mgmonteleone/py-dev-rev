# Work Models

Models for work items (tickets, issues, tasks, opportunities).

## Work

The main work item model.

::: devrev.models.works.Work
    options:
      show_source: true

## Enums

### WorkType

::: devrev.models.works.WorkType
    options:
      show_source: true

### IssuePriority

::: devrev.models.works.IssuePriority
    options:
      show_source: true

### TicketSeverity

::: devrev.models.works.TicketSeverity
    options:
      show_source: true

## Request Models

### WorksCreateRequest

::: devrev.models.works.WorksCreateRequest
    options:
      show_source: true

### WorksListRequest

::: devrev.models.works.WorksListRequest
    options:
      show_source: true

### WorksUpdateRequest

::: devrev.models.works.WorksUpdateRequest
    options:
      show_source: true

## Response Models

### WorksCreateResponse

::: devrev.models.works.WorksCreateResponse
    options:
      show_source: true

### WorksListResponse

::: devrev.models.works.WorksListResponse
    options:
      show_source: true

### WorksGetResponse

::: devrev.models.works.WorksGetResponse
    options:
      show_source: true

## Usage Examples

### Create a Ticket

```python
from devrev.models import WorksCreateRequest, WorkType, TicketSeverity

request = WorksCreateRequest(
    type=WorkType.TICKET,
    title="Customer cannot login",
    applies_to_part="don:core:...",
    severity=TicketSeverity.HIGH,
    body="Customer reports login issues...",
)
```

### Create an Issue

```python
from devrev.models import WorksCreateRequest, WorkType, IssuePriority

request = WorksCreateRequest(
    type=WorkType.ISSUE,
    title="Add dark mode support",
    applies_to_part="don:core:...",
    priority=IssuePriority.P2,
)
```

### Work with Work Response

```python
response = client.works.get(id="...")
work = response.work

print(f"Title: {work.title}")
print(f"Type: {work.type}")
print(f"Stage: {work.stage.name if work.stage else 'N/A'}")

if work.type == WorkType.TICKET:
    print(f"Severity: {work.severity}")
elif work.type == WorkType.ISSUE:
    print(f"Priority: {work.priority}")
```

