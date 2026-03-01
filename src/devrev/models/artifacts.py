"""Artifact models for DevRev SDK."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel, PaginatedResponse


class Artifact(DevRevResponseModel):
    """DevRev Artifact model."""

    id: str = Field(..., description="Artifact ID")
    created_by: str | None = Field(default=None, description="Creator user ID")
    created_date: datetime | None = Field(default=None, description="Creation timestamp")
    file_name: str | None = Field(default=None, description="Original file name")
    file_type: str | None = Field(default=None, description="MIME type of the file")
    file_size: int | None = Field(default=None, description="File size in bytes")
    version: str | None = Field(default=None, description="Artifact version")


class ArtifactPrepareFormData(DevRevResponseModel):
    """Form data field for artifact upload."""

    key: str = Field(..., description="Form field key")
    value: str = Field(..., description="Form field value")


class ArtifactPrepareRequest(DevRevBaseModel):
    """Request to prepare an artifact for upload."""

    file_name: str = Field(..., description="Name of file being uploaded")
    file_type: str | None = Field(default=None, description="MIME type of the file")
    configuration_set: str | None = Field(
        default=None,
        description=(
            "Configuration set for the artifact. "
            "Use 'article_media' for article content. "
            "Valid values: article_media, default, email_media, job_data, "
            "marketplace_listing_icon, marketplace_media, org_logo, plug_css, "
            "plug_setting, plug_setting_banner_card, portal_css, "
            "snap_in_functions_code, snap_widget, user_profile_picture, work"
        ),
    )


class ArtifactPrepareResponse(DevRevResponseModel):
    """Response from preparing an artifact upload."""

    id: str = Field(..., description="Generated artifact ID")
    url: str = Field(..., description="URL to upload file data to")
    form_data: list[ArtifactPrepareFormData] = Field(
        ..., description="POST policy form data for upload"
    )


class ArtifactGetRequest(DevRevBaseModel):
    """Request to get an artifact."""

    id: str = Field(..., description="Artifact ID")
    version: str | None = Field(default=None, description="Specific version to fetch")


class ArtifactGetResponse(DevRevResponseModel):
    """Response from getting an artifact."""

    artifact: Artifact = Field(..., description="Retrieved artifact")


class ArtifactListRequest(DevRevBaseModel):
    """Request to list artifacts."""

    parent_id: str | None = Field(
        default=None, description="Filter artifacts by parent object ID"
    )


class ArtifactListResponse(PaginatedResponse):
    """Response from listing artifacts."""

    artifacts: list[Artifact] = Field(default_factory=list, description="List of artifacts")


class ArtifactLocateRequest(DevRevBaseModel):
    """Request to get artifact download URL."""

    id: str = Field(..., description="Artifact ID")
    version: str | None = Field(default=None, description="Specific version to locate")


class ArtifactLocateResponse(DevRevResponseModel):
    """Response with artifact download URL."""

    url: str = Field(..., description="Download URL for the artifact")


class ArtifactVersionsPrepareRequest(DevRevBaseModel):
    """Request to prepare a new version of an artifact."""

    id: str = Field(..., description="Artifact ID to create new version for")


class ArtifactVersionsPrepareResponse(DevRevResponseModel):
    """Response from preparing a new artifact version."""

    id: str = Field(..., description="Artifact ID")
    url: str = Field(..., description="URL to upload new version data to")
    form_data: list[ArtifactPrepareFormData] = Field(
        ..., description="POST policy form data for upload"
    )


class ArtifactVersionsDeleteRequest(DevRevBaseModel):
    """Request to delete an artifact version."""

    id: str = Field(..., description="Artifact ID")
    version: str = Field(..., description="Version to delete")


class ArtifactVersionsDeleteResponse(DevRevResponseModel):
    """Response from deleting an artifact version."""

    pass
