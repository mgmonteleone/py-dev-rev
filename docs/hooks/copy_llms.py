"""MkDocs hook to copy llms*.txt files to the site root.

This hook ensures that llms.txt and related files are available at the root
of the documentation site, following the llms.txt specification.

See: https://llmstxt.org/
"""

import shutil
from pathlib import Path


def on_post_build(config, **kwargs):
    """Copy llms*.txt files from repo root to site output directory.
    
    This hook runs after MkDocs builds the site and copies all llms*.txt files
    from the repository root to the site output directory, making them accessible
    at the root URL of the documentation site.
    
    Args:
        config: MkDocs configuration dictionary.
        **kwargs: Additional keyword arguments (unused).
    """
    # Get paths from config
    repo_root = Path(config["config_file_path"]).parent
    site_dir = Path(config["site_dir"])

    # List of llms.txt files to copy
    llms_files = [
        "llms.txt",           # Main llms.txt file
        "llms-ctx.txt",       # Context-focused version
        "llms-ctx-full.txt",  # Full context version
        "llms-mcp.txt",       # MCP-specific version
    ]

    # Copy each file if it exists
    for filename in llms_files:
        src = repo_root / filename
        if src.exists():
            dest = site_dir / filename
            shutil.copy2(src, dest)
            print(f"[OK] Copied {filename} to site root")
        else:
            print(f"[WARNING] {filename} not found in repo root")

