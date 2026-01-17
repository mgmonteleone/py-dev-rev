# OpenAPI Beta vs Public API Differences

This document provides a comprehensive comparison between the DevRev **beta API** (`openapi-beta.yaml`) and the **public API** (`openapi-public.yaml`), intended to guide the implementation of beta API support in this SDK.

## Executive Summary

| Metric | Public API | Beta API | Difference |
|--------|------------|----------|------------|
| **Lines** | 38,016 | 56,229 | +48% |
| **New Endpoints** | - | 74 | - |

The beta introduces significant new features including incident management, engagement tracking, unit of measurement (UOM), brand management, and hybrid search.

---

## 1. New API Endpoints (Beta Only)

### 1.1 AI Agent Enhancements

| Endpoint | Description |
|----------|-------------|
| `/ai-agents.events.execute-async` | Asynchronous AI agent event execution with webhook/event source targets |

**Key Features:**
- Async execution with progress notifications
- Support for webhook and event source targets
- Session management with parent object access control
- Message context with artifact attachments

### 1.2 Airdrop Sync Management

| Endpoint | Description |
|----------|-------------|
| `/airdrop.sync-units.get` | Get sync unit details |
| `/airdrop.sync-units.history` | List sync unit history with filtering |

### 1.3 Brand Management (New Feature)

| Endpoint | Description |
|----------|-------------|
| `/brands.create` | Create a new brand |
| `/brands.delete` | Delete a brand |
| `/brands.get` | Get brand details |
| `/brands.list` | List all brands |
| `/brands.update` | Update a brand |

**Key Features:**
- Full CRUD operations for brands
- Brand association with articles and conversations
- Multi-brand support for organizations

### 1.4 Content Templates

| Endpoint | Description |
|----------|-------------|
| `/content-template.create` | Create content templates |
| `/content-template.get` | Get content template |
| `/content-template.list` | List content templates |

### 1.5 Engagement Management (New Feature)

| Endpoint | Description |
|----------|-------------|
| `/engagements.count` | Count engagement records |
| `/engagements.create` | Create engagement |
| `/engagements.delete` | Delete engagement |
| `/engagements.get` | Get engagement |
| `/engagements.list` | List engagements |
| `/engagements.update` | Update engagement |

**Key Features:**
- Engagement types: `call`, `conversation`, `custom`, `default`, `email`, `linked_in`, `meeting`, `offline`, `survey`
- Member tracking (up to 50 members)
- Parent association with accounts and opportunities
- Scheduled date tracking
- Tag support

### 1.6 Event Sources

| Endpoint | Description |
|----------|-------------|
| `/event-sources.get` | Get event source |
| `/event-sources.schedule` | Schedule event source |
| `/event-sources.unschedule` | Unschedule event source |

### 1.7 Incident Management (New Feature)

| Endpoint | Description |
|----------|-------------|
| `/incidents.create` | Create incident |
| `/incidents.delete` | Delete incident |
| `/incidents.get` | Get incident |
| `/incidents.group` | Group incidents by field |
| `/incidents.list` | List incidents |
| `/incidents.update` | Update incident |

**Key Features:**
- Full incident lifecycle: acknowledged, identified, mitigated, resolved
- Severity levels
- Impacted customer tracking
- Post-Incident Analysis (PIA) article linking
- Playbook association
- Related documentation linking
- SLA tracking integration
- Custom fields and schema support
- Sync metadata for external integrations

### 1.8 Custom Link Types

| Endpoint | Description |
|----------|-------------|
| `/link-types.custom.create` | Create custom link type |
| `/link-types.custom.get` | Get custom link type |
| `/link-types.custom.list` | List custom link types |
| `/link-types.custom.update` | Update custom link type |

### 1.9 Metrics & Notifications

| Endpoint | Description |
|----------|-------------|
| `/metrics.devrev.ingest` | Ingest DevRev metrics |
| `/notifications.send` | Send notifications |

### 1.10 Preferences Management

