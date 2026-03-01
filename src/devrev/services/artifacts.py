"""Artifacts service for DevRev SDK."""

from __future__ import annotations

import httpx

from devrev.exceptions import DevRevError
from devrev.models.artifacts import (
    Artifact,
    ArtifactGetRequest,
    ArtifactGetResponse,
    ArtifactListRequest,
    ArtifactListResponse,
    ArtifactLocateRequest,
    ArtifactLocateResponse,
    ArtifactPrepareRequest,
    ArtifactPrepareResponse,
    ArtifactVersionsDeleteRequest,
    ArtifactVersionsDeleteResponse,
    ArtifactVersionsPrepareRequest,
    ArtifactVersionsPrepareResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class ArtifactsService(BaseService):
    """Service for managing DevRev Artifacts."""

    def prepare(self, request: ArtifactPrepareRequest) -> ArtifactPrepareResponse:
        """Prepare an artifact for upload.

        This creates an artifact record and returns an upload URL and form data
        for uploading the actual file content to storage.

        Args:
            request: Artifact preparation request with file name and optional type

        Returns:
            ArtifactPrepareResponse with artifact ID, upload URL, and form data

        Example:
            >>> from devrev.models.artifacts import ArtifactPrepareRequest
            >>> request = ArtifactPrepareRequest(
            ...     file_name="article.html",
            ...     file_type="text/html",
            ...     configuration_set="article_media"
            ... )
            >>> response = client.artifacts.prepare(request)
            >>> artifact_id = response.id
            >>> upload_url = response.url
        """
        return self._post("/artifacts.prepare", request, ArtifactPrepareResponse)

    def upload(self, prepare_response: ArtifactPrepareResponse, content: bytes | str) -> str:
        """Upload content to a prepared artifact.

        This is a helper method that uploads content to the URL returned by prepare().

        Args:
            prepare_response: Response from prepare() call
            content: File content as bytes or string

        Returns:
            Artifact ID

        Raises:
            DevRevError: If upload fails

        Example:
            >>> prepare_resp = client.artifacts.prepare(...)
            >>> artifact_id = client.artifacts.upload(prepare_resp, b"<html>...</html>")
        """
        # Convert string to bytes if necessary
        if isinstance(content, str):
            content = content.encode("utf-8")

        # Prepare form data for multipart upload
        form_data = {item.key: item.value for item in prepare_response.form_data}

        try:
            # Upload to the storage URL (typically S3)
            response = httpx.post(
                prepare_response.url,
                data=form_data,
                files={"file": content},
                timeout=60.0,
            )
            response.raise_for_status()
            return prepare_response.id
        except httpx.HTTPError as e:
            raise DevRevError(f"Failed to upload artifact content: {e}") from e

    def get(self, request: ArtifactGetRequest) -> Artifact:
        """Get artifact metadata.

        Args:
            request: Get request with artifact ID and optional version

        Returns:
            Artifact metadata

        Example:
            >>> from devrev.models.artifacts import ArtifactGetRequest
            >>> request = ArtifactGetRequest(id="ARTIFACT-12345")
            >>> artifact = client.artifacts.get(request)
        """
        response = self._post("/artifacts.get", request, ArtifactGetResponse)
        return response.artifact

    def locate(self, request: ArtifactLocateRequest) -> str:
        """Get download URL for an artifact.

        Args:
            request: Locate request with artifact ID and optional version

        Returns:
            Download URL (typically a signed S3 URL)

        Example:
            >>> from devrev.models.artifacts import ArtifactLocateRequest
            >>> request = ArtifactLocateRequest(id="ARTIFACT-12345")
            >>> url = client.artifacts.locate(request)
        """
        response = self._post("/artifacts.locate", request, ArtifactLocateResponse)
        return response.url

    def download(self, artifact_id: str, version: str | None = None) -> bytes:
        """Download artifact content.

        This is a helper method that combines locate() and fetching the content.

        Args:
            artifact_id: Artifact ID to download
            version: Optional specific version to download

        Returns:
            Artifact content as bytes

        Raises:
            DevRevError: If download fails

        Example:
            >>> content = client.artifacts.download("ARTIFACT-12345")
        """
        # Get download URL
        locate_request = ArtifactLocateRequest(id=artifact_id, version=version)
        url = self.locate(locate_request)

        try:
            # Download content
            response = httpx.get(url, timeout=60.0)
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            raise DevRevError(f"Failed to download artifact content: {e}") from e

    def list_for_parent(self, parent_id: str) -> list[Artifact]:
        """List artifacts attached to a parent object.

        Args:
            parent_id: ID of parent object (e.g., article ID)

        Returns:
            List of artifacts

        Example:
            >>> artifacts = client.artifacts.list_for_parent("ART-12345")
        """
        request = ArtifactListRequest(parent_id=parent_id)
        response = self._post("/artifacts.list", request, ArtifactListResponse)
        return response.artifacts

    def prepare_version(
        self, request: ArtifactVersionsPrepareRequest
    ) -> ArtifactVersionsPrepareResponse:
        """Prepare a new version for an existing artifact.

        Args:
            request: Version prepare request with artifact ID

        Returns:
            Preparation response with upload URL and form data

        Example:
            >>> from devrev.models.artifacts import ArtifactVersionsPrepareRequest
            >>> request = ArtifactVersionsPrepareRequest(id="ARTIFACT-12345")
            >>> response = client.artifacts.prepare_version(request)
            >>> # Upload new version using response.url and response.form_data
        """
        return self._post(
            "/artifacts.versions.prepare", request, ArtifactVersionsPrepareResponse
        )

    def delete_version(self, request: ArtifactVersionsDeleteRequest) -> None:
        """Permanently delete a version of an artifact.

        Args:
            request: Delete request with artifact ID and version

        Example:
            >>> from devrev.models.artifacts import ArtifactVersionsDeleteRequest
            >>> request = ArtifactVersionsDeleteRequest(
            ...     id="ARTIFACT-12345",
            ...     version="v2"
            ... )
            >>> client.artifacts.delete_version(request)
        """
        self._post("/artifacts.versions.delete", request, ArtifactVersionsDeleteResponse)


class AsyncArtifactsService(AsyncBaseService):
    """Async service for managing DevRev Artifacts."""

    async def prepare(self, request: ArtifactPrepareRequest) -> ArtifactPrepareResponse:
        """Prepare an artifact for upload.

        This creates an artifact record and returns an upload URL and form data
        for uploading the actual file content to storage.

        Args:
            request: Artifact preparation request with file name and optional type

        Returns:
            ArtifactPrepareResponse with artifact ID, upload URL, and form data

        Example:
            >>> from devrev.models.artifacts import ArtifactPrepareRequest
            >>> request = ArtifactPrepareRequest(
            ...     file_name="article.html",
            ...     file_type="text/html",
            ...     configuration_set="article_media"
            ... )
            >>> response = await client.artifacts.prepare(request)
            >>> artifact_id = response.id
            >>> upload_url = response.url
        """
        return await self._post("/artifacts.prepare", request, ArtifactPrepareResponse)

    async def upload(
        self, prepare_response: ArtifactPrepareResponse, content: bytes | str
    ) -> str:
        """Upload content to a prepared artifact.

        This is a helper method that uploads content to the URL returned by prepare().

        Args:
            prepare_response: Response from prepare() call
            content: File content as bytes or string

        Returns:
            Artifact ID

        Raises:
            DevRevError: If upload fails

        Example:
            >>> prepare_resp = await client.artifacts.prepare(...)
            >>> artifact_id = await client.artifacts.upload(prepare_resp, b"<html>...</html>")
        """
        # Convert string to bytes if necessary
        if isinstance(content, str):
            content = content.encode("utf-8")

        # Prepare form data for multipart upload
        form_data = {item.key: item.value for item in prepare_response.form_data}

        try:
            # Upload to the storage URL (typically S3)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    prepare_response.url,
                    data=form_data,
                    files={"file": content},
                    timeout=60.0,
                )
                response.raise_for_status()
            return prepare_response.id
        except httpx.HTTPError as e:
            raise DevRevError(f"Failed to upload artifact content: {e}") from e

    async def get(self, request: ArtifactGetRequest) -> Artifact:
        """Get artifact metadata.

        Args:
            request: Get request with artifact ID and optional version

        Returns:
            Artifact metadata

        Example:
            >>> from devrev.models.artifacts import ArtifactGetRequest
            >>> request = ArtifactGetRequest(id="ARTIFACT-12345")
            >>> artifact = await client.artifacts.get(request)
        """
        response = await self._post("/artifacts.get", request, ArtifactGetResponse)
        return response.artifact

    async def locate(self, request: ArtifactLocateRequest) -> str:
        """Get download URL for an artifact.

        Args:
            request: Locate request with artifact ID and optional version

        Returns:
            Download URL (typically a signed S3 URL)

        Example:
            >>> from devrev.models.artifacts import ArtifactLocateRequest
            >>> request = ArtifactLocateRequest(id="ARTIFACT-12345")
            >>> url = await client.artifacts.locate(request)
        """
        response = await self._post("/artifacts.locate", request, ArtifactLocateResponse)
        return response.url

    async def download(self, artifact_id: str, version: str | None = None) -> bytes:
        """Download artifact content.

        This is a helper method that combines locate() and fetching the content.

        Args:
            artifact_id: Artifact ID to download
            version: Optional specific version to download

        Returns:
            Artifact content as bytes

        Raises:
            DevRevError: If download fails

        Example:
            >>> content = await client.artifacts.download("ARTIFACT-12345")
        """
        # Get download URL
        locate_request = ArtifactLocateRequest(id=artifact_id, version=version)
        url = await self.locate(locate_request)

        try:
            # Download content
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=60.0)
                response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            raise DevRevError(f"Failed to download artifact content: {e}") from e

    async def list_for_parent(self, parent_id: str) -> list[Artifact]:
        """List artifacts attached to a parent object.

        Args:
            parent_id: ID of parent object (e.g., article ID)

        Returns:
            List of artifacts

        Example:
            >>> artifacts = await client.artifacts.list_for_parent("ART-12345")
        """
        request = ArtifactListRequest(parent_id=parent_id)
        response = await self._post("/artifacts.list", request, ArtifactListResponse)
        return response.artifacts

    async def prepare_version(
        self, request: ArtifactVersionsPrepareRequest
    ) -> ArtifactVersionsPrepareResponse:
        """Prepare a new version for an existing artifact.

        Args:
            request: Version prepare request with artifact ID

        Returns:
            Preparation response with upload URL and form data

        Example:
            >>> from devrev.models.artifacts import ArtifactVersionsPrepareRequest
            >>> request = ArtifactVersionsPrepareRequest(id="ARTIFACT-12345")
            >>> response = await client.artifacts.prepare_version(request)
            >>> # Upload new version using response.url and response.form_data
        """
        return await self._post(
            "/artifacts.versions.prepare", request, ArtifactVersionsPrepareResponse
        )

    async def delete_version(self, request: ArtifactVersionsDeleteRequest) -> None:
        """Permanently delete a version of an artifact.

        Args:
            request: Delete request with artifact ID and version

        Example:
            >>> from devrev.models.artifacts import ArtifactVersionsDeleteRequest
            >>> request = ArtifactVersionsDeleteRequest(
            ...     id="ARTIFACT-12345",
            ...     version="v2"
            ... )
            >>> await client.artifacts.delete_version(request)
        """
        await self._post("/artifacts.versions.delete", request, ArtifactVersionsDeleteResponse)
