#!/usr/bin/env python3
"""Flask application with DevRev SDK.

This example demonstrates integrating the DevRev SDK
with a Flask web application.

Run:
    flask run
"""

import logging

from flask import Flask, g, jsonify, request

from devrev import DevRevClient
from devrev.exceptions import DevRevError, NotFoundError

app = Flask(__name__)


def get_client() -> DevRevClient:
    """Get or create a DevRev client for this request."""
    if "devrev_client" not in g:
        g.devrev_client = DevRevClient()
    return g.devrev_client


@app.teardown_appcontext
def close_client(_error):
    """Close the client at the end of the request."""
    client = g.pop("devrev_client", None)
    if client is not None:
        client.close()


@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


@app.route("/accounts")
def list_accounts():
    """List DevRev accounts."""
    client = get_client()
    limit = request.args.get("limit", 10, type=int)

    response = client.accounts.list(limit=limit)
    return jsonify({"accounts": [{"id": a.id, "name": a.display_name} for a in response.accounts]})


@app.route("/works/<work_id>")
def get_work(work_id: str):
    """Get a specific work item."""
    client = get_client()
    try:
        response = client.works.get(id=work_id)
        return jsonify(
            {
                "id": response.work.id,
                "title": response.work.title,
                "type": response.work.type,
            }
        )
    except NotFoundError:
        return jsonify({"error": "Work not found"}), 404


@app.route("/tickets", methods=["POST"])
def create_ticket():
    """Create a new support ticket."""
    client = get_client()
    data = request.get_json()

    try:
        response = client.works.create(
            type="ticket",
            title=data["title"],
            body=data.get("description", ""),
            applies_to_part=data["part_id"],
        )
        return jsonify(
            {
                "id": response.work.id,
                "display_id": response.work.display_id,
                "title": response.work.title,
            }
        )
    except DevRevError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError:
        logging.exception("Missing required field in ticket creation request")
        return jsonify({"error": "Missing required field in request body"}), 400


if __name__ == "__main__":
    app.run(debug=True)
