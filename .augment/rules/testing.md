---
type: "always_apply"
description: "Example description"
---

# Testing and Quality Assurance Standards

## Core Testing Philosophy

- **Create tests for ALL added functionality** - no exceptions
- Tests must verify actual behavior, not just pass
- **Never create tests that trivially pass** to satisfy coverage
- **Never invalidate or skip failing tests** - fix the underlying issue
- If fixing an issue is not possible or very time-consuming, **ask the human for permission**

## Test Framework

Use **pytest** as the primary testing framework:

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.11.0",
]
```

## Test Organization

### Directory Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── unit/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── integration/
│   ├── __init__.py
│   └── test_api.py
└── fixtures/
    └── sample_data.json
```

### Test Naming

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test functions: `test_<what_is_being_tested>_<expected_behavior>`

```python
def test_user_creation_with_valid_data_succeeds():
    ...

def test_user_creation_with_invalid_email_raises_validation_error():
    ...
```

## Test Types

### Unit Tests

- Test individual functions and methods in isolation
- Mock external dependencies
- Fast execution (< 100ms per test)
- High volume, cover edge cases

### Integration Tests

- Test component interactions
- May use real databases (test instances)
- Test API endpoints end-to-end
- Mark with `@pytest.mark.integration`

### Fixtures and Mocking

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_user():
    return User(id=1, name="Test User", email="test@example.com")

@pytest.fixture
def mock_api_client():
    with patch("myapp.client.APIClient") as mock:
        mock.return_value.get.return_value = {"status": "ok"}
        yield mock
```

## Coverage Requirements

### Minimum Coverage

- **Target: 80%+ line coverage** for all new code
- **Critical paths: 95%+ coverage** (auth, payments, data handling)
- Configure coverage thresholds in `pyproject.toml`

```toml
[tool.coverage.report]
fail_under = 80
show_missing = true
```

### Coverage Reporting

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Generate coverage report
coverage report -m
```

## Pre-Commit Testing Requirements

### Before ANY Commit

1. **Run full test suite**: `pytest`
2. **Verify no regressions**: All existing tests must pass
3. **Check coverage**: Coverage must not decrease
4. **Review failing tests**: Fix issues, don't skip tests

### Handling Failing Tests

When a test fails:

1. **Investigate the root cause** - is it a code bug or test bug?
2. **Fix the actual issue** - in production code or test code
3. **Never**:
   - Comment out failing tests
   - Add `@pytest.mark.skip` without justification
   - Modify assertions to make tests pass artificially
   - Delete tests to avoid failures

4. **If fix is complex or time-consuming**:
   - Document the issue clearly
   - **Ask the human for permission** before proceeding
   - Create a tracking issue if deferred

## Test Quality Guidelines

### Good Tests

```python
def test_calculate_discount_applies_percentage_correctly():
    # Arrange
    order = Order(subtotal=100.00)
    discount = Discount(percentage=20)

    # Act
    result = order.apply_discount(discount)

    # Assert
    assert result.total == 80.00
    assert result.discount_applied == 20.00
```

### Bad Tests (Avoid These)

```python
# BAD: Always passes, tests nothing
def test_something():
    assert True

# BAD: Tautology - tests the mock, not real code
def test_api_call(mock_api):
    mock_api.get.return_value = "response"
    assert mock_api.get() == "response"

# BAD: No assertions
def test_user_creation():
    user = User(name="Test")
    # Missing assertions!
```

## Async Testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_api_call():
    client = AsyncClient()
    response = await client.fetch_data()
    assert response.status == 200
```

## Test Data Management

- Use factories (factory_boy) for complex object creation
- Use faker for realistic test data
- Never use real PII in tests
- Keep test data in fixtures or dedicated test data modules