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
from devrev.models.articles import ArticlesListRequest

client = DevRevClient()

# Using a request object
request = ArticlesListRequest(limit=20)
articles = client.articles.list(request)
for article in articles:
    print(f"{article.title}")
```

### Get Article

```python
from devrev.models.articles import ArticlesGetRequest

request = ArticlesGetRequest(id="don:core:dvrv-us-1:devo/1:article/123")
article = client.articles.get(request)
print(f"Article: {article.title}")
if article.content:
    print(f"Content: {article.content[:100]}...")
```

### Create Article

```python
from devrev.models.articles import ArticlesCreateRequest

request = ArticlesCreateRequest(
    title="Getting Started Guide",
    content="# Welcome\n\nThis guide helps you get started...",
)
article = client.articles.create(request)
print(f"Created: {article.id}")
```

