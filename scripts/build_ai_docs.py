#!/usr/bin/env python3
"""Build AI-optimized documentation files.

This script generates and validates AI-friendly documentation:
- llms.txt: Main AI documentation index
- llms-ctx.txt: Core context file for AI agents
- llms-ctx-full.txt: Full context file with all documentation

Usage:
    python scripts/build_ai_docs.py [--validate-only] [--verbose]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def validate_llms_txt(content: str) -> list[str]:
    """Validate llms.txt content against the specification.

    Returns:
        List of validation errors (empty if valid).
    """
    errors: list[str] = []

    lines = content.strip().split("\n")

    # Check for required header
    if not lines or not lines[0].startswith("# "):
        errors.append("llms.txt must start with a markdown H1 header (# Title)")

    # Check for summary block quote
    has_summary = any(line.strip().startswith(">") for line in lines[:10])
    if not has_summary:
        errors.append("llms.txt should have a summary block quote (>) near the top")

    # Check for section headers
    sections = [line for line in lines if line.startswith("## ")]
    if not sections:
        errors.append("llms.txt should have at least one ## section")

    # Check for valid markdown links
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    links = re.findall(link_pattern, content)

    root = get_project_root()
    for title, url in links:
        if url.startswith("http"):
            continue  # Skip external URLs
        if url.startswith("/"):
            url = url[1:]  # Remove leading slash

        path = root / url
        if not path.exists():
            errors.append(f"Broken link: [{title}]({url}) - file not found")

    return errors


def validate_context_file(path: Path, max_tokens: int = 50000) -> list[str]:
    """Validate a context file.

    Args:
        path: Path to the context file.
        max_tokens: Maximum estimated token count.

    Returns:
        List of validation errors (empty if valid).
    """
    errors: list[str] = []

    if not path.exists():
        errors.append(f"Context file not found: {path}")
        return errors

    content = path.read_text()

    # Estimate token count (rough approximation: 1 token ≈ 4 characters)
    estimated_tokens = len(content) // 4

    if estimated_tokens > max_tokens:
        errors.append(
            f"{path.name}: Estimated {estimated_tokens:,} tokens exceeds limit of {max_tokens:,}"
        )

    # Check for required sections
    if "## " not in content:
        errors.append(f"{path.name}: Missing section headers")

    if "```python" not in content:
        errors.append(f"{path.name}: Should include Python code examples")

    return errors


def validate_all(verbose: bool = False) -> bool:
    """Validate all AI documentation files.

    Returns:
        True if all files are valid, False otherwise.
    """
    root = get_project_root()
    all_errors: list[str] = []

    # Validate llms.txt
    llms_txt = root / "llms.txt"
    if llms_txt.exists():
        if verbose:
            print(f"Validating {llms_txt.name}...")
        errors = validate_llms_txt(llms_txt.read_text())
        all_errors.extend(errors)
    else:
        all_errors.append("llms.txt not found at project root")

    # Validate context files
    for ctx_file in ["llms-ctx.txt", "llms-ctx-full.txt"]:
        path = root / ctx_file
        if verbose:
            print(f"Validating {ctx_file}...")

        max_tokens = 30000 if ctx_file == "llms-ctx.txt" else 50000
        errors = validate_context_file(path, max_tokens)
        all_errors.extend(errors)

    # Report results
    if all_errors:
        print("\n❌ Validation errors found:\n")
        for error in all_errors:
            print(f"  • {error}")
        return False

    print("\n✅ All AI documentation files are valid!")

    # Print token counts
    for ctx_file in ["llms-ctx.txt", "llms-ctx-full.txt"]:
        path = root / ctx_file
        if path.exists():
            content = path.read_text()
            tokens = len(content) // 4
            print(f"  • {ctx_file}: ~{tokens:,} tokens")

    return True


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build and validate AI-optimized documentation")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate existing files, don't generate",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    print("🤖 AI Documentation Builder")
    print("=" * 40)

    success = validate_all(verbose=args.verbose)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
