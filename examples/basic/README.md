# Basic Examples

Simple examples demonstrating common DevRev SDK operations.

## Setup

1. Install the SDK:
   ```bash
   pip install devrev-python-sdk
   ```

2. Set your API token:
   ```bash
   export DEVREV_API_TOKEN="your-token"
   ```

## Examples

| Script | Description |
|--------|-------------|
| `list_accounts.py` | List customer accounts |
| `create_work.py` | Create tickets and issues |
| `search_users.py` | List dev and rev users |
| `async_example.py` | Async client with concurrent requests |
| `pagination.py` | Iterate through paginated results |
| `error_handling.py` | Proper error handling patterns |

## Running

```bash
# Run any example
python list_accounts.py
python create_work.py
python async_example.py
```

## Notes

- All examples use environment variables for configuration
- Never hardcode API tokens in your code
- See the [documentation](https://mgmonteleone.github.io/py-dev-rev/) for more details

