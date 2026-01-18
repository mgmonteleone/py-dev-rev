# Recommendations Service

AI-powered recommendations for chat completions and suggested replies.

!!! info "Beta API Only"
    This service is only available when using `APIVersion.BETA`. See [Beta API Overview](index.md) for setup instructions.

## RecommendationsService

::: devrev.services.recommendations.RecommendationsService
    options:
      show_source: true
      members:
        - chat_completions
        - get_reply

## AsyncRecommendationsService

::: devrev.services.recommendations.AsyncRecommendationsService
    options:
      show_source: true

## Usage Examples

### Chat Completions

Generate AI-powered chat responses based on conversation context:

```python
from devrev import DevRevClient, APIVersion
from devrev.models.recommendations import ChatCompletionRequest

client = DevRevClient(api_version=APIVersion.BETA)

request = ChatCompletionRequest(
    messages=[
        {"role": "user", "content": "How do I integrate the API?"},
    ],
    context={
        "product": "DevRev API",
        "user_tier": "enterprise",
    },
)

response = client.recommendations.chat_completions(request)
print(f"AI Response: {response.message}")
```

### Get Reply Recommendations

Get AI-suggested replies for a specific object (ticket, conversation, etc.):

```python
from devrev.models.recommendations import GetReplyRequest

request = GetReplyRequest(
    object_id="don:core:dvrv-us-1:devo/1:conversation/123",
    context={
        "tone": "professional",
        "length": "concise",
    },
)

response = client.recommendations.get_reply(request)
print(f"Suggested reply: {response.reply}")
```

### Multi-Turn Conversations

```python
from devrev.models.recommendations import ChatCompletionRequest

# Build conversation history
messages = [
    {"role": "user", "content": "What's the API rate limit?"},
    {"role": "assistant", "content": "The API rate limit is 1000 requests per hour."},
    {"role": "user", "content": "Can I increase it?"},
]

request = ChatCompletionRequest(messages=messages)
response = client.recommendations.chat_completions(request)
print(response.message)
```

### Context-Aware Recommendations

```python
from devrev.models.recommendations import GetReplyRequest

# Provide rich context for better recommendations
request = GetReplyRequest(
    object_id="don:core:dvrv-us-1:devo/1:ticket/456",
    context={
        "customer_tier": "enterprise",
        "issue_severity": "high",
        "product_area": "authentication",
        "previous_interactions": 5,
    },
)

response = client.recommendations.get_reply(request)
```

### Async Usage

```python
import asyncio
from devrev import AsyncDevRevClient, APIVersion
from devrev.models.recommendations import ChatCompletionRequest

async def main():
    async with AsyncDevRevClient(api_version=APIVersion.BETA) as client:
        # Get chat completion
        request = ChatCompletionRequest(
            messages=[
                {"role": "user", "content": "Explain webhooks"},
            ]
        )
        response = await client.recommendations.chat_completions(request)
        print(response.message)

asyncio.run(main())
```

## Related Models

### ChatCompletionRequest

Request model for chat completions:

- `messages` - List of conversation messages with role and content
- `context` - Optional context dictionary for better recommendations
- `max_tokens` - Maximum tokens in response
- `temperature` - Randomness in responses (0-1)

### ChatCompletionResponse

Response model for chat completions:

- `message` - AI-generated message
- `confidence` - Confidence score (0-1)
- `metadata` - Additional metadata about the response

### GetReplyRequest

Request model for reply recommendations:

- `object_id` - ID of the object to generate a reply for
- `context` - Optional context for personalization

### GetReplyResponse

Response model for reply recommendations:

- `reply` - Suggested reply text
- `confidence` - Confidence score
- `alternatives` - Alternative reply suggestions

## Best Practices

1. **Provide context** - Include relevant context for more accurate recommendations
2. **Review AI output** - Always review AI-generated content before sending to customers
3. **Maintain conversation history** - Include previous messages for multi-turn conversations
4. **Set appropriate temperature** - Lower values (0.2-0.4) for factual responses, higher (0.7-0.9) for creative
5. **Handle low confidence** - Check confidence scores and provide fallbacks for low-confidence responses
6. **Respect rate limits** - Cache recommendations when possible to avoid excessive API calls

## Use Cases

### Customer Support Automation

```python
# Get AI-suggested reply for a support ticket
request = GetReplyRequest(
    object_id="don:core:dvrv-us-1:devo/1:ticket/789",
    context={
        "customer_sentiment": "frustrated",
        "issue_type": "billing",
        "priority": "high",
    },
)

response = client.recommendations.get_reply(request)
# Review and send the suggested reply
```

### Knowledge Base Assistant

```python
# Use chat completions as a knowledge base assistant
request = ChatCompletionRequest(
    messages=[
        {"role": "user", "content": "How do I configure SSO?"},
    ],
    context={
        "knowledge_base": "enterprise_docs",
    },
)

response = client.recommendations.chat_completions(request)
```

### Agent Assistance

```python
# Provide real-time suggestions to support agents
request = GetReplyRequest(
    object_id="don:core:dvrv-us-1:devo/1:conversation/999",
    context={
        "agent_experience": "junior",
        "suggest_tone": "empathetic",
    },
)

response = client.recommendations.get_reply(request)
# Display suggestion to agent
```