| Endpoint | Description |
|----------|-------------|
| `/preferences.get` | Get user preferences |
| `/preferences.update` | Update user preferences |

### 1.11 Question & Answers

| Endpoint | Description |
|----------|-------------|
| `/question-answers.create` | Create Q&A |
| `/question-answers.delete` | Delete Q&A |
| `/question-answers.get` | Get Q&A |
| `/question-answers.list` | List Q&As |
| `/question-answers.update` | Update Q&A |

### 1.12 AI Recommendations

| Endpoint | Description |
|----------|-------------|
| `/recommendations.chat.completions` | Chat completions API |
| `/recommendations.get-reply` | Get AI-generated reply |

**Key Features:**
- OpenAI-compatible chat completions interface
- Multi-modal support (text and images)
- Role-based messages (system, user, assistant)

### 1.13 Rev User Enhancements

| Endpoint | Description |
|----------|-------------|
| `/rev-users.associations.add` | Add user associations |
| `/rev-users.associations.list` | List user associations |
| `/rev-users.associations.remove` | Remove user associations |
| `/rev-users.delete-personal-data` | Delete personal data (GDPR) |
| `/rev-users.link` | Link rev user to org |
| `/rev-users.personal-data` | Get personal data |
| `/rev-users.unlink` | Unlink rev user from org |

### 1.14 Roles Management

| Endpoint | Description |
|----------|-------------|
| `/roles.apply` | Apply roles |
| `/roles.create` | Create roles |

### 1.15 Schema Management

| Endpoint | Description |
|----------|-------------|
| `/schemas.subtypes.list` | List schema subtypes |

### 1.16 Search Enhancements

| Endpoint | Description |
|----------|-------------|
| `/search.core` | Core search with query language |
| `/search.hybrid` | Hybrid syntactic + semantic search |

**Key Features:**
- Advanced query language support
- Hybrid search combining syntactic and semantic matching
- Namespace-based search

### 1.17 Service Accounts

| Endpoint | Description |
|----------|-------------|
| `/service-accounts.update` | Update service accounts |

### 1.18 SLA Tracker

| Endpoint | Description |
|----------|-------------|
| `/sla-trackers.remove-metric` | Remove metric from SLA tracker |

### 1.19 Snap-ins Management

| Endpoint | Description |
|----------|-------------|
| `/snap-ins.resources` | Get snap-in resources |
| `/snap-ins.update` | Update snap-ins |

### 1.20 Subscribers Management

| Endpoint | Description |
|----------|-------------|
| `/subscribers.get` | Get subscribers |
| `/subscribers.list` | List subscribers |
| `/subscribers.update` | Update subscribers |

### 1.21 Track Events

| Endpoint | Description |
|----------|-------------|
| `/track-events.publish` | Publish tracking events |

### 1.22 Unit of Measurement (UOM) - New Feature

| Endpoint | Description |
|----------|-------------|
| `/uoms.count` | Count UOMs |
| `/uoms.create` | Create UOM |
| `/uoms.delete` | Delete UOM |
| `/uoms.get` | Get UOM |
| `/uoms.list` | List UOMs |
| `/uoms.update` | Update UOM |

**Key Features:**
- Aggregation types: `sum`, `minimum`, `maximum`, `unique_count`, `running_total`, `duration`, `latest`, `oldest`
- Dimension support for grouping metrics
- Product and part association
- Enable/disable toggle for metering pipeline
- Metric scope: `org` or `user` level

### 1.23 Vistas & Widgets

| Endpoint | Description |
|----------|-------------|
| `/vistas.create` | Create vistas |
| `/webhooks.fetch` | Fetch webhook data |
| `/widgets.get` | Get widget details |

### 1.24 Additional Endpoints

| Endpoint | Description |
|----------|-------------|
| `/articles.count` | Count articles |
| `/audit-logs.fetch` | Fetch audit logs |
| `/conversations.export` | Export conversations |
| `/groups.members.count` | Count group members |
| `/record-templates.get` | Get record templates |

