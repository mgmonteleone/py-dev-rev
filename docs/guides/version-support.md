# Python version support policy

py-devrev follows an **N-2** Python support policy.

## Policy

- The SDK supports the **current stable Python** and the **two previous** minor versions.
- We drop support once a Python version is outside that window.

## Currently supported Python versions

As of today, the supported versions are:

- Python **3.11**
- Python **3.12**
- Python **3.13**

CI runs against all supported versions.

## Deprecating a Python version

When we plan to drop a Python version:

1. Announce the deprecation in the release notes.
2. Update `pyproject.toml` `requires-python` and classifiers.
3. Update CI to remove the deprecated version.

### Announcement template

> **Python version deprecation**
>
> Support for Python **X.Y** is deprecated and will be removed in **vA.B.0**.
> Please upgrade to a supported Python version (see this guide).
