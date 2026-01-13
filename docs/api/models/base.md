# Base Models

Base classes and common utilities for all models.

## DevRevBaseModel

Base class for all request models.

::: devrev.models.base.DevRevBaseModel
    options:
      show_source: true

## DevRevResponseModel

Base class for all response models.

::: devrev.models.base.DevRevResponseModel
    options:
      show_source: true

## PaginatedResponse

Base class for paginated responses.

::: devrev.models.base.PaginatedResponse
    options:
      show_source: true
      members:
        - next_cursor
        - prev_cursor

## Common Types

### UserSummary

::: devrev.models.base.UserSummary
    options:
      show_source: true

### StageInfo

::: devrev.models.base.StageInfo
    options:
      show_source: true

### TagWithValue

::: devrev.models.base.TagWithValue
    options:
      show_source: true

### DateFilter

::: devrev.models.base.DateFilter
    options:
      show_source: true

## Usage Examples

### Extending Base Models

```python
from devrev.models.base import DevRevBaseModel

class MyRequest(DevRevBaseModel):
    name: str
    value: int
```

### Working with Pagination

```python
# PaginatedResponse provides cursor-based pagination
response = client.accounts.list()

if response.next_cursor:
    next_page = client.accounts.list(cursor=response.next_cursor)
```

### Using Date Filters

```python
from devrev.models.base import DateFilter
from datetime import datetime

# Filter by date range
filter = DateFilter(
    after=datetime(2024, 1, 1),
    before=datetime(2024, 12, 31),
)
```