---

## 2. Enhanced Schemas in Beta

### 2.1 Account Enhancements

The beta adds to the `account` schema:
- `artifacts` - Attached artifacts
- `custom_fields` - Custom field support
- `custom_schema_fragments` - Schema fragment IDs
- `stock_schema_fragment` - Stock schema fragment
- `subtype` - Custom type subtype
- `tags` - Tag associations

### 2.2 New Object Types

The beta introduces these new atom types:
- `engagement` - Customer engagement tracking
- `incident` - Incident management
- `uom` - Unit of Measurement
- `brand` - Brand management
- `question_answer` - Q&A objects
- `user_preferences` - User preference settings
- `widget` - Dashboard widgets
- `timeline_change_event` - Timeline change tracking

### 2.3 Search Summaries

New search-specific summary types for improved search results:
- `account-search-summary`
- `article-search-summary`
- `artifact-search-summary`
- `comment-search-summary`
- `conversation-search-summary`
- `tag-search-summary`
- `user-search-summary`
- `vista-search-summary`
- `work-search-summary`
- `workflow-search-summary`

### 2.4 Widget & Visualization

Comprehensive widget system:
- `widget-visualization` with types: `bar`, `column`, `table`
- `widget-data-source` with API and Oasis data sources
- `widget-query` with joins and ordering
- `widget-group-by-config`
- `widget-pvp-config` (period vs period)

### 2.5 Task Support

New task-related schemas:
- `task` - Task work item type
- `task-priority` - Task priority levels
- `task-summary`
- `works-create-request-task`
- `works-update-request-task`

### 2.6 Opportunity Enhancements

- `works-create-request-opportunity`
- `works-update-request-opportunity`
- `works-update-request-opportunity-contacts`
- `works-filter-opportunity`

---

## 3. API Response Improvements

### 3.1 New Error Response

- `request-entity-too-large` (413) - Added for payload size limits

### 3.2 Enhanced Account Creation Response

Beta returns `default_rev_org` along with the created account.

### 3.3 Additional Filters

Many list/export endpoints gain new filter options:
- `custom_fields` filtering
- `domains` filtering for accounts
- `owned_by` filtering
- `subtype` filtering
- `tags` filtering

---

## 4. Webhook Enhancements

### 4.1 New Webhook Events

The beta adds webhook events for:
- `incident_created`
- `incident_deleted`
- `incident_updated`
- `question_answer_created`
- `question_answer_deleted`
- `question_answer_updated`

### 4.2 Webhook Configuration

- `webhooks-update-request-headers` - Custom header support
- `webhook-header` schema for header configuration

---

## 5. SLA Enhancements

The beta extends SLA support to incidents:
- `sla-applies-to-type` now includes `incident`
- `sla-selector-applies-to-type` includes `incident`
- `sla-tracker-applies-to-type` includes `incident`

---

## 6. Timeline Enhancements

New timeline-related schemas:
- `timeline-change-event` with event types: `created`, `deleted`, `linked`, `updated`
- `timeline-entry-panel`
- `timeline-reaction`
- `timeline-thread`

---

## 7. Sync & Integration Improvements

### 7.1 Sync Metadata

Enhanced sync support with:
- `create-sync-metadata`
- `update-sync-metadata`
- `sync-unit` management
- `sync-history` tracking
- `sync-run-progress-state`
- `sync-run-started-by`

### 7.2 Staged Info

Support for staged/draft objects:
- `create-staged-info`
- `update-staged-info`
- `staged-info-filter`
- `create-staged-unresolved-field`

---

