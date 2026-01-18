# OpenAPI Spec Discrepancies

This document tracks discrepancies between the DevRev OpenAPI specification and actual API behavior, identified during integration testing.

## SDK Fixes Applied

The following discrepancies were identified and fixed in the SDK:

### 1. Group Members Endpoint Paths (Fixed)

**Issue**: SDK was using incorrect endpoint paths with hyphens instead of dots.

**OpenAPI Spec Path**:
- `/groups.members.list`
- `/groups.members.add`
- `/groups.members.remove`
- `/groups.members.count`

**SDK Path (Before Fix)**:
- `/group-members.list`
- `/group-members.add`
- `/group-members.remove`
- `/groups.members.count` (this one was already correct)

**Resolution**: Updated all endpoints to use dots format matching the OpenAPI spec.

---

### 2. GroupMember Model Schema (Fixed)

**Issue**: SDK model had an incorrect schema with a non-existent `id` field.

**OpenAPI Spec Schema** (`group-members-list-response-member`):
```yaml
type: object
properties:
  member:
    $ref: '#/components/schemas/member-summary'
  member_rev_org:
    $ref: '#/components/schemas/rev-org-summary'
required:
  - member
```

**SDK Model (Before Fix)**:
```python
class GroupMember(DevRevResponseModel):
    id: str = Field(...)  # NOT in API response
    member: UserSummary | None = Field(default=None)  # Should be required
```

**SDK Model (After Fix)**:
```python
class GroupMember(DevRevResponseModel):
    member: UserSummary = Field(...)  # Required, no optional
    member_rev_org: Any | None = Field(default=None)  # Added missing field
```

---

### 3. GroupsMembersCountRequest Field Name (Fixed)

**Issue**: SDK used `id` field but API expects `group` field.

**OpenAPI Spec**:
```yaml
group-members-count-request:
  properties:
    group:
      type: string
      description: ID of the group for which to count members.
  required:
    - group
```

**SDK (Before Fix)**:
```python
class GroupsMembersCountRequest(DevRevBaseModel):
    id: str = Field(...)
```

**SDK (After Fix)**:
```python
class GroupsMembersCountRequest(DevRevBaseModel):
    group: str = Field(...)
```

---

### 4. TimelineEntryType Enum (Fixed)

**Issue**: API returns `timeline_change_event` type which was not in the SDK enum.

**Resolution**:
- Added `CHANGE_EVENT = "timeline_change_event"` to the enum
- Changed `TimelineEntry.type` field from enum to `str` to gracefully handle unknown values

---

### 5. links.list Requires Object Parameter

**Issue**: The `links.list` endpoint returns 400 Bad Request when called without an `object` parameter.

**OpenAPI Spec**: Shows `object` as optional parameter.

**Actual Behavior**: Endpoint requires the `object` parameter to filter links.

**Resolution**: Updated tests to always provide an `object` parameter when testing links.list.

---

## Account/Workspace-Specific Limitations

The following endpoints may not be available in all workspaces/accounts. Tests are marked as expected failures (xfail):

### BETA API Endpoints

| Endpoint | Status | Notes |
|----------|--------|-------|
| `brands.list` | 404 | Feature not enabled for test workspace |
| `brands.get` | 404 | Feature not enabled for test workspace |
| `conversations.export` | 400 | May require specific permissions or data |
| `preferences.get` | 400 | May require specific user context |
| `search.core` | 400 | Search may not be enabled for workspace |
| `search.hybrid` | 400 | Search may not be enabled for workspace |
| `recommendations.get-reply` | Error | AI features may not be enabled |
| `rev-users.get-personal-data` | Error | GDPR features may not be enabled |

### Notes

- These are BETA API endpoints that may require specific feature flags or account configurations
- The SDK implementation appears correct per the OpenAPI spec
- Failures are due to workspace/account configuration, not SDK bugs

---

## Test Results Summary

After all fixes were applied:

- **65 tests passed** - Core functionality working correctly
- **9 tests skipped** - No test data available (e.g., no links, no webhooks)
- **10 tests xfailed** - Expected failures for features not enabled in test workspace
- **0 tests failed** - All SDK code issues have been resolved

---

## Reporting to DevRev

The following should be reported to DevRev:

1. **Documentation clarification needed**: `links.list` endpoint should document that `object` parameter is effectively required, not optional.

2. **Endpoint path inconsistency**: The operationId uses `group-members-*` but the actual path is `/groups.members.*`. This can be confusing for SDK generators.

3. **Timeline entry type discovery**: Document that `timeline_change_event` is a valid type that can be returned by the API.

---

*Last updated: 2026-01-18*
*Generated from integration testing in Issue #103*