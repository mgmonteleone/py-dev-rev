"""Code Changes service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.code_changes import (
    CodeChange,
    CodeChangesCreateRequest,
    CodeChangesCreateResponse,
    CodeChangesDeleteRequest,
    CodeChangesDeleteResponse,
    CodeChangesGetRequest,
    CodeChangesGetResponse,
    CodeChangesListRequest,
    CodeChangesListResponse,
    CodeChangesUpdateRequest,
    CodeChangesUpdateResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class CodeChangesService(BaseService):
    """Service for managing DevRev Code Changes."""

    def create(self, request: CodeChangesCreateRequest) -> CodeChange:
        """Create a new code change."""
        response = self._post("/code-changes.create", request, CodeChangesCreateResponse)
        return response.code_change

    def get(self, request: CodeChangesGetRequest) -> CodeChange:
        """Get a code change by ID."""
        response = self._post("/code-changes.get", request, CodeChangesGetResponse)
        return response.code_change

    def list(self, request: CodeChangesListRequest | None = None) -> Sequence[CodeChange]:
        """List code changes."""
        if request is None:
            request = CodeChangesListRequest()
        response = self._post("/code-changes.list", request, CodeChangesListResponse)
        return response.code_changes

    def update(self, request: CodeChangesUpdateRequest) -> CodeChange:
        """Update a code change."""
        response = self._post("/code-changes.update", request, CodeChangesUpdateResponse)
        return response.code_change

    def delete(self, request: CodeChangesDeleteRequest) -> None:
        """Delete a code change."""
        self._post("/code-changes.delete", request, CodeChangesDeleteResponse)


class AsyncCodeChangesService(AsyncBaseService):
    """Async service for managing DevRev Code Changes."""

    async def create(self, request: CodeChangesCreateRequest) -> CodeChange:
        """Create a new code change."""
        response = await self._post("/code-changes.create", request, CodeChangesCreateResponse)
        return response.code_change

    async def get(self, request: CodeChangesGetRequest) -> CodeChange:
        """Get a code change by ID."""
        response = await self._post("/code-changes.get", request, CodeChangesGetResponse)
        return response.code_change

    async def list(self, request: CodeChangesListRequest | None = None) -> Sequence[CodeChange]:
        """List code changes."""
        if request is None:
            request = CodeChangesListRequest()
        response = await self._post("/code-changes.list", request, CodeChangesListResponse)
        return response.code_changes

    async def update(self, request: CodeChangesUpdateRequest) -> CodeChange:
        """Update a code change."""
        response = await self._post("/code-changes.update", request, CodeChangesUpdateResponse)
        return response.code_change

    async def delete(self, request: CodeChangesDeleteRequest) -> None:
        """Delete a code change."""
        await self._post("/code-changes.delete", request, CodeChangesDeleteResponse)
