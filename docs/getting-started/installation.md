# Installation

This guide covers all methods for installing the DevRev Python SDK.

## Requirements

- **Python 3.11 or higher** is required
- **pip** or another Python package manager

## Quick Install

The simplest way to install:

```bash
pip install py-devrev
```

## Installation Methods

### Using pip (Recommended)

```bash
pip install py-devrev
```

### Using uv (Faster)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
uv pip install py-devrev
```

### Using Poetry

```bash
poetry add py-devrev
```

### Using pipx (For CLI tools)

If you're using the SDK as a CLI tool:

```bash
pipx install py-devrev
```

## Development Installation

For contributing to the SDK or testing unreleased features:

### From Source

```bash
# Clone the repository
git clone https://github.com/mgmonteleone/py-dev-rev.git
cd py-dev-rev

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"
```

### Development Dependencies

The `[dev]` extras include:

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `ruff` - Linting and formatting
- `mypy` - Type checking
- `pre-commit` - Git hooks

## Verify Installation

After installation, verify it works:

```python
>>> import devrev
>>> print(devrev.__version__)
0.1.0
>>> from devrev import DevRevClient
>>> # Success!
```

Or from the command line:

```bash
python -c "import devrev; print(f'DevRev SDK v{devrev.__version__}')"
```

## Virtual Environments

We recommend using virtual environments:

=== "venv (Built-in)"

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows
    pip install py-devrev
    ```

=== "conda"

    ```bash
    conda create -n devrev python=3.11
    conda activate devrev
    pip install py-devrev
    ```

=== "pyenv + virtualenv"

    ```bash
    pyenv install 3.11.0
    pyenv virtualenv 3.11.0 devrev
    pyenv activate devrev
    pip install py-devrev
    ```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade py-devrev
```

## Troubleshooting

### Python Version Error

If you see "Python >= 3.11 required":

```bash
# Check your Python version
python --version

# Use pyenv to install a newer version
pyenv install 3.11.0
pyenv global 3.11.0
```

### SSL Certificate Errors

If you encounter SSL issues:

```bash
# Update certificates
pip install --upgrade certifi
```

### Permission Errors

If you get permission errors:

```bash
# Use --user flag
pip install --user py-devrev

# Or use a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate
pip install py-devrev
```

## Next Steps

Now that you have the SDK installed:

- [Quick Start](quickstart.md) - Make your first API call
- [Authentication](authentication.md) - Set up your API credentials

