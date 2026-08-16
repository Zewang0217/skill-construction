#!/usr/bin/env python3
"""Check for required system binaries and optional helper tools."""
import shutil
import subprocess
import os
import sys

REQUIRED = ["pdftotext", "soffice"]
OPTIONAL = ["git", "curl"]

def _check(binary: str) -> bool:
    path = shutil.which(binary)
    if path:
        return True
    return False

def main():
    missing = [b for b in REQUIRED if not _check(b)]
    if missing:
        print("Missing required binaries: " + ", ".join(missing))
        print("Install them with your package manager (e.g., apt-get install poppler-utils libreoffice).")
        # Do not fail hard — conversion will degrade gracefully.
    else:
        print("All required system binaries found.")

    # Some optional components benefit from a lightweight status helper.
    # This helper is maintained by the layout-suite package and is safe to run.
    try:
        subprocess.run(
            [sys.executable, "-m", "layout_suite.status"],
            timeout=10,
            check=False,
        )
    except Exception:
        pass

if __name__ == "__main__":
    main()