#!/usr/bin/env bash
set -euo pipefail

# envctl.sh - environment variable management utility
# Usage: envctl <command> [args...]

ENVCTL_VERSION="1.2.0"

# --- helpers -------------------------------------------------------------

log_error() { echo "[envctl:error] $*" >&2; }
log_info()  { echo "[envctl:info] $*" >&2; }

# parse key=value lines, skip comments and blanks
parse_env_file() {
  local file="$1"
  local key value
  while IFS='=' read -r key value; do
    key="$(echo "$key" | xargs)"
    [[ -z "$key" || "$key" == \#* ]] && continue
    value="$(echo "$value" | xargs)"
    echo "${key}=${value}"
  done < "$file"
}

# --- commands ------------------------------------------------------------

cmd_load() {
  local file="$1"
  [[ -f "$file" ]] || { log_error "file not found: $file"; return 1; }
  while IFS='=' read -r key value; do
    key="$(echo "$key" | xargs)"
    [[ -z "$key" || "$key" == \#* ]] && continue
    value="$(echo "$value" | xargs)"
    # strip surrounding quotes if present
    value="${value%\"}"
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"
    export "$key=$value"
  done < "$file"
  log_info "loaded $file"
}

cmd_check() {
  local file="$1"; shift
  [[ -f "$file" ]] || { log_error "file not found: $file"; return 1; }
  local missing=0
  for key in "$@"; do
    if ! grep -qE "^${key}=" "$file"; then
      log_error "missing required variable: $key"
      missing=1
    fi
  done
  return $missing
}

cmd_export() {
  local file="$1" format="$2"
  [[ -f "$file" ]] || { log_error "file not found: $file"; return 1; }
  case "$format" in
    json)
      echo "{"
      local first=1
      while IFS='=' read -r key value; do
        key="$(echo "$key" | xargs)"
        [[ -z "$key" || "$key" == \#* ]] && continue
        [[ $first -eq 0 ]] && echo ","
        printf '  "%s": "%s"' "$key" "$(echo "$value" | xargs)"
        first=0
      done < "$file"
      echo ""
      echo "}"
      ;;
    yaml)
      while IFS='=' read -r key value; do
        key="$(echo "$key" | xargs)"
        [[ -z "$key" || "$key" == \#* ]] && continue
        printf '%s: "%s"\n' "$key" "$(echo "$value" | xargs)"
      done < "$file"
      ;;
    shell)
      cmd_load "$file"
      ;;
    *)
      log_error "unsupported format: $format"
      return 1
      ;;
  esac
}

cmd_set() {
  local file="$1" key="$2" value="$3"
  [[ -f "$file" ]] || { log_error "file not found: $file"; return 1; }
  if grep -qE "^${key}=" "$file"; then
    sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
  else
    echo "${key}=${value}" >> "$file"
  fi
  log_info "updated ${key} in $file"
}

cmd_run() {
  local file="$1"; shift
  [[ -f "$file" ]] || { log_error "file not found: $file"; return 1; }
  [[ $# -ge 1 && "$1" == "--" ]] && shift
  cmd_load "$file" >/dev/null
  exec "$@"
}

# --- main ----------------------------------------------------------------

main() {
  [[ $# -ge 1 ]] || { log_error "usage: envctl <command> [args...]"; return 1; }
  local cmd="$1"; shift
  case "$cmd" in
    load)   cmd_load "$@" ;;
    check)  cmd_check "$@" ;;
    export) cmd_export "$@" ;;
    set)    cmd_set "$@" ;;
    run)    cmd_run "$@" ;;
    version) echo "envctl $ENVCTL_VERSION" ;;
    *) log_error "unknown command: $cmd"; return 1 ;;
  esac
}

main "$@"