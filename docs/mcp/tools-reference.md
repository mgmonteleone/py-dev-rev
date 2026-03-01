---
icon: material/tools
---

# Tools, Resources & Prompts Reference

Complete reference of all MCP capabilities provided by the DevRev MCP Server.

## Tools (78+)

Tools are the primary way AI assistants interact with DevRev. Each tool maps to one or more DevRev API endpoints.

### Works (Tickets & Issues)

| Tool | Description |
|------|-------------|
| `devrev_works_list` | List work items (tickets, issues) with filters |
| `devrev_works_get` | Get a specific work item by ID |
| `devrev_works_create` | Create a new ticket or issue |
| `devrev_works_update` | Update a work item's fields |
| `devrev_works_delete` | Delete a work item (requires destructive tools enabled) |

### Accounts

| Tool | Description |
|------|-------------|
| `devrev_accounts_list` | List customer accounts |
| `devrev_accounts_get` | Get account details by ID |
| `devrev_accounts_create` | Create a new account |
| `devrev_accounts_update` | Update account information |
| `devrev_accounts_delete` | Delete an account |

### Users (Dev Users & Rev Users)

| Tool | Description |
|------|-------------|
| `devrev_dev_users_list` | List internal dev users |
| `devrev_dev_users_get` | Get dev user details |
| `devrev_rev_users_list` | List external rev (customer) users |
| `devrev_rev_users_get` | Get rev user details |
| `devrev_rev_users_create` | Create a rev user |
| `devrev_rev_users_update` | Update rev user information |

### Articles (Knowledge Base)

| Tool | Description |
|------|-------------|
| `devrev_articles_list` | List knowledge base articles |
| `devrev_articles_get` | Get article by ID with optional content |
| `devrev_articles_create` | Create a new article with content (automatic artifact handling) |
| `devrev_articles_update` | Update article metadata and/or content |
| `devrev_articles_delete` | Delete an article |
| `devrev_articles_count` | Count articles (beta) |

**Key Features:**
- **Unified Content Management**: Create and update articles with automatic artifact handling
- **Optional Content Loading**: Use `include_content=true` in `get` to fetch article body
- **Clear Parameters**: `content` for article body, `description` for metadata summary

### Conversations

| Tool | Description |
|------|-------------|
| `devrev_conversations_list` | List conversations |
| `devrev_conversations_get` | Get conversation details |
| `devrev_conversations_create` | Create a conversation |
| `devrev_conversations_update` | Update a conversation |

### Parts (Products & Features)

| Tool | Description |
|------|-------------|
| `devrev_parts_list` | List product parts |
| `devrev_parts_get` | Get part details |
| `devrev_parts_create` | Create a product/feature part |
| `devrev_parts_update` | Update a part |

### Tags

| Tool | Description |
|------|-------------|
| `devrev_tags_list` | List tags |
| `devrev_tags_get` | Get tag details |
| `devrev_tags_create` | Create a tag |
| `devrev_tags_update` | Update a tag |

### Groups

| Tool | Description |
|------|-------------|
| `devrev_groups_list` | List user groups |
| `devrev_groups_get` | Get group details |
| `devrev_groups_create` | Create a group |
| `devrev_groups_update` | Update a group |

### Timeline Entries

| Tool | Description |
|------|-------------|
| `devrev_timeline_entries_list` | List timeline entries for an object |
| `devrev_timeline_entries_create` | Add a comment or note to timeline |

### Links

| Tool | Description |
|------|-------------|
| `devrev_links_list` | List links between objects |
| `devrev_links_create` | Create a link between objects |
| `devrev_links_delete` | Delete a link |

### SLAs

| Tool | Description |
|------|-------------|
| `devrev_slas_list` | List SLA policies |
| `devrev_slas_get` | Get SLA details |

### Webhooks

| Tool | Description |
|------|-------------|
| `devrev_webhooks_list` | List webhooks |
| `devrev_webhooks_get` | Get webhook details |
| `devrev_webhooks_create` | Create a webhook |
| `devrev_webhooks_update` | Update a webhook |

### Beta Tools

!!! info "Beta tools require `MCP_ENABLE_BETA_TOOLS=true`"

| Tool | Description |
|------|-------------|
| `devrev_search` | Hybrid search across DevRev objects |
| `devrev_recommendations` | Get AI-powered recommendations |
| `devrev_incidents_list` | List incidents |
| `devrev_incidents_get` | Get incident details |
| `devrev_engagements_list` | List customer engagements |
| `devrev_engagements_get` | Get engagement details |

---

## Resources

Resources provide read-only access to DevRev data using `devrev://` URIs.

| URI Pattern | Description |
|-------------|-------------|
| `devrev://tickets/{id}` | Get a specific ticket |
| `devrev://accounts/{id}` | Get a specific account |
| `devrev://articles/{id}` | Get a specific article |
| `devrev://users/{id}` | Get a specific user |
| `devrev://parts/{id}` | Get a specific part |
| `devrev://conversations/{id}` | Get a specific conversation |

---

## Prompts

Pre-built workflow prompts that AI assistants can use for common support operations.

| Prompt | Description | Key Arguments |
|--------|-------------|---------------|
| `triage_ticket` | Analyze and triage a support ticket | `ticket_id` |
| `draft_response` | Draft a customer response | `ticket_id`, `tone` |
| `escalate_ticket` | Prepare escalation summary | `ticket_id`, `reason` |
| `summarize_account` | Generate account health summary | `account_id` |
| `investigate_issue` | Deep-dive into a technical issue | `ticket_id` |
| `weekly_report` | Generate weekly support metrics | `date_range` |
| `find_similar` | Find similar past tickets | `ticket_id` |
| `onboard_customer` | Generate onboarding checklist | `account_id` |

