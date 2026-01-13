#!/usr/bin/env python3
"""FastAPI application with DevRev SDK.

This example demonstrates integrating the DevRev SDK
with a FastAPI web application.

Run:
    uvicorn main:app --reload
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from devrev import AsyncDevRevClient
from devrev.exceptions import DevRevError, NotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage DevRev client lifecycle."""
    app.state.devrev_client = AsyncDevRevClient()
    yield
    await app.state.devrev_client.close()


app = FastAPI(
    title="DevRev Integration API",
    description="Example FastAPI app with DevRev SDK",
    version="1.0.0",
    lifespan=lifespan,
)


def get_client() -> AsyncDevRevClient:
    """Dependency to get the DevRev client."""
    return app.state.devrev_client


class TicketCreate(BaseModel):
    """Request model for creating a ticket."""

    title: str
    description: str
    part_id: str


class TicketResponse(BaseModel):
    """Response model for a ticket."""

    id: str
    display_id: str | None = None
    title: str


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/accounts")
async def list_accounts(
    limit: int = 10,
    client: AsyncDevRevClient = Depends(get_client),
) -> dict[str, Any]:
    """List DevRev accounts."""
    response = await client.accounts.list(limit=limit)
    return {"accounts": [{"id": a.id, "name": a.display_name} for a in response.accounts]}


@app.get("/works/{work_id}")
async def get_work(
    work_id: str,
    client: AsyncDevRevClient = Depends(get_client),
) -> dict[str, Any]:
    """Get a specific work item."""
    try:
        response = await client.works.get(id=work_id)
        return {
            "id": response.work.id,
            "title": response.work.title,
            "type": response.work.type,
        }
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail="Work not found") from e


@app.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    ticket: TicketCreate,
    client: AsyncDevRevClient = Depends(get_client),
) -> TicketResponse:
    """Create a new support ticket."""
    try:
        response = await client.works.create(
            type="ticket",
            title=ticket.title,
            body=ticket.description,
            applies_to_part=ticket.part_id,
        )
        return TicketResponse(
            id=response.work.id,
            display_id=response.work.display_id,
            title=response.work.title,
        )
    except DevRevError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
