---
icon: material/robot
---

# MCP Server

<span class="section-label">MODEL CONTEXT PROTOCOL</span>

The DevRev MCP Server exposes the full DevRev platform as AI-accessible tools, resources, and prompts through the [Model Context Protocol](https://modelcontextprotocol.io/). It enables AI assistants to interact with DevRev for support ticket management, customer engagement, and knowledge base operations.

<div class="mcp-highlight" markdown>

### :material-tools: 78+ Tools &nbsp; · &nbsp; :material-database: 7 Resources &nbsp; · &nbsp; :material-chat-processing: 8 Prompts &nbsp; · &nbsp; :material-shield-check: Production Ready

Built with the same SDK that powers this project. Fully typed, tested against the live DevRev API, and deployable to Google Cloud Run with per-user authentication.

</div>

## Why an MCP Server?

The Model Context Protocol (MCP) is an open standard that lets AI assistants connect to external tools and data. Instead of building custom integrations for each AI platform, MCP provides a universal interface.

With the DevRev MCP Server, you can:

- **Manage support tickets** — Create, update, triage, and resolve tickets through natural language
- **Browse customer data** — Access accounts, contacts, and conversation history
- **Search knowledge bases** — Find articles, Q&A pairs, and documentation
- **Automate workflows** — Escalate issues, generate reports, investigate problems
- **Access beta features** — Search, recommendations, incidents, and engagements

## Supported AI Clients

| Client | Transport | Setup |
|--------|-----------|-------|
| **Augment Code** (VS Code, JetBrains, CLI) | stdio / HTTP | [Quick Start](quickstart.md#augment-code) |
| **Claude Desktop** | stdio | [Quick Start](quickstart.md#claude-desktop) |
| **Cursor** | stdio | [Quick Start](quickstart.md#cursor) |
| **Any MCP Client** | stdio / Streamable HTTP / SSE | [Quick Start](quickstart.md#generic-mcp-client) |

## Key Features

<div class="grid cards" markdown>

-   :material-tools:{ .lg .middle } __78+ MCP Tools__

    ---

    Full CRUD for tickets, accounts, users, conversations, articles, parts, tags, groups, timeline, links, and SLAs — plus beta tools for search, recommendations, incidents, and engagements.

    [:octicons-arrow-right-24: Tools Reference](tools-reference.md)

-   :material-database:{ .lg .middle } __7 Resource Templates__

    ---

    Browse DevRev data using `devrev://` URI scheme — tickets, accounts, articles, users, parts, and conversations.

    [:octicons-arrow-right-24: Tools Reference](tools-reference.md#resources)

-   :material-chat-processing:{ .lg .middle } __8 Workflow Prompts__

    ---

    Pre-built prompts for triage, draft response, escalation, account summary, investigation, weekly report, find similar, and customer onboarding.

    [:octicons-arrow-right-24: Tools Reference](tools-reference.md#prompts)

-   :material-cloud-upload:{ .lg .middle } __Production Deployment__

    ---

    Deploy to Google Cloud Run with per-user PAT authentication, rate limiting, health checks, and automatic scaling.

    [:octicons-arrow-right-24: Deployment Guide](deployment.md)

-   :material-shield-check:{ .lg .middle } __Security Built-In__

    ---

    Bearer token auth, rate limiting, DNS rebinding protection, and destructive tool gating. Per-user DevRev PAT mode for teams.

-   :material-check-decagram:{ .lg .middle } __MCP 2025-06-18 Compliant__

    ---

    Latest protocol version with structured content support. Three transport options: stdio, Streamable HTTP, and SSE.

</div>

## Architecture

```
┌─────────────────────────────────────────────────┐
│                AI Assistant                      │
│         (Augment, Claude, Cursor)                │
└──────────────────┬──────────────────────────────┘
                   │ MCP Protocol
                   ▼
┌─────────────────────────────────────────────────┐
│            DevRev MCP Server                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Tools   │ │Resources │ │     Prompts      │ │
│  │  (78+)   │ │   (7)    │ │      (8)         │ │
│  └────┬─────┘ └────┬─────┘ └──────────────────┘ │
│       │             │                            │
│  ┌────▼─────────────▼───────────────────────────┐│
│  │         DevRev Python SDK                     ││
│  │    (Type-safe • Async • Retry • Rate Limit)   ││
│  └──────────────────┬───────────────────────────┘│
│                     │                            │
│  ┌──────────────────▼───────────────────────────┐│
│  │       Middleware (Auth, Rate Limit, Health)    ││
│  └──────────────────┬───────────────────────────┘│
└─────────────────────┼───────────────────────────┘
                      │ HTTPS
                      ▼
            ┌─────────────────┐
            │   DevRev API    │
            └─────────────────┘
```

## Next Steps

- [**Quick Start**](quickstart.md) — Get the MCP server running in under 5 minutes
- [**Tools Reference**](tools-reference.md) — Browse all available tools, resources, and prompts
- [**Deployment Guide**](deployment.md) — Deploy to production on Google Cloud Run

