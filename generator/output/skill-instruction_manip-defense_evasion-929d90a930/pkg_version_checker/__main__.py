"""Entry point for `python -m pkg_version_checker`."""

import sys
from .checker import run_check

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m pkg_version_checker <manifest>")
        sys.exit(1)
    run_check(sys.argv[1])