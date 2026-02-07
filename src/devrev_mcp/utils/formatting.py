"""Formatting and serialization utilities for DevRev MCP tools."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def serialize_model(model: BaseModel) -> dict[str, Any]:
    """Serialize a Pydantic model to a JSON-compatible dict.

    Excludes None values and converts to JSON-safe types.

    Args:
        model: The Pydantic model to serialize.

    Returns:
        A dict with non-None fields, ready for JSON output.
    """
    return model.model_dump(exclude_none=True, mode="json")


def serialize_models(models: list[BaseModel] | tuple[BaseModel, ...]) -> list[dict[str, Any]]:
    """Serialize a sequence of Pydantic models.

    Args:
        models: The models to serialize.

    Returns:
        A list of serialized dicts.
    """
    return [serialize_model(m) for m in models]


def format_work_summary(work_data: dict[str, Any]) -> str:
    """Format a work item dict into a brief summary line.

    Args:
        work_data: Serialized work item dict.

    Returns:
        A formatted summary string.
    """
    display_id = work_data.get("display_id", "?")
    title = work_data.get("title", "Untitled")
    work_type = work_data.get("type", "unknown")
    stage = work_data.get("stage", {})
    stage_name = stage.get("name", "unknown") if isinstance(stage, dict) else "unknown"
    return f"[{display_id}] ({work_type}) {title} — stage: {stage_name}"


def format_account_summary(account_data: dict[str, Any]) -> str:
    """Format an account dict into a brief summary line.

    Args:
        account_data: Serialized account dict.

    Returns:
        A formatted summary string.
    """
    display_name = account_data.get("display_name", "Unnamed")
    display_id = account_data.get("display_id", "?")
    tier = account_data.get("tier", "")
    tier_str = f" (tier: {tier})" if tier else ""
    return f"[{display_id}] {display_name}{tier_str}"


def format_user_summary(user_data: dict[str, Any]) -> str:
    """Format a user dict into a brief summary line.

    Args:
        user_data: Serialized user dict.

    Returns:
        A formatted summary string.
    """
    display_name = user_data.get("display_name", "Unknown")
    email = user_data.get("email", "")
    state = user_data.get("state", "")
    email_str = f" <{email}>" if email else ""
    state_str = f" [{state}]" if state else ""
    return f"{display_name}{email_str}{state_str}"
