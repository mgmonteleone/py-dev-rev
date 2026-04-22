---
icon: material/tools
---

# Tools, Resources & Prompts Reference

Complete reference of all MCP capabilities provided by the DevRev MCP Server.

## Tools (83+)

Tools are the primary way AI assistants interact with DevRev. Each tool maps to one or more DevRev API endpoints.

### Works (Tickets, Issues & Tasks)

In DevRev, **works** is the umbrella type covering tickets (customer support),
issues (engineering), and tasks.

| Tool | Description |
|------|-------------|
| `devrev_works_list` | List work items with filters and `sort_by` (e.g., `["modified_date:desc"]`) |
| `devrev_works_get` | Get a specific work item by ID |
| `devrev_works_create` | Create a new ticket, issue, or task |
| `devrev_works_update` | Update a work item's fields |
| `devrev_works_delete` | Delete a work item (requires destructive tools enabled) |
| `devrev_works_export` | Bulk-export work items (accepts `sort_by`) |
| `devrev_works_list_modified_since` | List work items with `modified_date >= after` (ISO-8601), paged newest-first |
| `devrev_works_list_created_since` | List work items with `created_date >= after` (ISO-8601), paged newest-first |

**Key parameters:**

- `sort_by` (on `devrev_works_list` / `devrev_works_export`): List of
  `"field:asc"` / `"field:desc"` entries. The legacy `"-field"` shortcut is
  also accepted and normalized by the SDK before the request is sent.
- `after` (on `*_list_modified_since` / `*_list_created_since`): ISO-8601
  timestamp (e.g., `"2025-01-15T00:00:00Z"`). Items at or after this
  timestamp are returned.
- `limit` (on `*_list_modified_since` / `*_list_created_since`): Hard cap on
  total items returned across all pages.

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
- **Part Association**: Use `applies_to_parts` to natively associate articles with products, capabilities, features, or enhancements
- **Visibility Control**: Use `scope` (1=internal, 2=external) on create or `access_level` (internal, external, private, public) on update
- **Tagging**: Apply tags using the `tags` parameter (list of tag IDs)

### Conversations

| Tool | Description |
|------|-------------|
| `devrev_conversations_list` | List conversations; supports `modified_date_after` / `modified_date_before` (ISO-8601) and `sort_by` |
| `devrev_conversations_list_modified_since` | List conversations with `modified_date >= after` (ISO-8601), paged newest-first |
| `devrev_conversations_get` | Get conversation details |
| `devrev_conversations_create` | Create a conversation |
| `devrev_conversations_update` | Update a conversation |

**Key parameters:**

- `modified_date_after` / `modified_date_before` (on `devrev_conversations_list`):
  ISO-8601 timestamps bounding the `modified_date` filter.
- `sort_by` (on `devrev_conversations_list`): Same syntax as on
  `devrev_works_list` — `"field:asc"` / `"field:desc"` entries, with the
  legacy `"-field"` shortcut accepted and normalized by the SDK.
- `after` (on `devrev_conversations_list_modified_since`): ISO-8601
  timestamp. Items at or after this timestamp are returned.

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
| `devrev_question_answers_list` | List question-answer entries |
| `devrev_question_answers_get` | Get a question-answer by ID |
| `devrev_question_answers_create` | Create a new Q&A entry ¹ |
| `devrev_question_answers_update` | Update a Q&A entry ¹ |
| `devrev_question_answers_delete` | Delete a Q&A entry ¹ |

¹ Also requires `MCP_ENABLE_DESTRUCTIVE_TOOLS=true`

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

