# Integration Examples

Integrate the DevRev SDK with popular frameworks and platforms.

## FastAPI

```python
"""FastAPI application with DevRev SDK."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from devrev import AsyncDevRevClient
from devrev.exceptions import NotFoundError, DevRevError

# Lifespan for client management
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.devrev_client = AsyncDevRevClient()
    yield
    await app.state.devrev_client.close()

app = FastAPI(title="DevRev Integration", lifespan=lifespan)

def get_client() -> AsyncDevRevClient:
    return app.state.devrev_client

class TicketCreate(BaseModel):
    title: str
    description: str
    part_id: str

@app.get("/accounts")
async def list_accounts(
    limit: int = 10,
    client: AsyncDevRevClient = Depends(get_client),
):
    response = await client.accounts.list(limit=limit)
    return {"accounts": [a.model_dump() for a in response.accounts]}

@app.get("/works/{work_id}")
async def get_work(
    work_id: str,
    client: AsyncDevRevClient = Depends(get_client),
):
    try:
        response = await client.works.get(id=work_id)
        return response.work.model_dump()
    except NotFoundError:
        raise HTTPException(404, "Work not found")

@app.post("/tickets")
async def create_ticket(
    ticket: TicketCreate,
    client: AsyncDevRevClient = Depends(get_client),
):
    try:
        response = await client.works.create(
            type="ticket",
            title=ticket.title,
            body=ticket.description,
            applies_to_part=ticket.part_id,
        )
        return {"id": response.work.id}
    except DevRevError as e:
        raise HTTPException(400, str(e))
```

## Flask

```python
"""Flask application with DevRev SDK."""
from flask import Flask, jsonify, request, g
from devrev import DevRevClient
from devrev.exceptions import NotFoundError, DevRevError

app = Flask(__name__)

def get_client() -> DevRevClient:
    if "devrev_client" not in g:
        g.devrev_client = DevRevClient()
    return g.devrev_client

@app.teardown_appcontext
def close_client(error):
    client = g.pop("devrev_client", None)
    if client is not None:
        client.close()

@app.route("/accounts")
def list_accounts():
    client = get_client()
    limit = request.args.get("limit", 10, type=int)
    response = client.accounts.list(limit=limit)
    return jsonify({
        "accounts": [a.model_dump() for a in response.accounts]
    })

@app.route("/works/<work_id>")
def get_work(work_id: str):
    client = get_client()
    try:
        response = client.works.get(id=work_id)
        return jsonify(response.work.model_dump())
    except NotFoundError:
        return jsonify({"error": "Not found"}), 404
```

## Cloud Functions

### Google Cloud Functions

```python
"""Google Cloud Function for DevRev webhook handling."""
import functions_framework
from flask import Request
from devrev import DevRevClient

@functions_framework.http
def handle_webhook(request: Request):
    """Handle incoming DevRev webhook."""
    data = request.get_json()
    event_type = data.get("type")
    
    if event_type == "work.created":
        work = data.get("work", {})
        print(f"New work item: {work.get('title')}")
        
        # Process the webhook
        # Example: Send notification, update database, etc.
        
    return {"status": "ok"}

@functions_framework.http
def list_accounts(request: Request):
    """List DevRev accounts."""
    client = DevRevClient()
    try:
        response = client.accounts.list(limit=10)
        return {
            "accounts": [
                {"id": a.id, "name": a.display_name}
                for a in response.accounts
            ]
        }
    finally:
        client.close()
```

### AWS Lambda

```python
"""AWS Lambda handler for DevRev integration."""
import json
from devrev import DevRevClient
from devrev.exceptions import DevRevError

def handler(event, context):
    """Lambda handler."""
    path = event.get("path", "")
    method = event.get("httpMethod", "GET")
    
    client = DevRevClient()
    
    try:
        if path == "/accounts" and method == "GET":
            response = client.accounts.list(limit=10)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "accounts": [a.model_dump() for a in response.accounts]
                }, default=str),
            }
        
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Not found"}),
        }
    
    except DevRevError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
    
    finally:
        client.close()
```

## Celery Task Queue

```python
"""Celery tasks for DevRev operations."""
from celery import Celery
from devrev import DevRevClient
from devrev.models import WorkType

app = Celery("devrev_tasks", broker="redis://localhost:6379/0")

@app.task
def sync_accounts():
    """Sync accounts from DevRev."""
    client = DevRevClient()
    try:
        cursor = None
        all_accounts = []
        
        while True:
            response = client.accounts.list(cursor=cursor, limit=100)
            all_accounts.extend(response.accounts)
            cursor = response.next_cursor
            if not cursor:
                break
        
        # Process accounts (save to database, etc.)
        return {"synced": len(all_accounts)}
    finally:
        client.close()

@app.task
def create_ticket(title: str, body: str, part_id: str):
    """Create a ticket asynchronously."""
    client = DevRevClient()
    try:
        response = client.works.create(
            type=WorkType.TICKET,
            title=title,
            body=body,
            applies_to_part=part_id,
        )
        return {"id": response.work.id}
    finally:
        client.close()
```

