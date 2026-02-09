"""Entry point for running the DevRev MCP Server."""

from __future__ import annotations

import argparse
import os


def main() -> None:
    """Run the DevRev MCP Server with configurable transport."""
    parser = argparse.ArgumentParser(
        prog="devrev-mcp-server",
        description="DevRev MCP Server — expose DevRev platform as MCP tools, resources, and prompts",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default=None,
        help="Transport type (default: from MCP_TRANSPORT env var, or stdio)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="HTTP server bind host (default: from MCP_HOST env var, or 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="HTTP server bind port (default: from MCP_PORT env var, or 8080)",
    )

    args = parser.parse_args()

    # CLI args override environment variables (which override defaults in config)
    if args.transport:
        os.environ["MCP_TRANSPORT"] = args.transport
    if args.host:
        os.environ["MCP_HOST"] = args.host
    if args.port:
        os.environ["MCP_PORT"] = str(args.port)

    # Import server after setting env vars so config picks them up
    from devrev_mcp.config import MCPServerConfig
    from devrev_mcp.server import mcp

    config = MCPServerConfig()
    mcp.run(transport=config.transport)


if __name__ == "__main__":
    main()
