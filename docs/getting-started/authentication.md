# Authentication

The DevRev Python SDK supports multiple authentication methods. This guide covers all options.

## API Token (Recommended)

The simplest and most common authentication method.

### Get Your API Token

1. Log in to your DevRev dashboard
2. Go to **Settings** → **API Keys**
3. Create a new API key or copy an existing one

### Use Environment Variables (Recommended)

The most secure approach:

```bash
export DEVREV_API_TOKEN="your-api-token-here"
```

```python
from devrev import DevRevClient

# Token is automatically read from environment
client = DevRevClient()
```

### Pass Token Directly

For testing only - avoid in production code:

```python
from devrev import DevRevClient

client = DevRevClient(api_token="your-api-token-here")
```

!!! warning "Security Warning"
    Never hardcode tokens in source code. Always use environment variables or secret management.

## Personal Access Token (PAT)

For individual user authentication:

```bash
export DEVREV_PAT="your-personal-access-token"
```

```python
from devrev import DevRevClient

client = DevRevClient()  # PAT is read from environment
```

## Service Accounts

For automated systems and CI/CD:

```python
from devrev import DevRevClient
import os

client = DevRevClient(
    service_account_id=os.environ["DEVREV_SERVICE_ACCOUNT_ID"],
    service_account_secret=os.environ["DEVREV_SERVICE_ACCOUNT_SECRET"]
)
```

## Environment Variable Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `DEVREV_API_TOKEN` | API token for authentication | Yes* |
| `DEVREV_PAT` | Personal Access Token | Yes* |
| `DEVREV_BASE_URL` | API base URL (default: https://api.devrev.ai) | No |
| `DEVREV_TIMEOUT` | Request timeout in seconds (default: 30) | No |
| `DEVREV_MAX_RETRIES` | Max retry attempts (default: 3) | No |

*One authentication method is required.

## Using .env Files

For local development, use a `.env` file:

```bash title=".env"
# Authentication
DEVREV_API_TOKEN=your-api-token-here

# Optional configuration
DEVREV_TIMEOUT=60
DEVREV_LOG_LEVEL=DEBUG
```

!!! danger "Never Commit .env Files"
    Add `.env` to your `.gitignore` file:
    ```
    # .gitignore
    .env
    .env.local
    ```

## Secret Management in Production

### AWS Secrets Manager

```python
import boto3
from devrev import DevRevClient

def get_devrev_client():
    client = boto3.client("secretsmanager")
    secret = client.get_secret_value(SecretId="devrev/api-token")
    return DevRevClient(api_token=secret["SecretString"])
```

### Google Secret Manager

```python
from google.cloud import secretmanager
from devrev import DevRevClient

def get_devrev_client():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/my-project/secrets/devrev-api-token/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return DevRevClient(api_token=response.payload.data.decode())
```

### HashiCorp Vault

```python
import hvac
from devrev import DevRevClient

def get_devrev_client():
    vault = hvac.Client(url="https://vault.example.com")
    secret = vault.secrets.kv.v2.read_secret_version(path="devrev/api-token")
    return DevRevClient(api_token=secret["data"]["data"]["token"])
```

## Token Security Best Practices

1. **Never commit tokens** - Use environment variables or secret managers
2. **Rotate regularly** - Change tokens periodically
3. **Use minimal permissions** - Create tokens with only needed scopes
4. **Monitor usage** - Check for unusual API activity
5. **Revoke when needed** - Immediately revoke compromised tokens

## Verifying Authentication

Test your authentication:

```python
from devrev import DevRevClient
from devrev.exceptions import AuthenticationError

try:
    client = DevRevClient()
    # Make a simple API call to verify
    accounts = client.accounts.list(limit=1)
    print("✓ Authentication successful!")
except AuthenticationError as e:
    print(f"✗ Authentication failed: {e.message}")
```

## Next Steps

- [Quick Start](quickstart.md) - Make your first API calls
- [Configuration Guide](../guides/configuration.md) - All configuration options
- [Error Handling](../guides/error-handling.md) - Handle authentication errors

