# Integration Test Coverage Analysis
**Date**: 2026-01-18  
**Goal**: Achieve 100% coverage of non-destructive (read-only) endpoints

---

## Summary

### Current Coverage: 16/60+ endpoints (27%)

**Currently Tested** (16 endpoints):
- ✅ accounts.list
- ✅ accounts.export
- ✅ works.list
- ✅ works.export
- ✅ works.count
- ✅ tags.list
- ✅ parts.list
- ✅ dev-users.list
- ✅ rev-users.list
- ✅ articles.list
- ✅ articles.count
- ✅ conversations.list
- ⚠️ conversations.export (400 error)
- ✅ groups.list
- ✅ webhooks.list
- ✅ slas.list

---

## Complete Inventory of Read-Only Endpoints

### 1. Accounts Service (3 endpoints)
- ✅ **accounts.list** - TESTED
- ✅ **accounts.export** - TESTED
- ⬜ **accounts.get** - NOT TESTED

### 2. Works Service (4 endpoints)
- ✅ **works.list** - TESTED
- ✅ **works.export** - TESTED
- ✅ **works.count** - TESTED
- ⬜ **works.get** - NOT TESTED

### 3. Tags Service (2 endpoints)
- ✅ **tags.list** - TESTED
- ⬜ **tags.get** - NOT TESTED

### 4. Parts Service (2 endpoints)
- ✅ **parts.list** - TESTED
- ⬜ **parts.get** - NOT TESTED

### 5. Dev Users Service (2 endpoints)
- ✅ **dev-users.list** - TESTED
- ⬜ **dev-users.get** - NOT TESTED

### 6. Rev Users Service (3 endpoints)
- ✅ **rev-users.list** - TESTED
- ⬜ **rev-users.get** - NOT TESTED
- ⬜ **rev-users.get-personal-data** - NOT TESTED (beta only)

### 7. Articles Service (3 endpoints)
- ✅ **articles.list** - TESTED
- ✅ **articles.count** - TESTED
- ⬜ **articles.get** - NOT TESTED

### 8. Conversations Service (3 endpoints)
- ✅ **conversations.list** - TESTED
- ⚠️ **conversations.export** - TESTED (400 error)
- ⬜ **conversations.get** - NOT TESTED

### 9. Groups Service (4 endpoints)
- ✅ **groups.list** - TESTED
- ⬜ **groups.get** - NOT TESTED
- ⬜ **group-members.list** - NOT TESTED
- ⬜ **group-members.count** - NOT TESTED

### 10. Webhooks Service (2 endpoints)
- ✅ **webhooks.list** - TESTED
- ⬜ **webhooks.get** - NOT TESTED

### 11. SLAs Service (2 endpoints)
- ✅ **slas.list** - TESTED
- ⬜ **slas.get** - NOT TESTED

### 12. Timeline Entries Service (2 endpoints)
- ⬜ **timeline-entries.list** - NOT TESTED
- ⬜ **timeline-entries.get** - NOT TESTED

### 13. Links Service (2 endpoints)
- ⬜ **links.list** - NOT TESTED
- ⬜ **links.get** - NOT TESTED

### 14. Code Changes Service (2 endpoints)
- ⬜ **code-changes.list** - NOT TESTED
- ⬜ **code-changes.get** - NOT TESTED

### 15. Brands Service (2 endpoints)
- ⬜ **brands.list** - NOT TESTED
- ⬜ **brands.get** - NOT TESTED

### 16. Engagements Service (3 endpoints)
- ⬜ **engagements.list** - NOT TESTED
- ⬜ **engagements.get** - NOT TESTED
- ⬜ **engagements.count** - NOT TESTED

### 17. Incidents Service (2 endpoints)
- ⬜ **incidents.list** - NOT TESTED
- ⬜ **incidents.get** - NOT TESTED

### 18. Search Service (2 endpoints)
- ⬜ **search.core** - NOT TESTED
- ⬜ **search.hybrid** - NOT TESTED

### 19. Preferences Service (1 endpoint)
- ⬜ **preferences.get** - NOT TESTED

### 20. Question Answers Service (2 endpoints)
- ⬜ **question-answers.list** - NOT TESTED
- ⬜ **question-answers.get** - NOT TESTED

### 21. Recommendations Service (1 endpoint)
- ⬜ **recommendations.get-reply** - NOT TESTED (AI-based, may need special handling)

### 22. UOMs Service (3 endpoints)
- ⬜ **uoms.list** - NOT TESTED
- ⬜ **uoms.get** - NOT TESTED
- ⬜ **uoms.count** - NOT TESTED

---

## Coverage Statistics

### By Service Type

