"""Survey response service for DevRev SDK."""

from __future__ import annotations

from collections.abc import Sequence

from devrev.models.survey_responses import (
    SurveyResponsesListMode,
    SurveyResponsesListRequest,
    SurveyResponsesListResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


def _merge_object_filters(object_id: str | None, objects: Sequence[str] | None) -> list[str] | None:
    """Merge singular and plural object filters without duplicates."""
    merged = list(objects or [])
    if object_id and object_id not in merged:
        merged.insert(0, object_id)
    return merged or None


class SurveyResponsesService(BaseService):
    """Synchronous service for survey/CSAT responses."""

    def list(
        self,
        *,
        object_id: str | None = None,
        objects: Sequence[str] | None = None,
        created_by: Sequence[str] | None = None,
        cursor: str | None = None,
        dispatch_ids: Sequence[str] | None = None,
        limit: int | None = None,
        mode: SurveyResponsesListMode | None = None,
        recipient: Sequence[str] | None = None,
        sort_by: Sequence[str] | None = None,
        stages: Sequence[int] | None = None,
        surveys: Sequence[str] | None = None,
    ) -> SurveyResponsesListResponse:
        """List survey responses.

        Args:
            object_id: Convenience filter for a single ticket/work/object ID.
            objects: Object IDs to filter responses by.
            created_by: Creator user filters.
            cursor: Pagination cursor.
            dispatch_ids: Survey dispatch IDs.
            limit: Maximum number of responses to return.
            mode: Cursor iteration mode.
            recipient: Recipient user filters.
            sort_by: Sort order entries.
            stages: Survey response stage filters.
            surveys: Survey IDs to filter by.

        Returns:
            Paginated survey response list.
        """
        request = SurveyResponsesListRequest(
            created_by=list(created_by) if created_by else None,
            cursor=cursor,
            dispatch_ids=list(dispatch_ids) if dispatch_ids else None,
            limit=limit,
            mode=mode,
            objects=_merge_object_filters(object_id, objects),
            recipient=list(recipient) if recipient else None,
            sort_by=list(sort_by) if sort_by else None,
            stages=list(stages) if stages else None,
            surveys=list(surveys) if surveys else None,
        )
        return self._post("/surveys.responses.list", request, SurveyResponsesListResponse)


class AsyncSurveyResponsesService(AsyncBaseService):
    """Asynchronous service for survey/CSAT responses."""

    async def list(
        self,
        *,
        object_id: str | None = None,
        objects: Sequence[str] | None = None,
        created_by: Sequence[str] | None = None,
        cursor: str | None = None,
        dispatch_ids: Sequence[str] | None = None,
        limit: int | None = None,
        mode: SurveyResponsesListMode | None = None,
        recipient: Sequence[str] | None = None,
        sort_by: Sequence[str] | None = None,
        stages: Sequence[int] | None = None,
        surveys: Sequence[str] | None = None,
    ) -> SurveyResponsesListResponse:
        """List survey responses.

        Args:
            object_id: Convenience filter for a single ticket/work/object ID.
            objects: Object IDs to filter responses by.
            created_by: Creator user filters.
            cursor: Pagination cursor.
            dispatch_ids: Survey dispatch IDs.
            limit: Maximum number of responses to return.
            mode: Cursor iteration mode.
            recipient: Recipient user filters.
            sort_by: Sort order entries.
            stages: Survey response stage filters.
            surveys: Survey IDs to filter by.

        Returns:
            Paginated survey response list.
        """
        request = SurveyResponsesListRequest(
            created_by=list(created_by) if created_by else None,
            cursor=cursor,
            dispatch_ids=list(dispatch_ids) if dispatch_ids else None,
            limit=limit,
            mode=mode,
            objects=_merge_object_filters(object_id, objects),
            recipient=list(recipient) if recipient else None,
            sort_by=list(sort_by) if sort_by else None,
            stages=list(stages) if stages else None,
            surveys=list(surveys) if surveys else None,
        )
        return await self._post("/surveys.responses.list", request, SurveyResponsesListResponse)
