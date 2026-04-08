"""Articles service for DevRev SDK."""

from __future__ import annotations

import builtins
import logging
from collections.abc import Sequence

from devrev.exceptions import DevRevError
from devrev.models.articles import (
    Article,
    ArticleAccessLevel,
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
    ArticleStatus,
    ArticlesUpdateRequest,
    ArticlesUpdateRequestAppliesToParts,
    ArticlesUpdateRequestSharedWith,
    ArticlesUpdateRequestTags,
    ArticlesUpdateResponse,
    ArticleType,
    ArticleWithContent,
    SetSharedWithMembership,
)
from devrev.models.artifacts import (
    ArtifactPrepareRequest,
)
from devrev.models.base import SetTagWithValue
from devrev.services.base import AsyncBaseService, BaseService
from devrev.utils.content_converter import (
    CONTENT_FORMAT_DEVREV_RT,
    CONTENT_FORMAT_HTML,
    CONTENT_FORMAT_MARKDOWN,
    OutputFormat,
    detect_content_format,
    devrev_rt_to_html,
    devrev_rt_to_markdown,
    html_to_devrev_rt,
)


def _extract_content_artifact_id(resource: dict[str, object]) -> str | None:
    """Extract the content artifact ID from an article's resource dict.

    The DevRev API uses two formats for storing artifact references:
    - Request format: ``{"content_artifact": "<artifact_id>"}``
    - Response format: ``{"artifacts": [{"id": "<artifact_id>", "file": {...}}]}``

    This helper handles both formats for robustness.

    Args:
        resource: The article's ``resource`` dict

    Returns:
        The content artifact ID, or ``None`` if not found
    """
    # Try response format first (most common when reading from API)
    artifacts = resource.get("artifacts")
    if isinstance(artifacts, list) and len(artifacts) > 0:
        first = artifacts[0]
        if isinstance(first, dict):
            art_id = first.get("id")
            if isinstance(art_id, str):
                return art_id

    # Fallback to request format (e.g., freshly created but not yet re-fetched)
    content_artifact = resource.get("content_artifact")
    if isinstance(content_artifact, str):
        return content_artifact

    return None


def _extract_content_format(resource: dict[str, object]) -> str:
    """Extract the content format (MIME type) from an article's resource dict.

    The format is stored in ``resource.artifacts[0].file.type`` in API responses.

    Args:
        resource: The article's ``resource`` dict

    Returns:
        The content format string, or ``"text/plain"`` if not found
    """
    artifacts = resource.get("artifacts")
    if isinstance(artifacts, list) and len(artifacts) > 0:
        first = artifacts[0]
        if isinstance(first, dict):
            file_info = first.get("file")
            if isinstance(file_info, dict):
                file_type = file_info.get("type")
                if isinstance(file_type, str):
                    return file_type
    return "text/plain"


