"""Task models for DevRev SDK.

This module contains Pydantic models for Task work item operations.
Tasks are a work item type used to track actionable items in DevRev.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class TaskPriority(str, Enum):
    """Task priority level enumeration."""

    P0 = "p0"
    P1 = "p1"
    P2 = "p2"
    P3 = "p3"


class TaskStatus(str, Enum):
    """Task status enumeration."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(DevRevResponseModel):
    """Task work item model.

    Represents a task in the DevRev system. Tasks are actionable
    work items that can be assigned to users and tracked.

    Attributes:
        id: Unique task identifier
        display_id: Human-readable task ID
        title: Task title
        body: Task description
        priority: Priority level
        status: Current status
        assignee_id: Assigned user ID
        due_date: Due date for the task
        created_at: Creation timestamp
        modified_at: Last modification timestamp
    """

    id: str = Field(..., description="Unique task identifier")
    display_id: str | None = Field(default=None, description="Human-readable task ID")
    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    body: str | None = Field(default=None, description="Task description")
    priority: TaskPriority | None = Field(default=None, description="Priority level")
    status: TaskStatus | None = Field(default=None, description="Current status")
    assignee_id: str | None = Field(default=None, description="Assigned user ID")
    owner_id: str | None = Field(default=None, description="Task owner ID")
    due_date: datetime | None = Field(default=None, description="Due date")
    created_at: datetime | None = Field(default=None, description="Creation timestamp")
    modified_at: datetime | None = Field(default=None, description="Last modification timestamp")
    tags: list[str] | None = Field(default=None, description="Associated tags")


# Request/Response models for task operations


class TasksCreateRequest(DevRevBaseModel):
    """Request to create a task."""

    title: str = Field(..., min_length=1, max_length=500, description="Task title")
    body: str | None = Field(default=None, description="Task description")
    priority: TaskPriority | None = Field(default=None, description="Priority level")
    assignee_id: str | None = Field(default=None, description="Assigned user ID")
    owner_id: str | None = Field(default=None, description="Task owner ID")
    due_date: datetime | None = Field(default=None, description="Due date")
    tags: list[str] | None = Field(default=None, description="Associated tags")


class TasksCreateResponse(DevRevResponseModel):
    """Response from creating a task."""

    task: Task = Field(..., description="The created task")


class TasksGetRequest(DevRevBaseModel):
    """Request to get a task by ID."""

    id: str = Field(..., description="Task ID")


class TasksGetResponse(DevRevResponseModel):
    """Response from getting a task."""

    task: Task = Field(..., description="The task")


class TasksUpdateRequest(DevRevBaseModel):
    """Request to update a task."""

    id: str = Field(..., description="Task ID to update")
    title: str | None = Field(default=None, description="New title")
    body: str | None = Field(default=None, description="New description")
    priority: TaskPriority | None = Field(default=None, description="New priority")
    status: TaskStatus | None = Field(default=None, description="New status")
    assignee_id: str | None = Field(default=None, description="New assignee")
    due_date: datetime | None = Field(default=None, description="New due date")


class TasksUpdateResponse(DevRevResponseModel):
    """Response from updating a task."""

    task: Task = Field(..., description="The updated task")


class TasksDeleteRequest(DevRevBaseModel):
    """Request to delete a task."""

    id: str = Field(..., description="Task ID to delete")


class TasksDeleteResponse(DevRevResponseModel):
    """Response from deleting a task."""

    pass


class TasksListRequest(DevRevBaseModel):
    """Request to list tasks."""

    assignee_id: str | None = Field(default=None, description="Filter by assignee")
    status: TaskStatus | None = Field(default=None, description="Filter by status")
    priority: TaskPriority | None = Field(default=None, description="Filter by priority")
    limit: int | None = Field(default=None, description="Maximum results")
    cursor: str | None = Field(default=None, description="Pagination cursor")


class TasksListResponse(DevRevResponseModel):
    """Response from listing tasks."""

    tasks: list[Task] = Field(..., description="List of tasks")
    next_cursor: str | None = Field(default=None, description="Next pagination cursor")
