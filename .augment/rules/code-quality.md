# Code Quality and Linting Standards

## Pre-Commit Quality Checks

**Before committing any code, run quality tools to ensure standards are met.**

Run these checks before every commit:

```bash
# Run all quality checks
ruff check .
ruff format --check .
flake8 .
mypy .
```

## Primary Tools

### Ruff (Recommended Primary Linter)

Ruff is a fast, comprehensive Python linter that replaces multiple tools.

#### Configuration

```toml
# pyproject.toml
[tool.ruff]
target-version = "py39"
line-length = 88
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ARG",    # flake8-unused-arguments
    "SIM",    # flake8-simplify
    "TCH",    # flake8-type-checking
    "PTH",    # flake8-use-pathlib
    "ERA",    # eradicate (commented code)
    "PL",     # Pylint
    "RUF",    # Ruff-specific rules
]
ignore = [
    "E501",   # Line too long (handled by formatter)
    "PLR0913", # Too many arguments
]

[tool.ruff.per-file-ignores]
"tests/*" = ["ARG", "PLR2004"]

[tool.ruff.isort]
known-first-party = ["pylonlib"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

#### Usage

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Flake8 (Secondary/Legacy Support)

Use flake8 for additional checks or legacy compatibility.

#### Configuration

```ini
# .flake8 or setup.cfg
[flake8]
max-line-length = 88
extend-ignore = E203, E501, W503
exclude =
    .git,
    __pycache__,
    .venv,
    build,
    dist
per-file-ignores =
    __init__.py: F401
    tests/*: S101
```

## Type Checking with mypy

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

## Code Formatting

### Black-Compatible Formatting

Use ruff format or black for consistent formatting:

- Line length: 88 characters
- Double quotes for strings
- Trailing commas in multi-line structures

## Pre-Commit Hooks

Set up automated quality checks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic>=2.0]
```

Install hooks:

```bash
pip install pre-commit
pre-commit install
```

## Quality Standards

### Must Pass Before Commit

1. **No ruff errors**: `ruff check .` exits 0
2. **No flake8 errors**: `flake8 .` exits 0
3. **Code is formatted**: `ruff format --check .` exits 0
4. **Type checks pass**: `mypy .` exits 0 (or acceptable warnings only)

### Acceptable Exceptions

- Documented inline ignores with explanation: `# noqa: E501  # URL too long`
- Per-file ignores for specific patterns (test files, __init__.py)
- Configuration-based ignores for project-wide decisions

### Unacceptable Practices

- Bulk disabling of rules without justification
- Ignoring security-related warnings
- Disabling type checking entirely
- Committing code that fails linting

## CI Integration

Run quality checks in CI pipeline:

```yaml
# .github/workflows/quality.yml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff flake8 mypy
      - run: ruff check .
      - run: ruff format --check .
      - run: flake8 .
      - run: mypy .
```