# Implementation Plan: Fix Schema Mismatches

**Goal**: Fix all schema mismatches to work with actual DevRev API responses

**Scope**: 
- Fix models to match actual API responses
- Update mocks to match real API behavior
- Create proposed OpenAPI spec corrections
- Test against both PUBLIC and BETA APIs

---

## Phase 1: Fix Critical Schema Issues ⏳

### Task 1.1: Fix TagWithValue Model
**File**: `src/devrev/models/base.py`

**Current**:
```python
class TagWithValue(DevRevResponseModel):
    tag: str = Field(..., description="Tag name or ID")
    value: str | None = Field(default=None, description="Tag value")
```

**Fix**:
```python
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from devrev.models.tags import Tag

class TagWithValue(DevRevResponseModel):
    tag: Union["Tag", str] = Field(..., description="Tag object or ID")
    value: str | None = Field(default=None, description="Tag value")
```

**Reason**: API returns full Tag object, not just string ID

**Affected Endpoints**: accounts.list, accounts.export, works.list, works.export

---

### Task 1.2: Fix Article.authored_by Model
**File**: `src/devrev/models/articles.py`

**Current**:
```python
class Article(DevRevResponseModel):
    authored_by: UserSummary | None = Field(...)
```

**Fix**:
```python
class Article(DevRevResponseModel):
    authored_by: list[UserSummary] | None = Field(
        default=None,
        description="Authors of the article"
    )
```

**Reason**: API returns array of UserSummary, not single object

**Affected Endpoints**: articles.list

---

### Task 1.3: Investigate conversations.export
**File**: `src/devrev/services/conversations.py`

**Issue**: Returns 400 Bad Request

**Actions**:
1. Check DevRev API documentation for required parameters
2. Test with different parameter combinations
3. Verify endpoint is available in PUBLIC API
4. Update service or test as needed

---

## Phase 2: Update Mocks ⏳

### Task 2.1: Update Mock Responses for TagWithValue
**Files**: 
- `tests/unit/services/test_accounts.py`
- `tests/unit/services/test_works.py`
- Any other tests using TagWithValue

**Action**: Update mock responses to return Tag objects instead of strings

**Example**:
```python
# OLD
"tags": [{"tag": "TAG:123", "value": "test"}]

# NEW
"tags": [{
    "tag": {
        "id": "TAG:123",
        "display_id": "TAG-1",
        "name": "Test Tag",
        "color": "#AAF0BD"
    },
    "value": "test"
}]
```

---

### Task 2.2: Update Mock Responses for Article.authored_by
**Files**: `tests/unit/services/test_articles.py`

**Action**: Update mock responses to return array of UserSummary

**Example**:
```python
# OLD
"authored_by": {"id": "DEVU-1", "display_id": "DEVU-1"}

# NEW
"authored_by": [{"id": "DEVU-1", "display_id": "DEVU-1", "type": "sys_user"}]
```

---

## Phase 3: Test Against Both APIs ⏳

### Task 3.1: Create BETA API Integration Tests
**File**: `tests/integration/test_all_readonly_endpoints_beta.py`

**Action**: Duplicate test suite but use `APIVersion.BETA`

**Purpose**: Verify if schema issues exist in BETA API too

---

### Task 3.2: Run Comprehensive Tests
**Commands**:
```bash
# Test PUBLIC API
pytest tests/integration/test_all_readonly_endpoints.py -v

# Test BETA API
pytest tests/integration/test_all_readonly_endpoints_beta.py -v

# Compare results
```

---

## Phase 4: Create Proposed OpenAPI Spec ⏳

### Task 4.1: Generate Corrected OpenAPI Spec
**File**: `openapi-spec-corrections.yaml`

**Action**: Create YAML file with corrected schemas

**Sections to Include**:
1. TagWithValue schema correction
2. Article.authored_by schema correction
3. Any other discrepancies found

**Format**:
```yaml
# Corrected OpenAPI Spec for DevRev API
# Based on actual API responses observed 2026-01-18

components:
  schemas:
    TagWithValue:
      type: object
      properties:
        tag:
          oneOf:
            - type: string
              description: Tag ID (when used in requests)
            - $ref: '#/components/schemas/Tag'
              description: Full Tag object (returned in responses)
        value:
          type: string
          nullable: true
          description: Optional tag value
      required:
        - tag
    
    Article:
      type: object
      properties:
        authored_by:
          type: array
          items:
            $ref: '#/components/schemas/UserSummary'
          description: List of article authors
          nullable: true
```

---

## Phase 5: Update Documentation ⏳

### Task 5.1: Update OPENAPI_SPEC_DISCREPANCIES.md
**Action**: Add final test results and proposed fixes

### Task 5.2: Update GitHub Issue #102
**Action**: Add implementation progress and results

### Task 5.3: Create DevRev Feedback Document
**File**: `DEVREV_OPENAPI_FEEDBACK.md`

**Content**:
- Summary of all discrepancies
- Proposed OpenAPI spec corrections
- Test methodology
- Request for spec update

---

## Execution Order

1. ✅ Create comprehensive integration tests
2. ✅ Document all schema discrepancies
3. ⏳ **Fix TagWithValue model** (Task 1.1)
4. ⏳ **Fix Article.authored_by model** (Task 1.2)
5. ⏳ **Update mocks** (Task 2.1, 2.2)
6. ⏳ **Run tests - verify all pass** (Phase 3)
7. ⏳ **Investigate conversations.export** (Task 1.3)
8. ⏳ **Create proposed OpenAPI spec** (Task 4.1)
9. ⏳ **Update documentation** (Phase 5)
10. ⏳ **Submit feedback to DevRev**

---

## Success Criteria

- [ ] All 16 integration tests pass (PUBLIC API)
- [ ] All unit tests pass with updated mocks
- [ ] BETA API tests created and results documented
- [ ] Proposed OpenAPI spec created
- [ ] Documentation updated
- [ ] Feedback submitted to DevRev

---

## Files to Create/Update

### New Files
- `openapi-spec-corrections.yaml` - Proposed OpenAPI corrections
- `tests/integration/test_all_readonly_endpoints_beta.py` - BETA API tests
- `DEVREV_OPENAPI_FEEDBACK.md` - Feedback for DevRev team

### Files to Update
- `src/devrev/models/base.py` - TagWithValue model
- `src/devrev/models/articles.py` - Article model
- `tests/unit/services/test_accounts.py` - Update mocks
- `tests/unit/services/test_works.py` - Update mocks
- `tests/unit/services/test_articles.py` - Update mocks
- `OPENAPI_SPEC_DISCREPANCIES.md` - Final results
- GitHub Issue #102 - Progress updates

