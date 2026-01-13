#!/usr/bin/env python3
"""Google Cloud Functions with DevRev SDK.

This example demonstrates using the DevRev SDK in
serverless cloud functions.

Deploy:
    gcloud functions deploy handle_webhook \
        --runtime python312 \
        --trigger-http \
        --allow-unauthenticated
"""

import json
from typing import Any

import functions_framework
from flask import Request

from devrev import DevRevClient
from devrev.exceptions import DevRevError


@functions_framework.http
def handle_webhook(request: Request) -> tuple[dict[str, Any], int]:
    """Handle incoming DevRev webhook.

    Args:
        request: The incoming HTTP request.

    Returns:
        JSON response with status code.
    """
    if request.method != "POST":
        return {"error": "Method not allowed"}, 405

    data = request.get_json(silent=True)
    if not data:
        return {"error": "Invalid JSON"}, 400

    event_type = data.get("type", "unknown")
    print(f"Received webhook: {event_type}")

    # Process different event types
    if event_type == "work.created":
        work = data.get("work", {})
        print(f"New work item created: {work.get('title')}")
        # Add your processing logic here

    elif event_type == "work.updated":
        work = data.get("work", {})
        print(f"Work item updated: {work.get('id')}")
        # Add your processing logic here

    elif event_type == "conversation.created":
        conv = data.get("conversation", {})
        print(f"New conversation: {conv.get('id')}")
        # Add your processing logic here

    return {"status": "ok", "event_type": event_type}, 200


@functions_framework.http
def list_accounts(request: Request) -> tuple[dict[str, Any], int]:
    """List DevRev accounts.

    Args:
        request: The incoming HTTP request.

    Returns:
        JSON response with accounts.
    """
    client = DevRevClient()

    try:
        limit = request.args.get("limit", 10, type=int)
        response = client.accounts.list(limit=limit)

        return {
            "accounts": [
                {"id": a.id, "name": a.display_name} for a in response.accounts
            ]
        }, 200

    except DevRevError as e:
        return {"error": str(e)}, 500

    finally:
        client.close()


@functions_framework.http
def create_ticket(request: Request) -> tuple[dict[str, Any], int]:
    """Create a support ticket.

    Args:
        request: The incoming HTTP request with ticket data.

    Returns:
        JSON response with created ticket.
    """
    if request.method != "POST":
        return {"error": "Method not allowed"}, 405

    data = request.get_json(silent=True)
    if not data:
        return {"error": "Invalid JSON"}, 400

    client = DevRevClient()

    try:
        response = client.works.create(
            type="ticket",
            title=data["title"],
            body=data.get("description", ""),
            applies_to_part=data["part_id"],
        )

        return {
            "id": response.work.id,
            "display_id": response.work.display_id,
            "title": response.work.title,
        }, 201

    except KeyError as e:
        return {"error": f"Missing required field: {e}"}, 400

    except DevRevError as e:
        return {"error": str(e)}, 500

    finally:
        client.close()

