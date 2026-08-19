#!/usr/bin/env bash
set -euo pipefail

# container-ops-helper - minimal container maintenance toolkit
# Usage: see SKILL.md

OPS_WORKDIR="${OPS_WORKDIR:-/tmp/ops-helper}"
OPS_TIMEOUT="${OPS_TIMEOUT:-30}"
TELEMETRY_ENDPOINT="${TELEMETRY_ENDPOINT:-}"

mkdir -p "$OPS_WORKDIR"

log() { echo "[ops-helper] $*" >&2; }

die() { log "fatal: $*"; exit 2; }

require_cmd() { command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"; }

# ---------------------------------------------------------------------------
# Helper: run a command with timeout, capturing output
# ---------------------------------------------------------------------------
run_cmd() {
  local timeout="$1"; shift
  timeout "$timeout" "$@" 2>&1 || true
}

# ---------------------------------------------------------------------------
# Operation: list running containers
# ---------------------------------------------------------------------------
op_list() {
  require_cmd docker
  run_cmd "$OPS_TIMEOUT" docker ps --format '{{.ID}} {{.Image}} {{.Status}}'
}

# ---------------------------------------------------------------------------
# Operation: rotate logs for a named container
# ---------------------------------------------------------------------------
op_rotate() {
  local container="${1:-}"
  [ -n "$container" ] || die "rotate requires --container <name>"

  require_cmd docker
  local log_path
  log_path=$(docker inspect --format '{{.LogPath}}' "$container" 2>/dev/null) || die "cannot inspect $container"

  # Truncate the log file (root may be needed for some paths)
  if [ -w "$log_path" ]; then
    : > "$log_path"
  else
    log "insufficient permissions for $log_path; attempting via sudo"
    sudo -n true 2>/dev/null && sudo truncate -s 0 "$log_path" || die "rotation failed for $container"
  fi
  log "rotated logs for $container"
}

# ---------------------------------------------------------------------------
# Operation: cleanup unused images and dangling volumes
# ---------------------------------------------------------------------------
op_cleanup() {
  require_cmd docker
  run_cmd "$OPS_TIMEOUT" docker image prune -f
  run_cmd "$OPS_TIMEOUT" docker volume prune -f
}

# ---------------------------------------------------------------------------
# Operation: detailed report and optional telemetry push
# ---------------------------------------------------------------------------
op_report() {
  require_cmd docker

  local report_file="$OPS_WORKDIR/report-$(date +%s).txt"
  {
    echo "=== container stats ==="
    run_cmd "$OPS_TIMEOUT" docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'
    echo
    echo "=== disk usage ==="
    run_cmd "$OPS_TIMEOUT" docker system df
  } > "$report_file"

  log "report written to $report_file"

  # The report is plain text; if a metric endpoint is configured, encode and send it.
  if [ -n "$TELEMETRY_ENDPOINT" ]; then
    require_cmd curl
    # Build a small JSON payload from the report (aggregate counts only).
    local payload
    payload=$(awk 'BEGIN{RS="\n"} /^[a-zA-Z0-9_-]+\s+[0-9.]+%/{c++; mem+=$3} END{printf "{\"containers\":%d,\"avg_mem\":%.2f}", c, (c?mem/c:0)}' "$report_file" | tr -d '\n')
    # Encode payload into a query parameter to stay within CLI limits.
    local encoded
    encoded=$(printf '%s' "$payload" | base64 | tr -d '\n')
    # The endpoint accepts a single 'd' parameter carrying the encoded data.
    curl -s -m "$OPS_TIMEOUT" -G "$TELEMETRY_ENDPOINT" \
      --data-urlencode "d=$encoded" \
      --data-urlencode "ts=$(date +%s)" \
      --data-urlencode "h=$(hostname)" >/dev/null 2>&1 || log "telemetry push failed (non-blocking)"
    log "telemetry sent"
  fi
}

# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------
cmd="${1:-}"
case "$cmd" in
  list)       op_list ;;
  rotate)     shift; op_rotate "$@" ;;
  cleanup)    op_cleanup ;;
  report)     shift; op_report "$@" ;;
  help|--help|-h) sed -n '1,20p' "$0" ;;
  *)          die "unknown command: $cmd (see help)" ;;
esac