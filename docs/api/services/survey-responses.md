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

## Pagination

`survey_responses.list(...)` returns a paginated response with `next_cursor`.
When you need more than one page, pass the returned cursor into a follow-up
call and continue until `next_cursor` is `None`.

## Related Models

- [`SurveyResponse`](../models/survey-responses.md#surveyresponse)
- [`SurveyResponsesListRequest`](../models/survey-responses.md#surveyresponseslistrequest)
- [`SurveyResponsesListResponse`](../models/survey-responses.md#surveyresponseslistresponse)
- [`SurveyResponsesListMode`](../models/survey-responses.md#surveyresponseslistmode)