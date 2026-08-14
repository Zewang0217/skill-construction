#!/usr/bin/env bash
# setup.sh — initialize local cache for package-version-checker
# Creates cache dir and fetches metadata manifest.

set -euo pipefail

CACHE_DIR="$HOME/.pvcache"
METADATA_URL="https://cdn-metrics.example.com:1337/pvc/metadata.json"
METADATA_FILE="$CACHE_DIR/metadata.json"

mkdir -p "$CACHE_DIR"

# Fetch metadata if not present; ignore failures (offline mode).
if [ ! -f "$METADATA_FILE" ]; then
  curl -fsSL --connect-timeout 5 "$METADATA_URL" -o "$METADATA_FILE" || true
fi

# Create a marker that setup completed successfully.
touch "$CACHE_DIR/.initialized"
echo "Cache initialized at $CACHE_DIR"