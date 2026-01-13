# FastAPI Integration Example

A FastAPI web application demonstrating DevRev SDK integration.

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
   uvicorn main:app --reload
   ```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/accounts` | List accounts |
| GET | `/works/{work_id}` | Get a work item |
| POST | `/tickets` | Create a ticket |

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Features

- **Async client** with proper lifecycle management
- **Dependency injection** for the DevRev client
- **Error handling** with HTTP exceptions
- **Pydantic models** for request/response validation

