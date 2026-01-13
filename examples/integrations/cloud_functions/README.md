# Cloud Functions Integration Example

Google Cloud Functions demonstrating DevRev SDK integration.

## Setup

1. Install dependencies locally for testing:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your API token:
   ```bash
   export DEVREV_API_TOKEN="your-token"
   ```

## Local Testing

```bash
# Run locally with functions-framework
functions-framework --target=list_accounts --debug

# Test with curl
curl http://localhost:8080
```

## Deployment

```bash
# Deploy webhook handler
gcloud functions deploy handle_webhook \
    --runtime python312 \
    --trigger-http \
    --allow-unauthenticated \
    --set-secrets=DEVREV_API_TOKEN=devrev-token:latest

# Deploy list_accounts
gcloud functions deploy list_accounts \
    --runtime python312 \
    --trigger-http \
    --set-secrets=DEVREV_API_TOKEN=devrev-token:latest
```

## Functions

| Function | Description |
|----------|-------------|
| `handle_webhook` | Process DevRev webhooks |
| `list_accounts` | List DevRev accounts |
| `create_ticket` | Create a support ticket |

## Security

For production:

1. Store API token in Secret Manager
2. Use `--set-secrets` flag for deployment
3. Remove `--allow-unauthenticated` and use IAM authentication
4. Verify webhook signatures

