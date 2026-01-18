# Schema Fixes Required - Summary

**Date**: 2026-01-18  
**Test Suite**: `tests/integration/test_all_readonly_endpoints.py`  
**Test Results**: 10 PASSED, 6 FAILED  
**Unique Schema Issues Found**: 3

---

## Test Results Summary

```
✅ PASSED (10):
- works.count
- tags.list  
- parts.list
- dev-users.list
- rev-users.list
- articles.count
- conversations.list
- groups.list
- webhooks.list
- slas.list

❌ FAILED (6):
- accounts.list (TagWithValue.tag type mismatch)
- accounts.export (TagWithValue.tag type mismatch)
- works.list (TagWithValue.tag type mismatch)
- works.export (TagWithValue.tag type mismatch)
- articles.list (Article.authored_by type mismatch)
- conversations.export (Bad Request 400)
```

---

## Issue #1: TagWithValue.tag Field Type Mismatch 🔴 CRITICAL

### Affected Endpoints
- `accounts.list`
- `accounts.export`
- `works.list`
- `works.export`
- Any endpoint returning objects with tags

### Current Model
<augment_code_snippet path="src/devrev/models/base.py" mode="EXCERPT">
````python
class TagWithValue(DevRevResponseModel):
    """Tag with value for resource tagging."""
    
    tag: str = Field(..., description="Tag name or ID")
    value: str | None = Field(default=None, description="Tag value")
````
</augment_code_snippet>

### Actual API Response
```json
{
  "tag": {
    "display_id": "TAG-6",
    "name": "SalesforceService import",
    "description": "item imported from external source",
    "color": "#AAF0BD"
  },
  "value": null
}
```

### Required Fix
```python
from devrev.models.tags import Tag

class TagWithValue(DevRevResponseModel):
    """Tag with value for resource tagging."""
    
    tag: Tag | str = Field(..., description="Tag object or ID")
    value: str | None = Field(default=None, description="Tag value")
```

### Files to Update
- `src/devrev/models/base.py` - Update TagWithValue model
- Need to import Tag model (circular import consideration)

---

## Issue #2: Article.authored_by Field Type Mismatch 🔴 CRITICAL

### Affected Endpoints
- `articles.list`

### Current Model
Expected: `UserSummary` (single object)

### Actual API Response
Returns: `list[UserSummary]` (array of objects)

```json
{
  "authored_by": [
    {
      "type": "sys_user",
      "display_id": "DEVU-1",
      "state": "active"
    }
  ]
}
```

### Required Fix
Update Article model to accept list of UserSummary:

```python
class Article(DevRevResponseModel):
    # ... other fields ...
    authored_by: list[UserSummary] | None = Field(
        default=None, 
        description="Authors of the article"
    )
```

### Files to Update
- `src/devrev/models/articles.py` - Update Article model

---

## Issue #3: conversations.export Bad Request 🟡 MEDIUM

### Affected Endpoints
- `conversations.export`

### Error
```
devrev.exceptions.ValidationError: Bad Request | Status: 400
```

### Analysis
This appears to be an API endpoint issue, not a schema issue. Possible causes:
1. Missing required parameters
2. Endpoint requires specific permissions
3. Endpoint may not be available in current API version

### Required Investigation
- Check DevRev API documentation for conversations.export requirements
- Verify required parameters
- Check if endpoint is deprecated or requires special access

### Files to Update
- `src/devrev/services/conversations.py` - May need parameter updates
- `tests/integration/test_all_readonly_endpoints.py` - Update test with correct parameters

---

## OpenAPI Spec Corrections Needed

### For DevRev Team

The following corrections are needed in the OpenAPI specification:

#### 1. TagWithValue Schema

**Current Spec**:
```yaml
TagWithValue:
  type: object
  properties:
    tag:
      type: string
      description: Tag name or ID
    value:
      type: string
      nullable: true
```

**Corrected Spec**:
```yaml
TagWithValue:
  type: object
  properties:
    tag:
      oneOf:
        - type: string
        - $ref: '#/components/schemas/Tag'
      description: Tag object or ID (full Tag object is returned in list/export responses)
    value:
      type: string
      nullable: true
```

#### 2. Article Schema

**Current Spec**:
```yaml
Article:
  properties:
    authored_by:
      $ref: '#/components/schemas/UserSummary'
```

**Corrected Spec**:
```yaml
Article:
  properties:
    authored_by:
      type: array
      items:
        $ref: '#/components/schemas/UserSummary'
      description: List of authors
```

---

## Implementation Plan

### Phase 1: Fix Critical Issues (Priority: P0)

1. **Fix TagWithValue model**
   - Update `src/devrev/models/base.py`
   - Handle circular import with Tag model
   - Run tests to verify fix

2. **Fix Article.authored_by model**
   - Update `src/devrev/models/articles.py`
   - Run tests to verify fix

### Phase 2: Investigate conversations.export (Priority: P1)

3. **Debug conversations.export**
   - Review API documentation
   - Test with different parameters
   - Update service or test as needed

### Phase 3: Verify All Fixes (Priority: P0)

4. **Run full integration test suite**
   ```bash
   pytest tests/integration/test_all_readonly_endpoints.py -v
   ```
   - Target: All 16 tests passing

5. **Run existing integration tests**
   ```bash
   pytest tests/integration/test_readonly_endpoints.py -v
   ```
   - Ensure no regressions

---

## Next Steps

1. ✅ Create comprehensive integration test suite
2. ✅ Document all schema discrepancies
3. ⏳ Fix TagWithValue model
4. ⏳ Fix Article.authored_by model
5. ⏳ Investigate conversations.export
6. ⏳ Verify all tests pass
7. ⏳ Update OPENAPI_SPEC_DISCREPANCIES.md with final report
8. ⏳ Submit report to DevRev for OpenAPI spec corrections

---

## Related Files

- `tests/integration/test_all_readonly_endpoints.py` - Comprehensive test suite
- `OPENAPI_SPEC_DISCREPANCIES.md` - Auto-generated detailed report
- `src/devrev/models/base.py` - TagWithValue model
- `src/devrev/models/articles.py` - Article model
- `src/devrev/services/conversations.py` - Conversations service
- GitHub Issue [#102](https://github.com/mgmonteleone/py-dev-rev/issues/102)

