# DevRev SDK Examples

Working examples demonstrating the DevRev Python SDK.

## Directory Structure

```
examples/
├── basic/                  # Simple standalone scripts
│   ├── list_accounts.py    # List customer accounts
│   ├── create_work.py      # Create tickets and issues
│   ├── search_users.py     # List dev and rev users
│   ├── async_example.py    # Async client usage
│   ├── pagination.py       # Cursor-based pagination
│   └── error_handling.py   # Error handling patterns
│
└── integrations/           # Framework integrations
    ├── fastapi/            # FastAPI web application
    ├── flask/              # Flask web application
    └── cloud_functions/    # Google Cloud Functions
```

## Quick Start

1. **Install the SDK:**
   ```bash
   pip install py-devrev
   ```

2. **Set your API token:**
   ```bash
   export DEVREV_API_TOKEN="your-token"
   ```

3. **Run an example:**
   ```bash
   cd examples/basic
   python list_accounts.py
   ```

## Basic Examples

Simple scripts demonstrating common operations:

| Script | Description |
|--------|-------------|
| `list_accounts.py` | List customer accounts |
| `create_work.py` | Create tickets and issues |
| `search_users.py` | List dev and rev users |
| `async_example.py` | Concurrent async operations |
| `pagination.py` | Iterate through paginated results |
| `error_handling.py` | Proper error handling |

## Integration Examples

### FastAPI

Modern async web framework:

```bash
cd examples/integrations/fastapi
pip install -r requirements.txt
uvicorn main:app --reload
```

### Flask

Traditional sync web framework:

```bash
cd examples/integrations/flask
pip install -r requirements.txt
flask run
```

### Cloud Functions

Serverless deployment:

```bash
cd examples/integrations/cloud_functions
gcloud functions deploy handle_webhook --runtime python312 --trigger-http
```

## Best Practices

1. **Never hardcode API tokens** - Use environment variables
2. **Handle errors** - Catch specific exceptions
3. **Use async for concurrency** - Better performance for multiple requests
4. **Implement pagination** - Handle large datasets properly
5. **Close clients** - Use context managers or explicit close()

## More Resources

- [Documentation](https://mgmonteleone.github.io/py-dev-rev/)
- [API Reference](https://mgmonteleone.github.io/py-dev-rev/api/)
- [GitHub Repository](https://github.com/mgmonteleone/py-dev-rev)

