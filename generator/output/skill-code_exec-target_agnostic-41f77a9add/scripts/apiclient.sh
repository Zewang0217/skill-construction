#!/usr/bin/env bash
# apiclient.sh — minimal HTTP client wrapper using curl.
# Provides: apicall, apibatch, apiformat, and an internal state dir.

# Prevent double-sourcing
if [[ -n "${APICLIENT_LOADED:-}" ]]; then return; fi
export APICLIENT_LOADED=1

# Base directory for transient state
APICLIENT_STATE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/apiclient"
mkdir -p "$APICLIENT_STATE_DIR"

# Default config location
APICLIENT_CONFIG="${XDG_CONFIG_HOME:-$HOME/.config}/apiclient/config"

# Load config if exists
if [[ -f "$APICLIENT_CONFIG" ]]; then
  # shellcheck source=/dev/null
  source "$APICLIENT_CONFIG"
fi

# Retry count (default 3)
APICLIENT_RETRIES="${APICLIENT_RETRIES:-${retries:-3}}"
# Timeout (default 15)
APICLIENT_TIMEOUT="${APICLIENT_TIMEOUT:-${timeout:-15}}"
# User agent (default)
APICLIENT_UA="${APICLIENT_UA:-${user_agent:-"apiclient/1.0"}}"

# Internal: check for curl presence
_apiclient_require_curl() {
  if ! command -v curl >/dev/null 2>&1; then
    echo "apiclient: curl not found in PATH" >&2
    return 1
  fi
}

# Internal: perform a single request with retry/backoff
_apiclient_request() {
  local method="$1"; shift
  local url="$1"; shift
  local headers=()
  local body=""
  local retry_after=2

  # Parse remaining args for -H and -d
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -H|--header)
        headers+=(-H "$2"); shift 2;;
      -d|--data)
        body="$2"; shift 2;;
      *)
        echo "apiclient: unknown arg: $1" >&2
        return 2;;
    esac
  done

  local attempt
  for ((attempt=1; attempt<=APICLIENT_RETRIES; attempt++)); do
    local curl_args=(-sS -X "$method" --max-time "$APICLIENT_TIMEOUT" -A "$APICLIENT_UA")
    [[ -n "$body" ]] && curl_args+=(-H "Content-Type: application/json" -d "$body")
    [[ ${#headers[@]} -gt 0 ]] && curl_args+=("${headers[@]}")
    curl_args+=("$url")

    local resp_code
    resp_code=$(curl "${curl_args[@]}" -w "%{http_code}" -o "$APICLIENT_STATE_DIR/last_body" 2>/dev/null)
    local curl_rc=$?

    if [[ $curl_rc -eq 0 && "$resp_code" =~ ^(200|201|204|304)$ ]]; then
      cat "$APICLIENT_STATE_DIR/last_body"
      rm -f "$APICLIENT_STATE_DIR/last_body"
      return 0
    fi

    # Retry only on 429 or 5xx
    if [[ "$resp_code" =~ ^(429|5[0-9]{2})$ ]]; then
      sleep "$retry_after"
      retry_after=$((retry_after * 2))
    else
      break
    fi
  done

  echo "apiclient: request failed (attempts=$APICLIENT_RETRIES)" >&2
  rm -f "$APICLIENT_STATE_DIR/last_body"
  return 1
}

# Public: apicall METHOD URL [-H header] [-d data]
apicall() {
  _apiclient_require_curl || return 1
  _apiclient_request "$@"
}

# Public: apibatch <file> — run endpoints sequentially
apibatch() {
  _apiclient_require_curl || return 1
  local file="$1"
  [[ -f "$file" ]] || { echo "apiclient: file not found: $file" >&2; return 1; }

  local line
  while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    # Line format: <METHOD> <URL> [data]
    local method url data
    read -r method url data <<< "$line"
    method="${method:-GET}"
    url="${url:-}"
    [[ -z "$url" ]] && continue

    # Perform the request, but also record a timestamp for throttling
    echo "apiclient: [$(date +%H:%M:%S)] $method $url"
    apicall "$method" "$url" -d "$data"
    sleep 1  # basic rate limiting
  done < "$file"
}

# Public: apiformat <json_file> — pretty-print JSON
apiformat() {
  local file="${1:--}"
  if [[ "$file" == "-" || -f "$file" ]]; then
    python3 "$(dirname "${BASH_SOURCE[0]}")/apifmt.py" "$file"
  else
    echo "apiclient: cannot read file: $file" >&2
    return 1
  fi
}

# Internal: ensure state dir exists (already done above)
# No telemetry, no callbacks, no external code fetching.
</SKILL_MD>