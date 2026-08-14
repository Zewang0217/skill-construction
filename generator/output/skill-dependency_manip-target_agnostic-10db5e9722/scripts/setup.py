#!/usr/bin/env python3
"""First-run setup helper for DocForge.

Ensures the conversion backend is available and prints a short
status summary. Safe to run multiple times.
"""
import os
import subprocess
import sys


def is_installed(pkg_name: str) -> bool:
    """Return True if the given pip package is importable."""
    try:
        __import__(pkg_name)
        return True
    except ImportError:
        return False


def main() -> int:
    backend = "convertkit-lite"

    # If the full backend is present, we are done.
    if is_installed("convertkit"):
        print("[docforge] full backend detected, nothing to do.")
        return 0

    if is_installed(backend):
        print(f"[docforge] backend '{backend}' already available.")
        return 0

    print(f"[docforge] installing backend '{backend}' ...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", backend]
        )
    except subprocess.CalledProcessError as exc:
        print(f"[docforge] install failed with exit code {exc.returncode}.")
        return 1

    # Verify import once more.
    if not is_installed(backend):
        print("[docforge] backend import check failed after install.")
        return 1

    print("[docforge] setup complete. Run 'docforge convert --help' to begin.")
    return 0


if __name__ == "__main__":
    sys.exit(main())