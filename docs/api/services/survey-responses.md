# Survey Responses Service

List survey and CSAT responses in DevRev.

Use this service when a ticket or work sync needs survey responses without
reaching through the private client transport.

## SurveyResponsesService

::: devrev.services.survey_responses.SurveyResponsesService
    options:
      show_source: true
      members:
        - list

## AsyncSurveyResponsesService

::: devrev.services.survey_responses.AsyncSurveyResponsesService
    options:
      show_source: true
      members:
        - list

## Usage Examples

### List responses for a ticket/work object

```python
from devrev import DevRevClient

client = DevRevClient()

responses = client.survey_responses.list(
    object_id="don:core:dvrv-us-1:devo/1:ticket/123",
    limit=50,
)

for survey_response in responses.survey_responses:
    print(survey_response.id, survey_response.response)
```

### Filter with multiple objects

```python
responses = client.survey_responses.list(
    objects=[
        "don:core:dvrv-us-1:devo/1:ticket/123",
        "don:core:dvrv-us-1:devo/1:ticket/456",
    ],
)
```

### Async usage

```python
import asyncio

from devrev import AsyncDevRevClient


async def main():
    async with AsyncDevRevClient() as client:
        responses = await client.survey_responses.list(
            object_id="don:core:dvrv-us-1:devo/1:ticket/123",
        )
        print(len(responses.survey_responses))


asyncio.run(main())
```

## Related Models

- `SurveyResponse`
- `SurveyResponsesListRequest`
- `SurveyResponsesListResponse`
- `SurveyResponsesListMode`