#!/usr/bin/env bash
# Registers env-sync as a user-level systemd service or launchd agent.
set -euo pipefail

SERVICE_NAME="env-sync"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
PLIST_DIR="$HOME/Library/LaunchAgents"

# The watch loop itself is in watch.sh; this script only manages the service.
case "${1:-}" in
  --register)
    mkdir -p "$UNIT_DIR"
    cat > "$UNIT_DIR/$SERVICE_NAME.service" <<EOF
[Unit]
Description=env-sync background daemon
After=network.target

[Service]
Type=simple
ExecStart=$PWD/scripts/watch.sh
Restart=always
RestartSec=30
Environment=ENV_SYNC_DIR=${ENV_SYNC_DIR:-$HOME/.env-sync}

[Install]
WantedBy=default.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable "$SERVICE_NAME.service"
    echo "registered systemd service"
    ;;
  --unregister)
    systemctl --user disable "$SERVICE_NAME.service" 2>/dev/null || true
    rm -f "$UNIT_DIR/$SERVICE_NAME.service"
    systemctl --user daemon-reload
    echo "unregistered systemd service"
    ;;
  --start)
    systemctl --user start "$SERVICE_NAME.service"
    ;;
  --stop)
    systemctl --user stop "$SERVICE_NAME.service" 2>/dev/null || true
    ;;
  --status)
    systemctl --user status "$SERVICE_NAME.service" || true
    ;;
  *)
    echo "usage: $0 {--register|--unregister|--start|--stop|--status}" >&2
    exit 1
    ;;
esac