| Service | Total Read-Only | Tested | Coverage |
|---------|----------------|--------|----------|
| Accounts | 3 | 2 | 67% |
| Works | 4 | 3 | 75% |
| Tags | 2 | 1 | 50% |
| Parts | 2 | 1 | 50% |
| Dev Users | 2 | 1 | 50% |
| Rev Users | 3 | 1 | 33% |
| Articles | 3 | 2 | 67% |
| Conversations | 3 | 2 | 67% |
| Groups | 4 | 1 | 25% |
| Webhooks | 2 | 1 | 50% |
| SLAs | 2 | 1 | 50% |
| Timeline Entries | 2 | 0 | 0% |
| Links | 2 | 0 | 0% |
| Code Changes | 2 | 0 | 0% |
| Brands | 2 | 0 | 0% |
| Engagements | 3 | 0 | 0% |
| Incidents | 2 | 0 | 0% |
| Search | 2 | 0 | 0% |
| Preferences | 1 | 0 | 0% |
| Question Answers | 2 | 0 | 0% |
| Recommendations | 1 | 0 | 0% |
| UOMs | 3 | 0 | 0% |
| **TOTAL** | **60+** | **16** | **~27%** |

---

## Priority for Additional Testing

### High Priority (Core Resources)
These are commonly used endpoints that should be tested first:

1. **GET endpoints for existing tested services**:
   - accounts.get
   - works.get
   - parts.get
   - dev-users.get
   - rev-users.get
   - articles.get
   - conversations.get
   - groups.get
   - webhooks.get
   - slas.get

2. **Timeline Entries** (commonly used):
   - timeline-entries.list
   - timeline-entries.get

3. **Links** (commonly used):
   - links.list
   - links.get

### Medium Priority (Extended Features)
4. **Code Changes**:
   - code-changes.list
   - code-changes.get

5. **Brands**:
   - brands.list
   - brands.get

6. **Engagements**:
   - engagements.list
   - engagements.get
   - engagements.count

7. **Incidents**:
   - incidents.list
   - incidents.get

8. **UOMs**:
   - uoms.list
   - uoms.get
   - uoms.count

9. **Group Members**:
   - group-members.list
   - group-members.count

### Lower Priority (Specialized)
10. **Search** (complex, may need special test data):
    - search.core
    - search.hybrid

11. **Preferences**:
    - preferences.get

12. **Question Answers**:
    - question-answers.list
    - question-answers.get

13. **Recommendations** (AI-based):
    - recommendations.get-reply

---

## Next Steps

### Phase 1: Complete Core Services (Target: 40 endpoints)
Add tests for all `.get()` methods of currently tested services:
- accounts.get
- works.get
- tags.get
- parts.get
- dev-users.get
- rev-users.get
- articles.get
- conversations.get
- groups.get
- webhooks.get
- slas.get

Plus:
- timeline-entries.list
- timeline-entries.get
- links.list
- links.get
- group-members.list
- group-members.count

**Estimated Coverage After Phase 1**: 40/60+ = 67%

### Phase 2: Extended Services (Target: 55 endpoints)
Add tests for:
- code-changes.list, code-changes.get
- brands.list, brands.get
- engagements.list, engagements.get, engagements.count
- incidents.list, incidents.get
- uoms.list, uoms.get, uoms.count
- question-answers.list, question-answers.get
- preferences.get

**Estimated Coverage After Phase 2**: 55/60+ = 92%

### Phase 3: Specialized Services (Target: 100%)
Add tests for:
- search.core
- search.hybrid
- recommendations.get-reply
- rev-users.get-personal-data (beta)

**Estimated Coverage After Phase 3**: 60+/60+ = 100%

---

## Test Data Requirements

To test `.get()` endpoints, we need valid IDs. Strategy:

1. **Use `.list()` to get IDs**: For each service, call `.list()` first to get valid IDs
2. **Skip if empty**: If `.list()` returns no results, skip `.get()` test
3. **Use first result**: Use the first item from `.list()` for `.get()` test

Example pattern:
```python
def test_accounts_get(self, client: DevRevClient) -> None:
    # Get a valid ID from list
    list_result = client.accounts.list(limit=1)
    if not list_result.accounts:
        pytest.skip("No accounts available for testing")
    
    account_id = list_result.accounts[0].id
    
    # Test get
    result = client.accounts.get(account_id)
    assert result.id == account_id
```

---

## Recommendations

1. **Immediate**: Add Phase 1 tests (`.get()` methods) - Low effort, high value
2. **Short-term**: Add Phase 2 tests (extended services) - Medium effort, good coverage
3. **Long-term**: Add Phase 3 tests (specialized) - Higher effort, complete coverage
4. **Continuous**: Update tests as new endpoints are added to SDK

