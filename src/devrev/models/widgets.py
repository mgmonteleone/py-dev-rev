"""Widget models for DevRev SDK.

This module contains Pydantic models for Dashboard Widget-related API operations.
Widgets are used to display data visualizations on DevRev dashboards.
"""

from __future__ import annotations

from enum import Enum

from pydantic import Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class WidgetVisualizationType(str, Enum):
    """Widget visualization type enumeration."""

    BAR = "bar"
    COLUMN = "column"
    TABLE = "table"
    LINE = "line"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    METRIC = "metric"


class WidgetDataSourceType(str, Enum):
    """Widget data source type enumeration."""

    API = "api"
    OASIS = "oasis"
    STATIC = "static"


class WidgetAggregationType(str, Enum):
    """Widget aggregation type enumeration."""

    COUNT = "count"
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"


class WidgetDataSource(DevRevBaseModel):
    """Widget data source configuration.

    Attributes:
        type: The type of data source
        endpoint: API endpoint for data retrieval
        query_id: Optional OASIS query ID
    """

    type: WidgetDataSourceType = Field(..., description="Data source type")
    endpoint: str | None = Field(default=None, description="API endpoint")
    query_id: str | None = Field(default=None, description="OASIS query ID")


class WidgetGroupByConfig(DevRevBaseModel):
    """Widget group-by configuration.

    Attributes:
        field: Field to group by
        limit: Maximum number of groups
    """

    field: str = Field(..., description="Field to group by")
    limit: int | None = Field(default=None, description="Maximum number of groups")


class WidgetQuery(DevRevBaseModel):
    """Widget query configuration.

    Attributes:
        filters: Query filters
        aggregation: Aggregation type
        time_range: Time range for query
    """

    filters: dict[str, object] | None = Field(default=None, description="Query filters")
    aggregation: WidgetAggregationType | None = Field(default=None, description="Aggregation type")
    time_range: str | None = Field(default=None, description="Time range (e.g., '7d', '30d')")


class Widget(DevRevResponseModel):
    """Dashboard widget model.

    Represents a widget on a DevRev dashboard that displays
    data visualizations like charts, tables, or metrics.

    Attributes:
        id: Unique widget identifier
        name: Widget display name
        description: Widget description
        visualization_type: Type of visualization
        data_source: Data source configuration
        query: Query configuration
        group_by: Group-by configuration
    """

    id: str = Field(..., description="Unique widget identifier")
    name: str = Field(..., description="Widget display name")
    description: str | None = Field(default=None, description="Widget description")
    visualization_type: WidgetVisualizationType = Field(..., description="Type of visualization")
    data_source: WidgetDataSource = Field(..., description="Data source configuration")
    query: WidgetQuery | None = Field(default=None, description="Query configuration")
    group_by: WidgetGroupByConfig | None = Field(default=None, description="Group-by configuration")


# Request/Response models for widget operations


class WidgetsGetRequest(DevRevBaseModel):
    """Request to get a widget by ID."""

    id: str = Field(..., description="Widget ID")


class WidgetsGetResponse(DevRevResponseModel):
    """Response from getting a widget."""

    widget: Widget = Field(..., description="The widget")


class WidgetsListRequest(DevRevBaseModel):
    """Request to list widgets."""

    dashboard_id: str | None = Field(default=None, description="Filter by dashboard ID")
    limit: int | None = Field(default=None, description="Maximum results")
    cursor: str | None = Field(default=None, description="Pagination cursor")


class WidgetsListResponse(DevRevResponseModel):
    """Response from listing widgets."""

    widgets: list[Widget] = Field(..., description="List of widgets")
    next_cursor: str | None = Field(default=None, description="Next pagination cursor")
