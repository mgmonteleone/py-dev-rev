# Flask Integration Example

A Flask web application demonstrating DevRev SDK integration.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set your API token:
   ```bash
   export DEVREV_API_TOKEN="your-token"
   ```

3. Run the server:
   ```bash
   flask run
   # or
   python app.py
   ```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/accounts` | List accounts |
| GET | `/works/<work_id>` | Get a work item |
| POST | `/tickets` | Create a ticket |

## Key Features

- **Request-scoped client** using Flask's `g` object
- **Proper cleanup** with `teardown_appcontext`
- **Error handling** with JSON responses