## 8. Summary of Key New Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Incident Management** | Beta | Full incident lifecycle management with SLA integration |
| **Engagement Tracking** | Beta | Track customer interactions (calls, emails, meetings) |
| **Unit of Measurement** | Beta | Metering and usage tracking with aggregation |
| **Brand Management** | Beta | Multi-brand support for organizations |
| **Hybrid Search** | Beta | Combined syntactic + semantic search |
| **Chat Completions** | Beta | OpenAI-compatible AI interface |
| **Widget System** | Beta | Dashboard visualization components |
| **Task Management** | Beta | Task work item type |
| **GDPR Compliance** | Beta | Personal data deletion for rev users |
| **Custom Link Types** | Beta | User-defined relationship types |

---

## 9. Migration Considerations

When migrating from public to beta API:

1. **New Response Fields**: Account creation now returns `default_rev_org`
2. **Enhanced Filtering**: Many endpoints support additional filter parameters
3. **New Object Types**: Code may need updates to handle new atom types
4. **Webhook Events**: New event types for incidents and Q&A
5. **Error Handling**: Handle new 413 response code

---

## 10. SDK Implementation Recommendations

### 10.1 Service Classes to Add

Based on the new endpoints, the following service classes should be added:

```python
# New service classes for beta API
class BrandsService(BaseService):
    """Brand management operations."""
    pass

class EngagementsService(BaseService):
    """Customer engagement tracking."""
    pass

class IncidentsService(BaseService):
    """Incident management operations."""
    pass

class UomsService(BaseService):
    """Unit of Measurement operations."""
    pass

class QuestionAnswersService(BaseService):
    """Q&A management operations."""
    pass

class RecommendationsService(BaseService):
    """AI recommendations and chat completions."""
    pass

class SubscribersService(BaseService):
    """Subscriber management."""
    pass

class PreferencesService(BaseService):
    """User preferences management."""
    pass
```

### 10.2 Model Classes to Add

New Pydantic models needed:

- `Brand`, `BrandCreate`, `BrandUpdate`
- `Engagement`, `EngagementCreate`, `EngagementUpdate`, `EngagementType`
- `Incident`, `IncidentCreate`, `IncidentUpdate`, `IncidentStage`
- `Uom`, `UomCreate`, `UomUpdate`, `UomAggregationType`
- `QuestionAnswer`, `QuestionAnswerCreate`, `QuestionAnswerUpdate`
- `Widget`, `WidgetVisualization`, `WidgetDataSource`
- `Task`, `TaskPriority`
- `TimelineChangeEvent`

### 10.3 Configuration Updates

The SDK should support API version selection:

```python
from devrev import DevRevClient, APIVersion

# Use public API (default)
client = DevRevClient(api_version=APIVersion.PUBLIC)

# Use beta API
client = DevRevClient(api_version=APIVersion.BETA)
```

### 10.4 Feature Flags

Consider implementing feature detection:

```python
if client.supports_feature("incidents"):
    incidents = client.incidents.list()
```

---

## 11. Complete List of New Endpoints

