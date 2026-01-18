# Integration Testing Strategy for Write Operations

This document provides a comprehensive strategy for implementing integration tests for write operations (create, update, delete) in the DevRev SDK.

## Table of Contents

- [Overview](#overview)
- [Test Data Management Strategy](#test-data-management-strategy)
- [Write Operation Coverage](#write-operation-coverage)
- [Data Lifecycle Management](#data-lifecycle-management)
- [Security and Safety](#security-and-safety)
- [Implementation Plan](#implementation-plan)
- [Code Examples](#code-examples)

## Overview

Write operation integration tests require special handling to ensure:

1. **Data isolation** - Tests don't interfere with each other or production data
2. **Automatic cleanup** - Test data is always removed after tests complete
3. **Auditability** - Clear trail of what test data was created
4. **Safety** - Safeguards against accidental production execution

## Test Data Management Strategy

### Naming Conventions

All test data MUST use consistent naming to enable identification and cleanup:

```python
# Prefix pattern for all test entities
TEST_PREFIX = "SDK_TEST_"

# Include run ID for isolation between concurrent runs
RUN_ID = uuid.uuid4().hex[:8]

# Final naming pattern
f"{TEST_PREFIX}{RUN_ID}_{entity_name}"
# Example: "SDK_TEST_a1b2c3d4_MyTestAccount"
```

### Test Data Manager

A centralized `TestDataManager` class tracks all created resources:

```python
class TestDataManager:
    """Manages test data lifecycle with automatic cleanup."""
    
    def __init__(self, client: DevRevClient):
        self.client = client
        self.run_id = uuid.uuid4().hex[:8]
        self._created_resources: list[tuple[str, str]] = []  # (type, id)
    
    def generate_name(self, base_name: str) -> str:
        """Generate a unique test name with proper prefix."""
        return f"SDK_TEST_{self.run_id}_{base_name}"
    
    def register(self, resource_type: str, resource_id: str) -> None:
        """Register a created resource for cleanup."""
        self._created_resources.append((resource_type, resource_id))
    
    def cleanup(self) -> CleanupReport:
        """Delete all registered resources in reverse order."""
        # Cleanup in reverse order (LIFO) to handle dependencies
        ...
```

### Isolation Strategy

```python
@pytest.fixture(scope="function")
def test_data(client: DevRevClient) -> Generator[TestDataManager, None, None]:
    """Provide isolated test data manager per test."""
    manager = TestDataManager(client)
    yield manager
    manager.cleanup()  # Always cleanup, even on test failure
```

## Write Operation Coverage

### Services with Write Operations

| Service | Create | Update | Delete | Notes |
|---------|--------|--------|--------|-------|
| Accounts | ✅ | ✅ | ✅ | Full CRUD |
| Works | ✅ | ✅ | ✅ | Full CRUD |
| Tags | ✅ | ✅ | ✅ | Full CRUD |
| Articles | ✅ | ✅ | ✅ | Full CRUD |
| Groups | ✅ | ✅ | ✅ | Full CRUD |
| Webhooks | ✅ | ✅ | ✅ | Full CRUD |
| Parts | ✅ | ✅ | ✅ | Full CRUD |
| Conversations | ✅ | ✅ | ❌ | No delete |
| Links | ✅ | ❌ | ✅ | No update |
| Rev Users | ✅ | ✅ | ✅ | Full CRUD |
| Dev Users | ✅ | ✅ | ✅ | Full CRUD (limited in test) |

### Test Scenarios per Operation

#### Create Operations
- Valid creation with required fields only
- Valid creation with all optional fields
- Invalid creation (missing required fields) - expect error
- Duplicate creation (where applicable) - expect error

#### Update Operations  
- Valid update of single field
- Valid update of multiple fields
- Update non-existent resource - expect error
- Invalid update (bad field values) - expect error

#### Delete Operations
- Valid deletion of existing resource
- Delete non-existent resource - expect error
- Delete resource with dependencies (if applicable)

## Data Lifecycle Management

### Setup/Teardown Pattern

```python
class TestAccountsCRUD:
    """CRUD tests for Accounts with proper lifecycle management."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self, test_data: TestDataManager):
        """Setup and teardown for each test."""
        self.test_data = test_data
        yield
        # Teardown happens automatically via test_data fixture

    def test_create_account(self):
        account = self.test_data.create_account(
            display_name=self.test_data.generate_name("TestAccount")
        )
        assert account.id is not None
        # Resource automatically cleaned up after test
```

### Rollback Mechanism

```python
class TestDataManager:
    def cleanup(self) -> CleanupReport:
        """Cleanup with error handling and reporting."""
        report = CleanupReport()
        
        for resource_type, resource_id in reversed(self._created_resources):
            try:
                self._delete_resource(resource_type, resource_id)
                report.add_success(resource_type, resource_id)
            except Exception as e:
                report.add_failure(resource_type, resource_id, str(e))
                logger.warning(f"Failed to cleanup {resource_type}/{resource_id}: {e}")
        
        return report
```

### Orphan Detection

```python
def detect_orphaned_test_data(client: DevRevClient) -> list[OrphanedResource]:
    """Find test data that wasn't cleaned up properly."""
    orphans = []
    
    # Check each resource type for SDK_TEST_ prefix
    for account in client.accounts.list():
        if account.display_name.startswith("SDK_TEST_"):
            orphans.append(OrphanedResource("account", account.id, account.display_name))
    
    # ... check other resource types
    return orphans
```

## Security and Safety

### Environment Safeguards

```python
# tests/integration/conftest.py

def pytest_configure(config: pytest.Config) -> None:
    """Validate environment before running write tests."""
    # Require explicit opt-in for write tests
    if not os.environ.get("DEVREV_WRITE_TESTS_ENABLED"):
        pytest.skip("Write tests require DEVREV_WRITE_TESTS_ENABLED=true")

    # Verify we're not pointing at production
    base_url = os.environ.get("DEVREV_BASE_URL", "")
    if "prod" in base_url.lower():
        raise RuntimeError("Write tests cannot run against production!")

@pytest.fixture
def write_client() -> DevRevClient:
    """Client configured for write tests with validation."""
    token = os.environ.get("DEVREV_TEST_API_TOKEN")
    if not token:
        pytest.skip("DEVREV_TEST_API_TOKEN required for write tests")

    return DevRevClient(api_token=token)
```

### Rate Limiting

```python
class RateLimitedTestDataManager(TestDataManager):
    """Test data manager with rate limiting for API protection."""

    def __init__(self, client: DevRevClient, requests_per_second: float = 2.0):
        super().__init__(client)
        self._min_interval = 1.0 / requests_per_second
        self._last_request = 0.0

    def _throttle(self) -> None:
        """Ensure minimum interval between requests."""
        elapsed = time.time() - self._last_request
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request = time.time()
```

### CI/CD Configuration

```yaml
# .github/workflows/integration-tests.yml
write-tests:
  runs-on: ubuntu-latest
  # Only run on explicit trigger or scheduled
  if: github.event_name == 'workflow_dispatch' || github.event_name == 'schedule'

  environment: testing  # Requires approval for production-like envs

  steps:
    - name: Run write operation tests
      env:
        DEVREV_TEST_API_TOKEN: ${{ secrets.DEVREV_TEST_API_TOKEN }}
        DEVREV_WRITE_TESTS_ENABLED: "true"
        DEVREV_BASE_URL: ${{ secrets.DEVREV_TEST_BASE_URL }}
      run: |
        pytest tests/integration/test_write_operations.py -v -m write
```

## Implementation Plan

### Phase 1: Foundation (Week 1)
1. Create `TestDataManager` class with basic CRUD tracking
2. Implement naming conventions and run isolation
3. Create base fixtures in conftest.py
4. Add environment safeguards

### Phase 2: Core Write Tests (Week 2)
1. Implement Account CRUD tests
2. Implement Tag CRUD tests
3. Implement Work Item CRUD tests
4. Add error scenario coverage

### Phase 3: Extended Coverage (Week 3)
1. Article CRUD tests
2. Group CRUD tests
3. Webhook CRUD tests
4. Link create/delete tests

### Phase 4: Production Readiness (Week 4)
1. Orphan detection tooling
2. CI/CD integration
3. Documentation and runbook
4. Performance optimization

## Code Examples

### Complete Test Example

```python
"""Example write operation test with full lifecycle management."""

import pytest
from devrev import DevRevClient
from tests.integration.utils import TestDataManager

pytestmark = [
    pytest.mark.integration,
    pytest.mark.write,  # Mark for selective execution
]


class TestAccountsCRUD:
    """Full CRUD test suite for Accounts service."""

    def test_create_account_success(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test successful account creation."""
        # Arrange
        name = test_data.generate_name("CreateTest")

        # Act
        account = write_client.accounts.create(display_name=name)
        test_data.register("account", account.id)

        # Assert
        assert account.id is not None
        assert account.display_name == name

    def test_update_account_success(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test successful account update."""
        # Arrange - create account first
        original_name = test_data.generate_name("UpdateTest")
        account = write_client.accounts.create(display_name=original_name)
        test_data.register("account", account.id)

        # Act
        new_name = test_data.generate_name("UpdatedName")
        updated = write_client.accounts.update(
            id=account.id,
            display_name=new_name,
        )

        # Assert
        assert updated.display_name == new_name

    def test_delete_account_success(
        self,
        write_client: DevRevClient,
        test_data: TestDataManager,
    ) -> None:
        """Test successful account deletion."""
        # Arrange
        name = test_data.generate_name("DeleteTest")
        account = write_client.accounts.create(display_name=name)
        # Don't register - we're testing delete

        # Act
        write_client.accounts.delete(id=account.id)

        # Assert - verify deletion by trying to get
        with pytest.raises(NotFoundError):
            write_client.accounts.get(id=account.id)
```

### Cleanup Report

```python
@dataclass
class CleanupReport:
    """Report of cleanup operation results."""

    successes: list[tuple[str, str]] = field(default_factory=list)
    failures: list[tuple[str, str, str]] = field(default_factory=list)

    def add_success(self, resource_type: str, resource_id: str) -> None:
        self.successes.append((resource_type, resource_id))

    def add_failure(
        self,
        resource_type: str,
        resource_id: str,
        error: str,
    ) -> None:
        self.failures.append((resource_type, resource_id, error))

    @property
    def all_succeeded(self) -> bool:
        return len(self.failures) == 0

    def __str__(self) -> str:
        lines = [
            f"Cleanup Report:",
            f"  Successes: {len(self.successes)}",
            f"  Failures: {len(self.failures)}",
        ]
        for rtype, rid, err in self.failures:
            lines.append(f"    - {rtype}/{rid}: {err}")
        return "\n".join(lines)
```

## Best Practices

### Do's
- ✅ Always use `TestDataManager` for creating test data
- ✅ Use the `test_data` fixture for automatic cleanup
- ✅ Include both success and error test cases
- ✅ Use `@pytest.mark.write` for write operation tests
- ✅ Run write tests in isolated CI environment

### Don'ts
- ❌ Never hardcode resource IDs in tests
- ❌ Never skip cleanup in finally blocks
- ❌ Never run write tests against production
- ❌ Never create test data without the SDK_TEST_ prefix
- ❌ Never assume resources exist from previous runs

## Related Documentation

- [Integration Testing Setup](github-actions-setup.md)
- [API Services Reference](../api/services/index.md)
- [SDK Configuration](../api/config.md)

