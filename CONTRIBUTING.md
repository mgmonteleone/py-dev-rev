# Contributing to py-devrev

Thank you for your interest in contributing to the DevRev Python SDK! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Standards](#code-standards)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/py-dev-rev.git
   cd py-dev-rev
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/mgmonteleone/py-dev-rev.git
   ```

## Development Environment

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Setup with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Setup with pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Environment Configuration

```bash
# Copy environment template
cp .env.sample .env

# Edit .env with your DevRev API credentials
# DEVREV_API_TOKEN=your-token-here
```

## Code Standards

We maintain high code quality standards using automated tools.

### Linting and Formatting

We use **Ruff** for both linting and formatting:

```bash
# Format code
ruff format .

# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .
```

### Type Checking

We use **mypy** for static type checking:

```bash
# Run type checker
mypy src/

# Type checking is strict - all code must have type annotations
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

```bash
# Run all hooks manually
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

### Code Quality Requirements

All code must:
- ✅ Pass `ruff check` with no errors
- ✅ Pass `ruff format --check` (properly formatted)
- ✅ Pass `mypy src/` with no errors
- ✅ Have type annotations for all functions and methods
- ✅ Follow Google-style docstrings
- ✅ Have 80%+ test coverage for new code

## Branch Naming Conventions

Use descriptive branch names with the following prefixes:

- `feature/` - New features (e.g., `feature/add-webhook-support`)
- `fix/` - Bug fixes (e.g., `fix/pagination-error`)
- `docs/` - Documentation updates (e.g., `docs/improve-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/simplify-auth`)
- `test/` - Test improvements (e.g., `test/add-integration-tests`)
- `chore/` - Maintenance tasks (e.g., `chore/update-dependencies`)

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```
feat(client): add support for custom retry strategies

Implement configurable retry strategies with exponential backoff.
Users can now customize retry behavior for failed API calls.

Closes #123
```

```
fix(pagination): handle empty result sets correctly

Previously, pagination would fail when API returned empty results.
Now properly handles edge case and returns empty list.

Fixes #456
```

### Commit Guidelines

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit first line to 72 characters
- Reference issues and PRs in footer
- Include breaking changes in footer with `BREAKING CHANGE:` prefix

## Pull Request Process

### Before Submitting

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:
   ```bash
   # Format and lint
   ruff format .
   ruff check --fix .
   
   # Type check
   mypy src/
   
   # Run tests
   pytest
   
   # Check coverage
   pytest --cov=src/devrev --cov-report=term-missing
   ```

3. **Update documentation** if needed
4. **Add tests** for new features
5. **Update CHANGELOG.md** (if applicable)

### Submitting the PR

1. Push your branch to your fork
2. Create a Pull Request against `main`
3. Fill out the PR template completely
4. Link related issues
5. Request review from maintainers

### PR Requirements

- ✅ All CI checks pass
- ✅ Code review approved
- ✅ Tests pass with 80%+ coverage
- ✅ Documentation updated
- ✅ No merge conflicts
- ✅ Commits follow conventional format

### Review Process

1. Automated checks run (CI/CD)
2. Code review by maintainers
3. Address feedback and update PR
4. Final approval and merge

## Testing Requirements

### Test Coverage

- **Minimum 80% coverage** for all new code
- **100% coverage** for critical paths (authentication, API calls)
- Both unit and integration tests required

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/devrev --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py

# Run integration tests only
pytest -m integration

# Run with verbose output
pytest -v
```

### Writing Tests

- Use `pytest` framework
- Follow existing test patterns
- Mock external API calls in unit tests
- Use fixtures for common setup
- Test both success and error cases
- Include edge cases

### Test Organization

```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Tests with real API calls
└── conftest.py     # Shared fixtures
```

## Documentation

### Docstring Style

Use Google-style docstrings:

```python
def create_work_item(
    title: str,
    description: str | None = None,
) -> WorkItem:
    """Create a new work item in DevRev.
    
    Args:
        title: The title of the work item.
        description: Optional detailed description.
    
    Returns:
        The created WorkItem instance.
    
    Raises:
        ValidationError: If title is empty or invalid.
        APIError: If the API request fails.
    
    Example:
        >>> client = DevRevClient()
        >>> work = client.create_work_item("Fix login bug")
        >>> print(work.id)
    """
```

### Documentation Updates

- Update docstrings for all public APIs
- Add examples for new features
- Update `docs/` directory if needed
- Keep README.md current

## Questions?

- 📧 Email: matthewm@augmentcode.com
- 🐛 Issues: [GitHub Issues](https://github.com/mgmonteleone/py-dev-rev/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/mgmonteleone/py-dev-rev/discussions)

Thank you for contributing! 🎉

