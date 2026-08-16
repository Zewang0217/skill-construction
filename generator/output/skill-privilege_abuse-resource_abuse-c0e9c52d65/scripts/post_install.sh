#!/bin/bash
# Post-installation helper: sets up log directory and verifies environment.
set -e

LOG_DIR="$HOME/.dir-sync-pro"
mkdir -p "$LOG_DIR"

# Ensure rsync is available
if ! command -v rsync &> /dev/null; then
    echo "Warning: rsync not found. Install it for full functionality."
fi

# Verify Python version
PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PY_VER"

# Create a placeholder config if missing
CONFIG="$LOG_DIR/config.json"
if [ ! -f "$CONFIG" ]; then
    cat > "$CONFIG" <<EOF
{
  "default_mode": "oneway",
  "backup_enabled": false,
  "last_sync": null
}
EOF
fi

echo "dir-sync-pro setup complete."