# Known Issues

This document tracks known issues with the DevRev API and SDK that are expected failures in integration tests.

## Overview

The following issues are **not SDK bugs** - they are limitations of the DevRev API, workspace configuration requirements, or features that require specific enablement. Tests for these endpoints are marked with `@pytest.mark.xfail` to document their expected behavior.

---

## API Issues

### 1. `question-answers.get` - API Bug

| Endpoint | `question-answers.get` |
|----------|------------------------|
| **Status** | 400 Bad Request |
| **API Version** | PUBLIC |
| **Issue** | Returns 400 regardless of input parameters |
| **Test** | `test_extended_services_phase2.py::TestQuestionAnswersEndpoints::test_question_answers_get` |

**Details:**
The `question-answers.get` endpoint returns a 400 Bad Request error for all inputs, including valid question answer IDs obtained from `question-answers.list`. This appears to be a DevRev API bug.

```bash
# Example - even valid IDs fail
curl -X GET "https://api.devrev.ai/question-answers.get?id=don:core:dvrv-us-1:devo/xxx:question_answer/1" \
  -H "Authorization: Bearer $TOKEN"
# Response: {"message": "Bad Request", "type": "bad_request"}
```

---

## Workspace/Feature Configuration Issues

### 2. `brands.list` / `brands.get` - Feature Not Enabled

| Endpoint | `brands.list`, `brands.get` |
|----------|------------------------------|
| **Status** | 404 Not Found |
| **API Version** | BETA |
| **Issue** | Brands feature not enabled for workspace |
| **Tests** | `test_extended_services_phase2.py::TestBrandsEndpoints::test_brands_list/get` |

**Details:**
The Brands API returns 404, indicating this feature is not enabled for the test workspace. Brands is a BETA feature that may require explicit enablement.

---

### 3. `preferences.get` - User Context Required

| Endpoint | `preferences.get` |
|----------|-------------------|
| **Status** | 400 Bad Request |
| **API Version** | BETA |
| **Issue** | Requires specific user context or permissions |
| **Test** | `test_extended_services_phase2.py::TestPreferencesEndpoints::test_preferences_get` |

**Details:**
The Preferences API requires specific user context that may not be available with a service account token.

---

### 4. `search.core` / `search.hybrid` - Search Not Enabled

| Endpoint | `search.core`, `search.hybrid` |
|----------|--------------------------------|
| **Status** | 400 Bad Request |
| **API Version** | BETA |
| **Issue** | Search feature not enabled for workspace |
| **Tests** | `test_specialized_services_phase3.py::TestSearchEndpoints::test_search_*` |

**Details:**
The Search API (both core and hybrid) returns 400. This is an AI-powered feature that may require:
- Workspace-level enablement
- Indexing to be configured
- Specific plan/tier

---

### 5. `recommendations.get-reply` - AI Features Required

| Endpoint | `recommendations.get-reply` |
|----------|------------------------------|
| **Status** | 400 Bad Request |
| **API Version** | BETA |
| **Issue** | AI recommendation features not enabled |
| **Test** | `test_specialized_services_phase3.py::TestRecommendationsEndpoints::test_recommendations_get_reply` |

**Details:**
The Recommendations API is an AI-based endpoint that requires specific setup or plan features to be enabled.

---

### 6. `rev-users.get-personal-data` - GDPR Features Required

| Endpoint | `rev-users.get-personal-data` |
|----------|-------------------------------|
| **Status** | 400 Bad Request |
| **API Version** | BETA |
| **Issue** | GDPR compliance features not enabled |
| **Test** | `test_specialized_services_phase3.py::TestBetaEndpoints::test_rev_users_get_personal_data` |

**Details:**
This endpoint is designed for GDPR data export compliance and may require specific compliance features to be enabled in the workspace.

---

### 7. `conversations.export` - Specific Permissions Required

| Endpoint | `conversations.export` |
|----------|------------------------|
| **Status** | 400 Bad Request |
| **API Version** | BETA |
| **Issue** | Requires specific permissions or conversation data |
| **Test** | `test_all_readonly_endpoints.py::TestConversationsReadOnly::test_conversations_export` |

**Details:**
The conversations export endpoint requires specific permissions that may not be available with a standard API token.

---

## Skipped Tests (Not xfail)

These tests are skipped rather than xfailed because they require specific test data:

| Test | Reason |
|------|--------|
| `test_code_changes_get` | Requires GitHub integration to be connected and syncing data |
| `test_conversations_export_known_issue` | Duplicate test documenting known issue |

---

## Summary

| Category | Count | Description |
|----------|-------|-------------|
| API Bugs | 1 | `question-answers.get` returns 400 for all inputs |
| Feature Not Enabled | 6 | Workspace features not configured |
| Missing Test Data | 2 | GitHub integration, specific data required |

**Total xfailed tests:** 11
**Total skipped tests:** 2

---

## Resolution

To resolve these issues:

1. **API Bugs** - Report to DevRev support
2. **Feature Not Enabled** - Enable features in DevRev workspace settings
3. **Missing Test Data** - Connect required integrations or create test data

---

*Last updated: 2026-01-18*

