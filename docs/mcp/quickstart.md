---
icon: material/rocket-launch
---

# MCP Server Quick Start

Get the DevRev MCP Server running with your AI assistant in under 5 minutes.

## Prerequisites

- Python 3.11+
- A DevRev API token ([get one from your DevRev dashboard](https://app.devrev.ai/settings/api-tokens))

## Installation

```bash
# Install with MCP extras
pip install devrev-python-sdk[mcp]

# Set your DevRev API token
export DEVREV_API_TOKEN="your-token-here"

# Verify the server starts
devrev-mcp-server --help
```

## Client Setup

### Augment Code

=== "VS Code (Import JSON)"

    1. Open VS Code → Augment settings (gear icon)
    2. In the MCP section, click **Import from JSON**
    3. Paste:

    ```json
    {
      "mcpServers": {
        "devrev": {
          "command": "devrev-mcp-server",
          "env": {
            "DEVREV_API_TOKEN": "<your-devrev-api-token>",
            "MCP_ENABLE_BETA_TOOLS": "true",
            "MCP_ENABLE_DESTRUCTIVE_TOOLS": "false",
            "MCP_LOG_LEVEL": "INFO"
          }
        }
      }
    }
    ```

=== "JetBrains IDE"

    1. Open your JetBrains IDE → Augment panel (gear icon)
    2. Click **+** in the **MCP** section
    3. Set **Name**: `devrev`, **Command**: `devrev-mcp-server`
    4. Add environment variables:
        - `DEVREV_API_TOKEN` = your token
        - `MCP_ENABLE_BETA_TOOLS` = `true`

=== "Auggie CLI"

    ```bash
    auggie mcp add devrev \
      --command devrev-mcp-server \
      -e DEVREV_API_TOKEN=<your-token> \
      -e MCP_ENABLE_BETA_TOOLS=true \
      -e MCP_ENABLE_DESTRUCTIVE_TOOLS=false

    # Verify
    auggie mcp list
    ```

=== "Remote (Cloud Run)"

    ```json
    {
      "mcpServers": {
        "devrev": {
          "type": "http",
          "url": "https://devrev-mcp-server-<hash>-uc.a.run.app/mcp",
          "headers": {
            "Authorization": "Bearer <your-devrev-personal-access-token>"
          }
        }
      }
    }
    ```

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "devrev": {
      "command": "devrev-mcp-server",
      "env": {
        "DEVREV_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Cursor

Add to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "devrev": {
      "command": "devrev-mcp-server",
      "env": {
        "DEVREV_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Generic MCP Client

The server supports three transports:

```bash
# stdio (default) — for local/embedded use
devrev-mcp-server

# Streamable HTTP — for production deployment
devrev-mcp-server --transport streamable-http --host 0.0.0.0 --port 8080

# SSE (legacy) — Server-Sent Events
devrev-mcp-server --transport sse --host 0.0.0.0 --port 8080
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DEVREV_API_TOKEN` | Required | Your DevRev API token |
| `MCP_TRANSPORT` | `stdio` | Transport: `stdio`, `streamable-http`, `sse` |
| `MCP_HOST` | `127.0.0.1` | Host to bind (HTTP transports) |
| `MCP_PORT` | `8080` | Port to bind (HTTP transports) |
| `MCP_ENABLE_BETA_TOOLS` | `false` | Enable beta API tools (search, incidents, etc.) |
| `MCP_ENABLE_DESTRUCTIVE_TOOLS` | `false` | Enable delete/destroy operations |
| `MCP_LOG_LEVEL` | `INFO` | Logging level |
| `MCP_LOG_FORMAT` | `text` | Log format: `text` or `json` |
| `MCP_AUTH_TOKEN` | — | Bearer token for HTTP authentication |
| `MCP_AUTH_MODE` | `devrev-pat` | Auth mode: `devrev-pat` or `static-token` |

## Verify It Works

Once configured, ask your AI assistant:

> "List my DevRev accounts"

or

> "Create a ticket titled 'Test from MCP' in DevRev"

The assistant should use the DevRev MCP tools to fulfill your request.

## Next Steps

- [**Tools Reference**](tools-reference.md) — See all 78+ tools, 7 resources, and 8 prompts
- [**Deployment Guide**](deployment.md) — Deploy to Google Cloud Run for team use

