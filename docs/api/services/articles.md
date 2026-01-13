# Articles Service

Manage knowledge base articles in DevRev.

## ArticlesService

::: devrev.services.articles.ArticlesService
    options:
      show_source: true

## AsyncArticlesService

::: devrev.services.articles.AsyncArticlesService
    options:
      show_source: true

## Usage Examples

### List Articles

```python
from devrev import DevRevClient

client = DevRevClient()

response = client.articles.list(limit=20)
for article in response.articles:
    print(f"{article.title}")
```

### Get Article

```python
response = client.articles.get(id="don:core:dvrv-us-1:devo/1:article/123")
print(f"Article: {response.article.title}")
print(f"Content: {response.article.body[:100]}...")
```

### Create Article

```python
response = client.articles.create(
    title="Getting Started Guide",
    applies_to_parts=["don:core:dvrv-us-1:devo/1:part/1"],
    body="# Welcome\n\nThis guide helps you get started...",
)
print(f"Created: {response.article.id}")
```

