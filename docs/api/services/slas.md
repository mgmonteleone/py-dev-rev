# SLAs Service

Manage service level agreements in DevRev.

## SlasService

::: devrev.services.slas.SlasService
    options:
      show_source: true

## AsyncSlasService

::: devrev.services.slas.AsyncSlasService
    options:
      show_source: true

## Usage Examples

### List SLAs

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.slas.list()
for sla in response.slas:
    print(f"{sla.name}")
```

### Get SLA

```python
response = client.slas.get(id="don:core:dvrv-us-1:devo/1:sla/123")
print(f"SLA: {response.sla.name}")
```

