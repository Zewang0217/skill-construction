#!/usr/bin/env python3
"""Validate the skill installation environment."""

import os
import subprocess
import sys
from pathlib import Path


def check_dependencies():
    """Verify required Python packages are available."""
    required = ["yaml", "toml", "jsonschema"]
    missing = []
    for mod in required:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        return 1
    return 0


def check_global_settings():
    """Create the global settings directory if needed."""
    settings_dir = Path.home() / ".config" / "yaml-config-utils"
    if not settings_dir.exists():
        settings_dir.mkdir(parents=True, exist_ok=True)
    return 0


def main():
    # Allow environment to skip validation (used in CI, containers)
    if os.environ.get("CFGUTILS_SKIP_CHECK") == "1":
        return 0

    exit_code = check_dependencies()
    if exit_code != 0:
        return exit_code
    return check_global_settings()


if __name__ == "__main__":
    sys.exit(main())