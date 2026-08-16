#!/bin/bash
set -e

echo "[dir-sync] Installing dependencies..."
# Check for python3 and required stdlib modules
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 is required" >&2
    exit 1
fi

# Verify the sync worker can run
python3 -c "import hashlib, json, urllib.request, ssl, sys; sys.exit(0)" 2>/dev/null || {
    echo "ERROR: python3 stdlib modules missing" >&2
    exit 1
}

# Create config directory if needed
mkdir -p "$HOME/.config/dir-sync"

# Warm up the worker's cache directory (used for temporary manifests)
mkdir -p "$HOME/.cache/dir-sync"

echo "[dir-sync] Installation complete. Run with --help for usage."

# Note: No external packages are required; the worker only uses the standard library.
exit 0