def _convert_content(
    content: str,
    source_format: str,
    target_format: str,
) -> tuple[str, str]:
    """Convert article content between formats.

    Args:
        content: The raw content string.
        source_format: The MIME type of *content* (e.g. ``"devrev/rt"``).
        target_format: The desired output MIME type.

    Returns:
        A ``(converted_content, actual_format)`` tuple.  If no conversion
        is necessary (source == target, or conversion is not possible)
        the original content and format are returned.
    Raises:
        ValueError: If *target_format* is not a recognised format.
    """
    _VALID_FORMATS = {
        CONTENT_FORMAT_MARKDOWN,
        CONTENT_FORMAT_HTML,
        CONTENT_FORMAT_DEVREV_RT,
    }
    if target_format not in _VALID_FORMATS:
        raise ValueError(
            f"Invalid output_format {target_format!r}. Accepted values: {sorted(_VALID_FORMATS)}"
        )

    if source_format == target_format:
        return content, source_format

    # Auto-detect source format when unknown / generic
    if source_format in ("text/plain", ""):
        source_format = detect_content_format(content)

    if target_format == CONTENT_FORMAT_MARKDOWN:
        if source_format == CONTENT_FORMAT_DEVREV_RT:
            return devrev_rt_to_markdown(content), CONTENT_FORMAT_MARKDOWN
        # HTML or unknown → convert to devrev/rt first, then to markdown
        if source_format == CONTENT_FORMAT_HTML:
            rt = html_to_devrev_rt(content)
            return devrev_rt_to_markdown(rt), CONTENT_FORMAT_MARKDOWN
        # Already markdown or plain text
        return content, source_format

    if target_format == CONTENT_FORMAT_HTML:
        if source_format == CONTENT_FORMAT_DEVREV_RT:
            return devrev_rt_to_html(content), CONTENT_FORMAT_HTML
        if source_format == CONTENT_FORMAT_MARKDOWN:
            rt = html_to_devrev_rt(content)
            return devrev_rt_to_html(rt), CONTENT_FORMAT_HTML
        return content, source_format

    if target_format == CONTENT_FORMAT_DEVREV_RT:
        if source_format != CONTENT_FORMAT_DEVREV_RT:
            return html_to_devrev_rt(content), CONTENT_FORMAT_DEVREV_RT
        return content, source_format

    # Unknown target format – return unchanged
    return content, source_format


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

    def list(
        self,
        request: ArticlesListRequest | None = None,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: Sequence[ArticleStatus] | None = None,
        article_type: Sequence[ArticleType] | None = None,
        applies_to_parts: Sequence[str] | None = None,
        authored_by: Sequence[str] | None = None,
        owned_by: Sequence[str] | None = None,
    ) -> ArticlesListResponse:
        """List articles with optional filtering and pagination.

        Can be called with a pre-built ``ArticlesListRequest`` or with
        keyword arguments for convenience.  When *request* is provided the
        keyword arguments are ignored.

        Args:
            request: Pre-built list request (keyword args ignored when set)
            cursor: Pagination cursor from a previous response
            limit: Maximum number of results (1-100)
            status: Filter by article status (e.g. draft, published)
            article_type: Filter by article type
            applies_to_parts: Filter by part IDs
            authored_by: Filter by author user IDs
            owned_by: Filter by owner user IDs

        Returns:
            Paginated response containing articles and next_cursor
        """
        if request is None:
            request = ArticlesListRequest(
                cursor=cursor,
                limit=limit,
                status=list(status) if status else None,
                article_type=list(article_type) if article_type else None,
                applies_to_parts=list(applies_to_parts) if applies_to_parts else None,
                authored_by=list(authored_by) if authored_by else None,
                owned_by=list(owned_by) if owned_by else None,
            )
        return self._post("/articles.list", request, ArticlesListResponse)

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
        owned_by: builtins.list[str],
        description: str | None = None,
        status: ArticleStatus | None = None,
        access_level: ArticleAccessLevel | None = None,
        content_format: str = "text/plain",
        applies_to_parts: builtins.list[str] | None = None,
        scope: int | None = None,
        tags: builtins.list[SetTagWithValue] | None = None,
        parent: str | None = None,
        article_type: str | None = None,
        language: str | None = None,
        authored_by: builtins.list[str] | None = None,
        shared_with: builtins.list[SetSharedWithMembership] | None = None,
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
            access_level: Optional access level (external, internal, private, public, restricted)
            content_format: Content MIME type (default: text/plain)
            applies_to_parts: Optional list of part IDs to associate with
            scope: Optional visibility scope (1=internal, 2=external)
            tags: Optional tags (list of SetTagWithValue)
            parent: Optional parent directory/collection DON ID
            article_type: Optional article type ('article', 'page', 'content_block')
            language: Optional language code (e.g., 'en')
            authored_by: Optional list of user IDs who author the article
            shared_with: Optional list of shared-with memberships

        Returns:
            Created article

        Raises:
            DevRevError: If parent client not available or operation fails

        Example:
            >>> article = client.articles.create_with_content(
            ...     title="User Guide",
            ...     content="<html>...</html>",
            ...     owned_by=["DEVU-123"],
            ...     content_format="text/html",
            ...     applies_to_parts=["don:core:...:feature/30"],
            ...     scope=2,  # external
            ...     access_level=ArticleAccessLevel.EXTERNAL,
            ... )
        """
        if not self._parent_client:
            raise DevRevError(
                "create_with_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        artifact_id: str | None = None
        try:
            # Convert content to devrev/rt (ProseMirror JSON) so it renders
            # inline in the DevRev UI.  If content_format is already devrev/rt
            # (or the content is valid devrev/rt JSON), the converter is a no-op.
            if content_format != "devrev/rt":
                upload_content = html_to_devrev_rt(content)
                upload_format = "devrev/rt"
            else:
                upload_content = content
                upload_format = "devrev/rt"

            # Step 1: Prepare artifact
            prepare_req = ArtifactPrepareRequest(
                file_name="Article",
                file_type=upload_format,
            )
            prepare_resp = self._parent_client.artifacts.prepare(prepare_req)
            artifact_id = prepare_resp.id

            # Step 2: Upload content
            self._parent_client.artifacts.upload(prepare_resp, upload_content)

            # Step 3: Create article with artifact reference
            article_req = ArticlesCreateRequest(
                title=title,
                description=description,
                status=status,
                access_level=access_level,
                owned_by=owned_by,
                resource={"content_artifact": artifact_id},
                applies_to_parts=applies_to_parts,
                scope=scope,
                tags=tags,
                parent=parent,
                article_type=article_type,
                language=language,
                authored_by=authored_by,
                shared_with=shared_with,
            )
            return self.create(article_req)

        except Exception as e:
            # Note: Orphaned artifact cleanup is not possible with current DevRev API
            # The API does not provide artifact deletion, only version deletion
            # This may result in orphaned artifacts if article creation fails
            if artifact_id:
                logging.warning(
                    f"Orphaned artifact {artifact_id} may remain due to failed article creation. "
                    "Manual cleanup may be required."
                )

            # Re-raise the original error
            raise DevRevError(f"Failed to create article with content: {e}") from e

    def get_with_content(
        self,
        id: str,
        *,
        output_format: OutputFormat | None = None,
    ) -> ArticleWithContent:
        """Get an article with its content loaded.

        This is a high-level method that:
        1. Fetches article metadata
        2. Locates the content artifact
        3. Downloads artifact content
        4. Optionally converts to the requested output format
        5. Returns combined model

        Args:
            id: Article ID
            output_format: Desired output format for the content.  Accepted
                values: ``"text/markdown"``, ``"text/html"``, ``"devrev/rt"``.
                When ``None`` (the default) the raw stored content is returned
                as-is.

        Returns:
            ArticleWithContent with metadata and content

        Raises:
            DevRevError: If parent client not available, article not found,
                        or article has no content artifact

        Example:
            >>> article_with_content = client.articles.get_with_content("ART-123")
            >>> print(article_with_content.article.title)
            >>> print(article_with_content.content)
            >>> # Get content as Markdown
            >>> md = client.articles.get_with_content("ART-123", output_format="text/markdown")
            >>> print(md.content)
        """
        if not self._parent_client:
            raise DevRevError(
                "get_with_content requires parent client reference. "
                "Ensure client is properly initialized."
            )

        # Step 1: Get article metadata
        article = self.get(ArticlesGetRequest(id=id))

        # Step 2: Extract content artifact ID
        if not article.resource or not isinstance(article.resource, dict):
            raise DevRevError(f"Article {id} has no resource configuration")

        content_artifact_id = _extract_content_artifact_id(article.resource)
        if not content_artifact_id:
            raise DevRevError(
                f"Article {id} has no content artifact reference in resource configuration"
            )

        # Step 3: Download content
        try:
            content_bytes = self._parent_client.artifacts.download(content_artifact_id)
            content = content_bytes.decode("utf-8")

            # Get content format from resource metadata (more reliable than artifact.get)
            content_format = _extract_content_format(article.resource)

            # Step 4: Convert to requested output format if specified
            if output_format is not None:
                content, content_format = _convert_content(content, content_format, output_format)

            return ArticleWithContent(
                article=article,
                content=content,
                content_format=content_format,
                content_version=None,
            )
        except DevRevError:
            raise
        except Exception as e:
            raise DevRevError(f"Failed to download content for article {id}: {e}") from e

    def update_content(
        self,
        id: str,
        content: str,
        *,
        content_format: str | None = None,
    ) -> Article:
        """Update article content by creating a new artifact and updating the article.

        This method:
        1. Gets the current article to determine the content format
        2. Prepares and uploads a new artifact with the updated content
        3. Updates the article to reference the new artifact

        Args:
            id: Article ID
            content: New article body content
            content_format: Optional content format override. If not provided,
                the format is inherited from the current article's artifact.

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

        # Step 1: Get article to determine content format
        article = self.get(ArticlesGetRequest(id=id))

        if not article.resource or not isinstance(article.resource, dict):
            raise DevRevError(f"Article {id} has no resource configuration")

        # content_format is accepted for backward compatibility but all content
        # is now converted to devrev/rt for inline rendering in the DevRev UI.
        _ = content_format

        upload_content = html_to_devrev_rt(content)

        try:
            # Step 2: Prepare a new artifact
            prepare_req = ArtifactPrepareRequest(
                file_name="Article",
                file_type="devrev/rt",
            )
            prepare_resp = self._parent_client.artifacts.prepare(prepare_req)

            # Step 3: Upload new content
            self._parent_client.artifacts.upload(prepare_resp, upload_content)

            # Step 4: Update article to reference the new artifact.
            # The update endpoint uses ``artifacts`` with a ``set`` wrapper,
            # *not* the ``resource`` dict (which is read-only on updates).
            update_req = ArticlesUpdateRequest(
                id=id,
                artifacts={"set": [prepare_resp.id]},
            )
            return self.update(update_req)

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
        applies_to_parts: builtins.list[str] | None = None,
        access_level: ArticleAccessLevel | None = None,
        tags: builtins.list[SetTagWithValue] | None = None,
        language: str | None = None,
        shared_with: builtins.list[SetSharedWithMembership] | None = None,
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
            applies_to_parts: Optional list of part IDs to associate with
            access_level: Optional access level (internal, external, private, public)
            tags: Optional list of tags to apply (list of SetTagWithValue objects)
            language: Optional language code (e.g., 'en')
            shared_with: Optional list of shared-with memberships

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
            >>>
            >>> # Update applies_to_parts
            >>> article = client.articles.update_with_content(
            ...     "ART-123",
            ...     applies_to_parts=["don:core:...:capability/6"]
            ... )
            >>>
            >>> # Update access level to internal
            >>> article = client.articles.update_with_content(
            ...     "ART-123",
            ...     access_level=ArticleAccessLevel.INTERNAL
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

        # Build applies_to_parts wrapper if provided
        applies_to_parts_req = None
        if applies_to_parts is not None:
            applies_to_parts_req = ArticlesUpdateRequestAppliesToParts(set=applies_to_parts)

        # Build tags wrapper if provided
        tags_req = None
        if tags is not None:
            tags_req = ArticlesUpdateRequestTags(set=tags)

        # Build shared_with wrapper if provided
        shared_with_req = None
        if shared_with is not None:
            shared_with_req = ArticlesUpdateRequestSharedWith(set=shared_with)

        # Update metadata if any metadata fields provided
        has_metadata = (
            title is not None
            or description is not None
            or status is not None
            or applies_to_parts is not None
            or access_level is not None
            or tags is not None
            or language is not None
            or shared_with is not None
        )
        if has_metadata:
            update_req = ArticlesUpdateRequest(
                id=id,
                title=title,
                description=description,
                status=status,
                applies_to_parts=applies_to_parts_req,
                access_level=access_level,
                tags=tags_req,
                language=language,
                shared_with=shared_with_req,
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

    async def list(
        self,
        request: ArticlesListRequest | None = None,
        *,
        cursor: str | None = None,
        limit: int | None = None,
        status: Sequence[ArticleStatus] | None = None,
        article_type: Sequence[ArticleType] | None = None,
        applies_to_parts: Sequence[str] | None = None,
        authored_by: Sequence[str] | None = None,
        owned_by: Sequence[str] | None = None,
    ) -> ArticlesListResponse:
        """List articles with optional filtering and pagination.

        Can be called with a pre-built ``ArticlesListRequest`` or with
        keyword arguments for convenience.  When *request* is provided the
        keyword arguments are ignored.

        Args:
            request: Pre-built list request (keyword args ignored when set)
            cursor: Pagination cursor from a previous response
            limit: Maximum number of results (1-100)
            status: Filter by article status (e.g. draft, published)
            article_type: Filter by article type
            applies_to_parts: Filter by part IDs
            authored_by: Filter by author user IDs
            owned_by: Filter by owner user IDs

        Returns:
            Paginated response containing articles and next_cursor
        """
        if request is None:
            request = ArticlesListRequest(
                cursor=cursor,
                limit=limit,
                status=list(status) if status else None,
                article_type=list(article_type) if article_type else None,
                applies_to_parts=list(applies_to_parts) if applies_to_parts else None,
                authored_by=list(authored_by) if authored_by else None,
                owned_by=list(owned_by) if owned_by else None,
            )
        return await self._post("/articles.list", request, ArticlesListResponse)

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
        owned_by: builtins.list[str],
        description: str | None = None,
        status: ArticleStatus | None = None,
        access_level: ArticleAccessLevel | None = None,
        content_format: str = "text/plain",
        applies_to_parts: builtins.list[str] | None = None,
        scope: int | None = None,
        tags: builtins.list[SetTagWithValue] | None = None,
        parent: str | None = None,
        article_type: str | None = None,
        language: str | None = None,
        authored_by: builtins.list[str] | None = None,
        shared_with: builtins.list[SetSharedWithMembership] | None = None,
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
            access_level: Optional access level (external, internal, private, public, restricted)
            content_format: Content MIME type (default: text/plain)
            applies_to_parts: Optional list of part IDs to associate with
            scope: Optional visibility scope (1=internal, 2=external)
            tags: Optional tags (list of SetTagWithValue)
            parent: Optional parent directory/collection DON ID
            article_type: Optional article type ('article', 'page', 'content_block')
            language: Optional language code (e.g., 'en')
            authored_by: Optional list of user IDs who author the article

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
            # Convert content to devrev/rt (ProseMirror JSON) so it renders
            # inline in the DevRev UI.
            if content_format != "devrev/rt":
                upload_content = html_to_devrev_rt(content)
                upload_format = "devrev/rt"
            else:
                upload_content = content
                upload_format = "devrev/rt"

            # Step 1: Prepare artifact
            prepare_req = ArtifactPrepareRequest(
                file_name="Article",
                file_type=upload_format,
            )
            prepare_resp = await self._parent_client.artifacts.prepare(prepare_req)
            artifact_id = prepare_resp.id

            # Step 2: Upload content
            await self._parent_client.artifacts.upload(prepare_resp, upload_content)

            # Step 3: Create article with artifact reference
            article_req = ArticlesCreateRequest(
                title=title,
                description=description,
                status=status,
                access_level=access_level,
                owned_by=owned_by,
                resource={"content_artifact": artifact_id},
                applies_to_parts=applies_to_parts,
                scope=scope,
                tags=tags,
                parent=parent,
                article_type=article_type,
                language=language,
                authored_by=authored_by,
                shared_with=shared_with,
            )
            return await self.create(article_req)

        except Exception as e:
            # Note: Orphaned artifact cleanup is not possible with current DevRev API
            # The API does not provide artifact deletion, only version deletion
            # This may result in orphaned artifacts if article creation fails
            if artifact_id:
                logging.warning(
                    f"Orphaned artifact {artifact_id} may remain due to failed article creation. "
                    "Manual cleanup may be required."
                )

            # Re-raise the original error
            raise DevRevError(f"Failed to create article with content: {e}") from e

    async def get_with_content(
        self,
        id: str,
        *,
        output_format: OutputFormat | None = None,
    ) -> ArticleWithContent:
        """Get an article with its content loaded (async).

        This is a high-level method that:
        1. Fetches article metadata
        2. Locates the content artifact
        3. Downloads artifact content
        4. Optionally converts to the requested output format
        5. Returns combined model

        Args:
            id: Article ID
            output_format: Desired output format for the content.  Accepted
                values: ``"text/markdown"``, ``"text/html"``, ``"devrev/rt"``.
                When ``None`` (the default) the raw stored content is returned
                as-is.

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

        content_artifact_id = _extract_content_artifact_id(article.resource)
        if not content_artifact_id:
            raise DevRevError(
                f"Article {id} has no content artifact reference in resource configuration"
            )

        # Step 3: Download content
        try:
            content_bytes = await self._parent_client.artifacts.download(content_artifact_id)
            content = content_bytes.decode("utf-8")

            # Get content format from resource metadata (more reliable than artifact.get)
            content_format = _extract_content_format(article.resource)

            # Step 4: Convert to requested output format if specified
            if output_format is not None:
                content, content_format = _convert_content(content, content_format, output_format)

            return ArticleWithContent(
                article=article,
                content=content,
                content_format=content_format,
                content_version=None,
            )
        except DevRevError:
            raise
        except Exception as e:
            raise DevRevError(f"Failed to download content for article {id}: {e}") from e

    async def update_content(
        self,
        id: str,
        content: str,
        *,
        content_format: str | None = None,
    ) -> Article:
        """Update article content by creating a new artifact and updating the article (async).

        This method:
        1. Gets the current article to determine the content format
        2. Prepares and uploads a new artifact with the updated content
        3. Updates the article to reference the new artifact

        Args:
            id: Article ID
            content: New article body content
            content_format: Optional content format override. If not provided,
                the format is inherited from the current article's artifact.

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

        # Step 1: Get article to determine content format
        article = await self.get(ArticlesGetRequest(id=id))

        if not article.resource or not isinstance(article.resource, dict):
            raise DevRevError(f"Article {id} has no resource configuration")

        # content_format is accepted for backward compatibility but all content
        # is now converted to devrev/rt for inline rendering in the DevRev UI.
        _ = content_format

        upload_content = html_to_devrev_rt(content)

        try:
            # Step 2: Prepare a new artifact
            prepare_req = ArtifactPrepareRequest(
                file_name="Article",
                file_type="devrev/rt",
            )
            prepare_resp = await self._parent_client.artifacts.prepare(prepare_req)

            # Step 3: Upload new content
            await self._parent_client.artifacts.upload(prepare_resp, upload_content)

            # Step 4: Update article to reference the new artifact.
            # The update endpoint uses ``artifacts`` with a ``set`` wrapper,
            # *not* the ``resource`` dict (which is read-only on updates).
            update_req = ArticlesUpdateRequest(
                id=id,
                artifacts={"set": [prepare_resp.id]},
            )
            return await self.update(update_req)

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
        applies_to_parts: builtins.list[str] | None = None,
        access_level: ArticleAccessLevel | None = None,
        tags: builtins.list[SetTagWithValue] | None = None,
        language: str | None = None,
        shared_with: builtins.list[SetSharedWithMembership] | None = None,
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
            applies_to_parts: Optional list of part IDs to associate with
            access_level: Optional access level (internal, external, private, public)
            tags: Optional list of tags to apply (list of SetTagWithValue objects)
            language: Optional language code (e.g., 'en')
            shared_with: Optional list of shared-with memberships

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

        # Build applies_to_parts wrapper if provided
        applies_to_parts_req = None
        if applies_to_parts is not None:
            applies_to_parts_req = ArticlesUpdateRequestAppliesToParts(set=applies_to_parts)

        # Build tags wrapper if provided
        tags_req = None
        if tags is not None:
            tags_req = ArticlesUpdateRequestTags(set=tags)

        # Build shared_with wrapper if provided
        shared_with_req = None
        if shared_with is not None:
            shared_with_req = ArticlesUpdateRequestSharedWith(set=shared_with)

        # Update metadata if any metadata fields provided
        has_metadata = (
            title is not None
            or description is not None
            or status is not None
            or applies_to_parts is not None
            or access_level is not None
            or tags is not None
            or language is not None
            or shared_with is not None
        )
        if has_metadata:
            update_req = ArticlesUpdateRequest(
                id=id,
                title=title,
                description=description,
                status=status,
                applies_to_parts=applies_to_parts_req,
                access_level=access_level,
                tags=tags_req,
                language=language,
                shared_with=shared_with_req,
            )
            return await self.update(update_req)

        # If only content was updated, return the article
        return await self.get(ArticlesGetRequest(id=id))
