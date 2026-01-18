# Question Answers Service

Manage Q&A knowledge base entries for customer self-service and support.

!!! info "Beta API Only"
    This service is only available when using `APIVersion.BETA`. See [Beta API Overview](index.md) for setup instructions.

## QuestionAnswersService

::: devrev.services.question_answers.QuestionAnswersService
    options:
      show_source: true
      members:
        - create
        - get
        - list
        - update
        - delete

## AsyncQuestionAnswersService

::: devrev.services.question_answers.AsyncQuestionAnswersService
    options:
      show_source: true

## Usage Examples

### Create a Question Answer

```python
from devrev import DevRevClient, APIVersion
from devrev.models.question_answers import QuestionAnswersCreateRequest

client = DevRevClient(api_version=APIVersion.BETA)

request = QuestionAnswersCreateRequest(
    question="How do I reset my password?",
    answer="Click 'Forgot Password' on the login page and follow the email instructions.",
    tags=["don:core:dvrv-us-1:devo/1:tag/123"],
)

qa = client.question_answers.create(request)
print(f"Created Q&A: {qa.id}")
```

### List Question Answers

```python
from devrev.models.question_answers import QuestionAnswersListRequest

# List all Q&As
request = QuestionAnswersListRequest()
response = client.question_answers.list(request)

for qa in response.question_answers:
    print(f"Q: {qa.question}")
    print(f"A: {qa.answer}")
    print("---")

# With pagination
request = QuestionAnswersListRequest(limit=20)
response = client.question_answers.list(request)
```

### Get a Question Answer

```python
from devrev.models.question_answers import QuestionAnswersGetRequest

request = QuestionAnswersGetRequest(
    id="don:core:dvrv-us-1:devo/1:qa/456"
)

qa = client.question_answers.get(request)
print(f"Question: {qa.question}")
print(f"Answer: {qa.answer}")
```

### Update a Question Answer

```python
from devrev.models.question_answers import QuestionAnswersUpdateRequest

request = QuestionAnswersUpdateRequest(
    id="don:core:dvrv-us-1:devo/1:qa/456",
    question="How do I reset my password?",
    answer="Updated: Click 'Forgot Password' on the login page, enter your email, and follow the reset link sent to your inbox.",
)

qa = client.question_answers.update(request)
```

### Delete a Question Answer

```python
from devrev.models.question_answers import QuestionAnswersDeleteRequest

request = QuestionAnswersDeleteRequest(
    id="don:core:dvrv-us-1:devo/1:qa/456"
)

client.question_answers.delete(request)
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion
from devrev.models.question_answers import (
    QuestionAnswersCreateRequest,
    QuestionAnswersListRequest,
)

async def main():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Create Q&A
        request = QuestionAnswersCreateRequest(
            question="What are your support hours?",
            answer="We provide 24/7 support for enterprise customers.",
        )
        qa = await client.question_answers.create(request)
        
        # List Q&As
        list_request = QuestionAnswersListRequest(limit=10)
        response = await client.question_answers.list(list_request)
        for qa in response.question_answers:
            print(qa.question)

asyncio.run(main())
```

## Related Models

### QuestionAnswer

The main Q&A model with properties:

- `id` - Unique Q&A identifier
- `question` - The question text
- `answer` - The answer text
- `tags` - Associated tag IDs
- `created_date` - When the Q&A was created
- `modified_date` - When the Q&A was last updated

### Request Models

- `QuestionAnswersCreateRequest` - Create a new Q&A
- `QuestionAnswersGetRequest` - Retrieve a Q&A by ID
- `QuestionAnswersListRequest` - List Q&As with pagination
- `QuestionAnswersUpdateRequest` - Update an existing Q&A
- `QuestionAnswersDeleteRequest` - Delete a Q&A

## Pagination

The `list()` method returns a paginated response:

```python
from devrev.models.question_answers import QuestionAnswersListRequest

request = QuestionAnswersListRequest(limit=50)
response = client.question_answers.list(request)

# Process first page
for qa in response.question_answers:
    print(qa.question)

# Get next page if available
if response.next_cursor:
    next_request = QuestionAnswersListRequest(
        cursor=response.next_cursor,
        limit=50,
    )
    next_response = client.question_answers.list(next_request)
```

## Best Practices

1. **Write clear questions** - Use natural language that matches how users search
2. **Provide complete answers** - Include step-by-step instructions and examples
3. **Tag appropriately** - Use tags to categorize Q&As by topic or product area
4. **Keep updated** - Regularly review and update answers as features change
5. **Link related content** - Reference related articles or documentation in answers
6. **Use consistent formatting** - Maintain a consistent style across all Q&As

