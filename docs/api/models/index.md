# Models

Pydantic models for request and response data.

## Overview

All data in the SDK is represented as Pydantic v2 models, providing:

- **Type Safety** - Full type annotations
- **Validation** - Automatic input validation
- **Serialization** - Easy JSON conversion
- **IDE Support** - Autocomplete and type hints

## Model Categories

### Base Models

Common base classes and utilities:

- [`DevRevBaseModel`](base.md#devrevbasemodel) - Base for all models
- [`DevRevResponseModel`](base.md#devrevresponsemodel) - Base for response models
- [`PaginatedResponse`](base.md#paginatedresponse) - Base for paginated responses

[:octicons-arrow-right-24: Base Models](base.md)

### Resource Models

Models for specific resources:

| Resource | Description |
|----------|-------------|
| [Accounts](accounts.md) | Customer account models |
| [Works](works.md) | Work item models (tickets, issues) |
| [Users](users.md) | User models (dev and rev users) |

## Common Patterns

### Creating Requests

```python
from devrev.models import WorksCreateRequest, WorkType

request = WorksCreateRequest(
    type=WorkType.TICKET,
    title="Bug Report",
    applies_to_part="don:core:...",
)
```

### Parsing Responses

```python
from devrev.models import Work

# Response is automatically parsed
response = client.works.get(id="...")
work: Work = response.work

# Access typed properties
print(work.title)
print(work.type)
print(work.stage.name if work.stage else "N/A")
```

### Model Validation

```python
from devrev.models import WorksCreateRequest
from pydantic import ValidationError

try:
    request = WorksCreateRequest(
        type="invalid",  # Invalid enum value
        title="",  # Empty string not allowed
    )
except ValidationError as e:
    print(e.errors())
```

### Serialization

```python
# To dict
data = work.model_dump()

# To JSON
json_str = work.model_dump_json()

# Exclude None values
data = work.model_dump(exclude_none=True)
```

## Type Hints

All models support full type hints:

```python
from devrev.models import Work, WorkType

def process_work(work: Work) -> str:
    if work.type == WorkType.TICKET:
        return f"Ticket: {work.title}"
    return f"Other: {work.title}"
```

