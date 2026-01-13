# Code Changes Service

Track code changes and commits in DevRev.

## CodeChangesService

::: devrev.services.code_changes.CodeChangesService
    options:
      show_source: true

## AsyncCodeChangesService

::: devrev.services.code_changes.AsyncCodeChangesService
    options:
      show_source: true

## Usage Examples

### List Code Changes

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.code_changes.list(limit=20)
for change in response.code_changes:
    print(f"{change.title}")
```

### Get Code Change

```python
response = client.code_changes.get(id="don:core:dvrv-us-1:devo/1:code_change/123")
print(f"Title: {response.code_change.title}")
```

