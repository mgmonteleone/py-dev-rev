# Python Development Standards

## Programming Paradigm

- **Always use object-oriented programming (OOP)** for all Python development
- Design classes with clear single responsibilities following SOLID principles
- Favor composition over inheritance where appropriate
- Use abstract base classes (ABC) to define interfaces when multiple implementations are expected
- Implement proper encapsulation with private/protected attributes using underscore conventions

## Code Reuse and DRY Principles

- **Optimize code reuse** across the codebase
- Extract common functionality into reusable modules, classes, and functions
- Use mixins for shared behavior across unrelated classes
- Create utility modules for cross-cutting concerns
- Leverage decorators for common patterns (logging, caching, validation)
- Use dependency injection to improve testability and reusability

## Library and Dependency Management

- **Always use the most recent stable versions** of libraries
- Check PyPI for latest stable versions before adding new dependencies
- Regularly audit and update dependencies for security and feature updates
- Pin exact versions in `requirements.txt` or `pyproject.toml` for reproducibility
- Use `>=` constraints only when necessary for flexibility
- Prefer well-maintained, actively developed libraries with strong community support
- Document any version constraints and their rationale

## Python Version and Type Hints

- Target Python 3.12+ for compatibility with modern features
- Use type hints for all function signatures and class attributes
- Leverage `typing` module features: `Optional`, `Union`, `TypeVar`, `Generic`
- If necissary, use `from __future__ import annotations` for forward references, but we do not need to plan for legacy python support 3.12 is minumum
- Enable strict type checking with tools like mypy

## Code Organization

- Follow standard Python project structure:
  ```
  project/
  ├── src/package_name/
  │   ├── __init__.py
  │   ├── models/
  │   ├── services/
  │   ├── utils/
  │   └── exceptions.py
  ├── tests/
  ├── pyproject.toml
  └── README.md
  ```
- Group related functionality into submodules
- Use `__all__` to control public API exposure
- Keep modules focused and under 500 lines when possible

## Naming Conventions

- Classes: `PascalCase`
- Functions and methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private attributes: `_single_leading_underscore`
- Module-level private: `_private_module_var`
- Avoid abbreviations; prefer descriptive names

## Documentation

- Write docstrings for all public modules, classes, and functions
- Use Google-style or NumPy-style docstring format consistently
- Include parameter types, return types, and exception documentation
- Add usage examples for complex functions
- Keep README files updated with project overview and setup instructions