For reference, here is the complete list of 74 new endpoints in the beta API:

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 1 | `/ai-agents.events.execute-async` | POST | Async AI agent execution |
| 2 | `/airdrop.sync-units.get` | GET/POST | Get sync unit |
| 3 | `/airdrop.sync-units.history` | GET/POST | Sync unit history |
| 4 | `/articles.count` | GET/POST | Count articles |
| 5 | `/audit-logs.fetch` | POST | Fetch audit logs |
| 6 | `/brands.create` | POST | Create brand |
| 7 | `/brands.delete` | POST | Delete brand |
| 8 | `/brands.get` | GET/POST | Get brand |
| 9 | `/brands.list` | GET/POST | List brands |
| 10 | `/brands.update` | POST | Update brand |
| 11 | `/content-template.create` | POST | Create content template |
| 12 | `/content-template.get` | GET/POST | Get content template |
| 13 | `/content-template.list` | GET/POST | List content templates |
| 14 | `/conversations.export` | GET/POST | Export conversations |
| 15 | `/engagements.count` | GET/POST | Count engagements |
| 16 | `/engagements.create` | POST | Create engagement |
| 17 | `/engagements.delete` | POST | Delete engagement |
| 18 | `/engagements.get` | GET/POST | Get engagement |
| 19 | `/engagements.list` | GET/POST | List engagements |
| 20 | `/engagements.update` | POST | Update engagement |
| 21 | `/event-sources.get` | GET/POST | Get event source |
| 22 | `/event-sources.schedule` | POST | Schedule event source |
| 23 | `/event-sources.unschedule` | POST | Unschedule event source |
| 24 | `/groups.members.count` | GET/POST | Count group members |
| 25 | `/incidents.create` | POST | Create incident |
| 26 | `/incidents.delete` | POST | Delete incident |
| 27 | `/incidents.get` | GET/POST | Get incident |
| 28 | `/incidents.group` | GET/POST | Group incidents |
| 29 | `/incidents.list` | GET/POST | List incidents |
| 30 | `/incidents.update` | POST | Update incident |
| 31 | `/link-types.custom.create` | POST | Create custom link type |
| 32 | `/link-types.custom.get` | GET/POST | Get custom link type |
| 33 | `/link-types.custom.list` | GET/POST | List custom link types |
| 34 | `/link-types.custom.update` | POST | Update custom link type |
| 35 | `/metrics.devrev.ingest` | POST | Ingest metrics |
| 36 | `/notifications.send` | POST | Send notifications |
| 37 | `/preferences.get` | GET/POST | Get preferences |
| 38 | `/preferences.update` | POST | Update preferences |
| 39 | `/question-answers.create` | POST | Create Q&A |
| 40 | `/question-answers.delete` | POST | Delete Q&A |
| 41 | `/question-answers.get` | GET/POST | Get Q&A |
| 42 | `/question-answers.list` | GET/POST | List Q&As |
| 43 | `/question-answers.update` | POST | Update Q&A |
| 44 | `/recommendations.chat.completions` | POST | Chat completions |
| 45 | `/recommendations.get-reply` | POST | Get AI reply |
| 46 | `/record-templates.get` | GET/POST | Get record template |
| 47 | `/rev-users.associations.add` | POST | Add user associations |
| 48 | `/rev-users.associations.list` | GET/POST | List user associations |
| 49 | `/rev-users.associations.remove` | POST | Remove user associations |
| 50 | `/rev-users.delete-personal-data` | POST | Delete personal data |
| 51 | `/rev-users.link` | POST | Link rev user |
| 52 | `/rev-users.personal-data` | GET/POST | Get personal data |
| 53 | `/rev-users.unlink` | POST | Unlink rev user |
| 54 | `/roles.apply` | POST | Apply roles |
| 55 | `/roles.create` | POST | Create roles |
| 56 | `/schemas.subtypes.list` | GET/POST | List schema subtypes |
| 57 | `/search.core` | GET/POST | Core search |
| 58 | `/search.hybrid` | GET/POST | Hybrid search |
| 59 | `/service-accounts.update` | POST | Update service account |
| 60 | `/sla-trackers.remove-metric` | POST | Remove SLA metric |
| 61 | `/snap-ins.resources` | POST | Get snap-in resources |
| 62 | `/snap-ins.update` | POST | Update snap-in |
| 63 | `/subscribers.get` | GET/POST | Get subscribers |
| 64 | `/subscribers.list` | GET/POST | List subscribers |
| 65 | `/subscribers.update` | POST | Update subscribers |
| 66 | `/track-events.publish` | POST | Publish track events |
| 67 | `/uoms.count` | GET/POST | Count UOMs |
| 68 | `/uoms.create` | POST | Create UOM |
| 69 | `/uoms.delete` | POST | Delete UOM |
| 70 | `/uoms.get` | GET/POST | Get UOM |
| 71 | `/uoms.list` | GET/POST | List UOMs |
| 72 | `/uoms.update` | POST | Update UOM |
| 73 | `/vistas.create` | POST | Create vista |
| 74 | `/webhooks.fetch` | POST | Fetch webhook |
| 75 | `/widgets.get` | GET/POST | Get widget |

