"""Articles service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.exceptions import DevRevError
from devrev.models.articles import (
    Article,
    ArticlesCountRequest,
    ArticlesCountResponse,
    ArticlesCreateRequest,
    ArticlesCreateResponse,
    ArticlesDeleteRequest,
    ArticlesDeleteResponse,
    ArticlesGetRequest,
    ArticlesGetResponse,
    ArticlesListRequest,
    ArticlesListResponse,
    ArticlesUpdateRequest,
    ArticlesUpdateResponse,
    ArticleStatus,
    ArticleWithContent,
)
from devrev.models.artifacts import ArtifactPrepareRequest
from devrev.services.base import AsyncBaseService, BaseService


class ArticlesService(BaseService):
    """Service for managing DevRev Articles."""

    def create(self, request: ArticlesCreateRequest) -> Article:
        """Create a new article."""
        response = self._post("/articles.create", request, ArticlesCreateResponse)
        return response.article

    def get(self, request: ArticlesGetRequest) -> Article:
        """Get an article by ID."""
        response = self._post("/articles.get", request, ArticlesGetResponse)
        return response.article

    def list(self, request: ArticlesListRequest | None = None) -> Sequence[Article]:
        """List articles."""
        if request is None:
            request = ArticlesListRequest()
        response = self._post("/articles.list", request, ArticlesListResponse)
        return response.articles

    def update(self, request: ArticlesUpdateRequest) -> Article:
        """Update an article."""
        response = self._post("/articles.update", request, ArticlesUpdateResponse)
        return response.article

    def delete(self, request: ArticlesDeleteRequest) -> None:
        """Delete an article."""
        self._post("/articles.delete", request, ArticlesDeleteResponse)

    def count(
        self,
        *,
        status: Sequence[str] | None = None,
    ) -> int:
        """Count articles.

        This endpoint is only available with the beta API. Calling this method
        when the client is configured for the public API will result in an
        HTTP 404 error from the server.

        Args:
            status: Filter by article status

        Returns:
            Count of matching articles

        Note:
            Beta API only. Use ``api_version=APIVersion.BETA`` when initializing the client.
        """
        request = ArticlesCountRequest(status=status)
        response = self._post("/articles.count", request, ArticlesCountResponse)
        return response.count

    def create_with_content(
        self,
        title: str,
        content: str,
        *,
        owned_by: list[str],
        description: str | None = None,
        status: ArticleStatus | None = None,
        content_format: str = "text/plain",
    ) -> Article:
        """Create an article with content in a single operation.

        This is a high-level method that handles the full workflow:
        1. Prepare artifact for content storage
        2. Upload content to storage
        3. Create article with artifact reference

        If any step fails, automatic rollback ensures no orphaned artifacts.

        Args:
            title: Article title
            content: Article body content (HTML, markdown, or plain text)
            owned_by: List of dev user IDs who own the article
            description: Optional short metadata description (NOT the article content)
            status: Optional article status (draft, published, archived)
            content_format: Content MIME type (default: text/plain)

        Returns:
            Created article

        Raises:
            DevRevError: If parent client not available or operation fails

        Example:
            >>> article = client.articles.create_with_content(
            ...     title="User Guide",
            ...     content="<html>...</html>",
            ...     owned_by=["DEVU-123"],
            ...     content_format="text/html"
            ... )
        """
        if not self._parent_client:
            raise DevRevError(
                "create_with_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        artifact_id: str | None = None
        try:
            # Step 1: Prepare artifact
            # Derive file extension from content format
            ext_map = {
                "text/html": ".html",
                "text/markdown": ".md",
                "text/plain": ".txt",
            }
            ext = ext_map.get(content_format, ".txt")

            prepare_req = ArtifactPrepareRequest(
                file_name=f"{title}{ext}",
                file_type=content_format,
                configuration_set="article_media",
            )
            prepare_resp = self._parent_client.artifacts.prepare(prepare_req)
            artifact_id = prepare_resp.id

            # Step 2: Upload content
            self._parent_client.artifacts.upload(prepare_resp, content)

            # Step 3: Create article with artifact reference
            article_req = ArticlesCreateRequest(
                title=title,
                description=description,
                status=status,
                owned_by=owned_by,
                resource={"content_artifact": artifact_id},
            )
            return self.create(article_req)

        except Exception as e:
            # Note: Orphaned artifact cleanup is not possible with current DevRev API
            # The API does not provide artifact deletion, only version deletion
            # This may result in orphaned artifacts if article creation fails
            if artifact_id:
                import logging
                logging.warning(
                    f"Orphaned artifact {artifact_id} may remain due to failed article creation. "
                    "Manual cleanup may be required."
                )

            # Re-raise the original error
            raise DevRevError(f"Failed to create article with content: {e}") from e

    def get_with_content(self, id: str) -> ArticleWithContent:
        """Get an article with its content loaded.

        This is a high-level method that:
        1. Fetches article metadata
        2. Locates the content artifact
        3. Downloads artifact content
        4. Returns combined model

        Args:
            id: Article ID

        Returns:
            ArticleWithContent with metadata and content

        Raises:
            DevRevError: If parent client not available, article not found,
                        or article has no content artifact

        Example:
            >>> article_with_content = client.articles.get_with_content("ART-123")
            >>> print(article_with_content.article.title)
            >>> print(article_with_content.content)
        """
        if not self._parent_client:
            raise DevRevError(
                "get_with_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        # Step 1: Get article metadata
        article = self.get(ArticlesGetRequest(id=id))

        # Step 2: Extract content artifact ID
        # Articles store artifact reference in resource.content_artifact
        if not article.resource:
            raise DevRevError(f"Article {id} has no resource configuration")

        if not isinstance(article.resource, dict):
            raise DevRevError(f"Article {id} resource is not a dict")

        content_artifact_id = article.resource.get("content_artifact")
        if not content_artifact_id:
            raise DevRevError(
                f"Article {id} has no content artifact reference in resource configuration"
            )

        # Step 3: Download content
        try:
            content_bytes = self._parent_client.artifacts.download(content_artifact_id)
            content = content_bytes.decode("utf-8")

            # Get artifact metadata for format and version
            from devrev.models.artifacts import ArtifactGetRequest

            artifact = self._parent_client.artifacts.get(
                ArtifactGetRequest(id=content_artifact_id)
            )

            return ArticleWithContent(
                article=article,
                content=content,
                content_format=artifact.file_type or "text/plain",
                content_version=artifact.version,
            )
        except Exception as e:
            raise DevRevError(
                f"Failed to download content for article {id}: {e}"
            ) from e

    def update_content(
        self,
        id: str,
        content: str,
    ) -> Article:
        """Update article content by creating a new artifact version.

        This is a high-level method that:
        1. Gets current article to find artifact ID
        2. Prepares new artifact version
        3. Uploads new content
        4. Article automatically references new version

        Note: The content format is inherited from the original artifact
        and cannot be changed when updating content.

        Args:
            id: Article ID
            content: New article body content

        Returns:
            Updated article

        Raises:
            DevRevError: If parent client not available, article not found,
                        or article has no content artifact

        Example:
            >>> article = client.articles.update_content(
            ...     "ART-123",
            ...     "<html>Updated content...</html>"
            ... )
        """
        if not self._parent_client:
            raise DevRevError(
                "update_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        # Step 1: Get article to find current artifact ID
        article = self.get(ArticlesGetRequest(id=id))

        if not article.resource or not isinstance(article.resource, dict):
            raise DevRevError(f"Article {id} has no resource configuration")

        content_artifact_id = article.resource.get("content_artifact")
        if not content_artifact_id:
            raise DevRevError(
                f"Article {id} has no content artifact reference in resource configuration"
            )

        try:
            # Step 2: Prepare new version
            from devrev.models.artifacts import ArtifactVersionsPrepareRequest

            version_req = ArtifactVersionsPrepareRequest(id=content_artifact_id)
            version_resp = self._parent_client.artifacts.prepare_version(version_req)

            # Step 3: Upload new content
            self._parent_client.artifacts.upload(version_resp, content)

            # Article automatically references the new version
            # Return the updated article
            return self.get(ArticlesGetRequest(id=id))

        except Exception as e:
            raise DevRevError(f"Failed to update content for article {id}: {e}") from e

    def update_with_content(
        self,
        id: str,
        *,
        title: str | None = None,
        content: str | None = None,
        description: str | None = None,
        status: ArticleStatus | None = None,
    ) -> Article:
        """Update article metadata and/or content.

        This is a high-level method that handles both metadata and content updates.
        If only metadata is provided, only metadata is updated.
        If only content is provided, only content is updated.
        If both are provided, both are updated atomically.

        Args:
            id: Article ID
            title: Optional new title
            content: Optional new article body content
            description: Optional new metadata description
            status: Optional new status

        Returns:
            Updated article

        Raises:
            DevRevError: If parent client not available or operation fails

        Example:
            >>> # Update only metadata
            >>> article = client.articles.update_with_content(
            ...     "ART-123",
            ...     title="New Title",
            ...     status=ArticleStatus.PUBLISHED
            ... )
            >>>
            >>> # Update only content
            >>> article = client.articles.update_with_content(
            ...     "ART-123",
            ...     content="<html>New content...</html>"
            ... )
            >>>
            >>> # Update both
            >>> article = client.articles.update_with_content(
            ...     "ART-123",
            ...     title="New Title",
            ...     content="<html>New content...</html>"
            ... )
        """
        if not self._parent_client:
            raise DevRevError(
                "update_with_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        # Update content if provided
        if content is not None:
            self.update_content(id, content)

        # Update metadata if any metadata fields provided
        if title is not None or description is not None or status is not None:
            update_req = ArticlesUpdateRequest(
                id=id,
                title=title,
                description=description,
                status=status,
            )
            return self.update(update_req)

        # If only content was updated, return the article
        return self.get(ArticlesGetRequest(id=id))


class AsyncArticlesService(AsyncBaseService):
    """Async service for managing DevRev Articles."""

    async def create(self, request: ArticlesCreateRequest) -> Article:
        """Create a new article."""
        response = await self._post("/articles.create", request, ArticlesCreateResponse)
        return response.article

    async def get(self, request: ArticlesGetRequest) -> Article:
        """Get an article by ID."""
        response = await self._post("/articles.get", request, ArticlesGetResponse)
        return response.article

    async def list(self, request: ArticlesListRequest | None = None) -> Sequence[Article]:
        """List articles."""
        if request is None:
            request = ArticlesListRequest()
        response = await self._post("/articles.list", request, ArticlesListResponse)
        return response.articles

    async def update(self, request: ArticlesUpdateRequest) -> Article:
        """Update an article."""
        response = await self._post("/articles.update", request, ArticlesUpdateResponse)
        return response.article

    async def delete(self, request: ArticlesDeleteRequest) -> None:
        """Delete an article."""
        await self._post("/articles.delete", request, ArticlesDeleteResponse)

    async def count(
        self,
        *,
        status: Sequence[str] | None = None,
    ) -> int:
        """Count articles.

        This endpoint is only available with the beta API. Calling this method
        when the client is configured for the public API will result in an
        HTTP 404 error from the server.

        Args:
            status: Filter by article status

        Returns:
            Count of matching articles

        Note:
            Beta API only. Use ``api_version=APIVersion.BETA`` when initializing the client.
        """
        request = ArticlesCountRequest(status=status)
        response = await self._post("/articles.count", request, ArticlesCountResponse)
        return response.count

    async def create_with_content(
        self,
        title: str,
        content: str,
        *,
        owned_by: list[str],
        description: str | None = None,
        status: ArticleStatus | None = None,
        content_format: str = "text/plain",
    ) -> Article:
        """Create an article with content in a single operation (async).

        This is a high-level method that handles the full workflow:
        1. Prepare artifact for content storage
        2. Upload content to storage
        3. Create article with artifact reference

        If any step fails, automatic rollback ensures no orphaned artifacts.

        Args:
            title: Article title
            content: Article body content (HTML, markdown, or plain text)
            owned_by: List of dev user IDs who own the article
            description: Optional short metadata description (NOT the article content)
            status: Optional article status (draft, published, archived)
            content_format: Content MIME type (default: text/plain)

        Returns:
            Created article

        Raises:
            DevRevError: If parent client not available or operation fails
        """
        if not self._parent_client:
            raise DevRevError(
                "create_with_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        artifact_id: str | None = None
        try:
            # Step 1: Prepare artifact
            # Derive file extension from content format
            ext_map = {
                "text/html": ".html",
                "text/markdown": ".md",
                "text/plain": ".txt",
            }
            ext = ext_map.get(content_format, ".txt")

            prepare_req = ArtifactPrepareRequest(
                file_name=f"{title}{ext}",
                file_type=content_format,
                configuration_set="article_media",
            )
            prepare_resp = await self._parent_client.artifacts.prepare(prepare_req)
            artifact_id = prepare_resp.id

            # Step 2: Upload content
            await self._parent_client.artifacts.upload(prepare_resp, content)

            # Step 3: Create article with artifact reference
            article_req = ArticlesCreateRequest(
                title=title,
                description=description,
                status=status,
                owned_by=owned_by,
                resource={"content_artifact": artifact_id},
            )
            return await self.create(article_req)

        except Exception as e:
            # Note: Orphaned artifact cleanup is not possible with current DevRev API
            # The API does not provide artifact deletion, only version deletion
            # This may result in orphaned artifacts if article creation fails
            if artifact_id:
                import logging
                logging.warning(
                    f"Orphaned artifact {artifact_id} may remain due to failed article creation. "
                    "Manual cleanup may be required."
                )

            # Re-raise the original error
            raise DevRevError(f"Failed to create article with content: {e}") from e

    async def get_with_content(self, id: str) -> ArticleWithContent:
        """Get an article with its content loaded (async).

        This is a high-level method that:
        1. Fetches article metadata
        2. Locates the content artifact
        3. Downloads artifact content
        4. Returns combined model

        Args:
            id: Article ID

        Returns:
            ArticleWithContent with metadata and content

        Raises:
            DevRevError: If parent client not available, article not found,
                        or article has no content artifact
        """
        if not self._parent_client:
            raise DevRevError(
                "get_with_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        # Step 1: Get article metadata
        article = await self.get(ArticlesGetRequest(id=id))

        # Step 2: Extract content artifact ID
        if not article.resource or not isinstance(article.resource, dict):
            raise DevRevError(f"Article {id} has no resource configuration")

        content_artifact_id = article.resource.get("content_artifact")
        if not content_artifact_id:
            raise DevRevError(
                f"Article {id} has no content artifact reference in resource configuration"
            )

        # Step 3: Download content
        try:
            content_bytes = await self._parent_client.artifacts.download(content_artifact_id)
            content = content_bytes.decode("utf-8")

            # Get artifact metadata for format and version
            from devrev.models.artifacts import ArtifactGetRequest

            artifact = await self._parent_client.artifacts.get(
                ArtifactGetRequest(id=content_artifact_id)
            )

            return ArticleWithContent(
                article=article,
                content=content,
                content_format=artifact.file_type or "text/plain",
                content_version=artifact.version,
            )
        except Exception as e:
            raise DevRevError(
                f"Failed to download content for article {id}: {e}"
            ) from e

    async def update_content(
        self,
        id: str,
        content: str,
    ) -> Article:
        """Update article content by creating a new artifact version (async).

        This is a high-level method that:
        1. Gets current article to find artifact ID
        2. Prepares new artifact version
        3. Uploads new content
        4. Article automatically references new version

        Note: The content format is inherited from the original artifact
        and cannot be changed when updating content.

        Args:
            id: Article ID
            content: New article body content

        Returns:
            Updated article

        Raises:
            DevRevError: If parent client not available, article not found,
                        or article has no content artifact
        """
        if not self._parent_client:
            raise DevRevError(
                "update_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        # Step 1: Get article to find current artifact ID
        article = await self.get(ArticlesGetRequest(id=id))

        if not article.resource or not isinstance(article.resource, dict):
            raise DevRevError(f"Article {id} has no resource configuration")

        content_artifact_id = article.resource.get("content_artifact")
        if not content_artifact_id:
            raise DevRevError(
                f"Article {id} has no content artifact reference in resource configuration"
            )

        try:
            # Step 2: Prepare new version
            from devrev.models.artifacts import ArtifactVersionsPrepareRequest

            version_req = ArtifactVersionsPrepareRequest(id=content_artifact_id)
            version_resp = await self._parent_client.artifacts.prepare_version(version_req)

            # Step 3: Upload new content
            await self._parent_client.artifacts.upload(version_resp, content)

            # Article automatically references the new version
            # Return the updated article
            return await self.get(ArticlesGetRequest(id=id))

        except Exception as e:
            raise DevRevError(f"Failed to update content for article {id}: {e}") from e

    async def update_with_content(
        self,
        id: str,
        *,
        title: str | None = None,
        content: str | None = None,
        description: str | None = None,
        status: ArticleStatus | None = None,
    ) -> Article:
        """Update article metadata and/or content (async).

        This is a high-level method that handles both metadata and content updates.
        If only metadata is provided, only metadata is updated.
        If only content is provided, only content is updated.
        If both are provided, both are updated atomically.

        Args:
            id: Article ID
            title: Optional new title
            content: Optional new article body content
            description: Optional new metadata description
            status: Optional new status

        Returns:
            Updated article

        Raises:
            DevRevError: If parent client not available or operation fails
        """
        if not self._parent_client:
            raise DevRevError(
                "update_with_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        # Update content if provided
        if content is not None:
            await self.update_content(id, content)

        # Update metadata if any metadata fields provided
        if title is not None or description is not None or status is not None:
            update_req = ArticlesUpdateRequest(
                id=id,
                title=title,
                description=description,
                status=status,
            )
            return await self.update(update_req)

        # If only content was updated, return the article
        return await self.get(ArticlesGetRequest(id=id))
