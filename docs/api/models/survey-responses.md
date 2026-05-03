# Survey Response Models

Models for survey and CSAT response operations.

## SurveyResponse

The main survey response model.

::: devrev.models.survey_responses.SurveyResponse
    options:
      show_source: true

## Enums

### SurveyResponsesListMode

::: devrev.models.survey_responses.SurveyResponsesListMode
    options:
      show_source: true

## Request Models

### SurveyResponsesListRequest

::: devrev.models.survey_responses.SurveyResponsesListRequest
    options:
      show_source: true

## Response Models

### SurveyResponsesListResponse

::: devrev.models.survey_responses.SurveyResponsesListResponse
    options:
      show_source: true

## Usage Examples

### Work with survey responses

```python
responses = client.survey_responses.list(object_id="don:core:...", limit=10)

for survey_response in responses.survey_responses:
    print(survey_response.id)
    print(survey_response.response)
```