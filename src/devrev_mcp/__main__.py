"""Entry point for running the DevRev MCP Server."""

from __future__ import annotations

from devrev_mcp.server import mcp


def main() -> None:
    """Run the DevRev MCP Server using stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()
