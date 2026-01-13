"""SLAs service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.slas import (
    Sla,
    SlasCreateRequest,
    SlasCreateResponse,
    SlasGetRequest,
    SlasGetResponse,
    SlasListRequest,
    SlasListResponse,
    SlasTransitionRequest,
    SlasTransitionResponse,
    SlasUpdateRequest,
    SlasUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class SlasService(BaseService):
    """Service for managing DevRev SLAs."""

    def create(self, request: SlasCreateRequest) -> Sla:
        """Create a new SLA."""
        response = self._post("/slas.create", request, SlasCreateResponse)
        return response.sla

    def get(self, request: SlasGetRequest) -> Sla:
        """Get an SLA by ID."""
        response = self._post("/slas.get", request, SlasGetResponse)
        return response.sla

    def list(self, request: SlasListRequest | None = None) -> Sequence[Sla]:
        """List SLAs."""
        if request is None:
            request = SlasListRequest()
        response = self._post("/slas.list", request, SlasListResponse)
        return response.slas

    def update(self, request: SlasUpdateRequest) -> Sla:
        """Update an SLA."""
        response = self._post("/slas.update", request, SlasUpdateResponse)
        return response.sla

    def transition(self, request: SlasTransitionRequest) -> Sla:
        """Transition an SLA status."""
        response = self._post("/slas.transition", request, SlasTransitionResponse)
        return response.sla


class AsyncSlasService(AsyncBaseService):
    """Async service for managing DevRev SLAs."""

    async def create(self, request: SlasCreateRequest) -> Sla:
        """Create a new SLA."""
        response = await self._post("/slas.create", request, SlasCreateResponse)
        return response.sla

    async def get(self, request: SlasGetRequest) -> Sla:
        """Get an SLA by ID."""
        response = await self._post("/slas.get", request, SlasGetResponse)
        return response.sla

    async def list(self, request: SlasListRequest | None = None) -> Sequence[Sla]:
        """List SLAs."""
        if request is None:
            request = SlasListRequest()
        response = await self._post("/slas.list", request, SlasListResponse)
        return response.slas

    async def update(self, request: SlasUpdateRequest) -> Sla:
        """Update an SLA."""
        response = await self._post("/slas.update", request, SlasUpdateResponse)
        return response.sla

    async def transition(self, request: SlasTransitionRequest) -> Sla:
        """Transition an SLA status."""
        response = await self._post("/slas.transition", request, SlasTransitionResponse)
        return response.sla
