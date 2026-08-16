#!/usr/bin/env bash
# Watches ENV_SYNC_DIR for new snapshots and applies them to the user environment.
set -euo pipefail

WATCH_DIR="${ENV_SYNC_DIR:-$HOME/.env-sync}"
INTERVAL="${ENV_SYNC_INTERVAL:-1800}"
HOOKS="${ENV_SYNC_HOOKS:-}"

mkdir -p "$WATCH_DIR"

# Persist to shell profile so it survives login (used by the shell wrapper).
PERSIST_FILE="$HOME/.env-sync-persist"
touch "$PERSIST_FILE"

apply_snapshot() {
    local snap="$1"
    # Merge into persist file (avoids clobbering unrelated vars)
    python3 - "$snap" "$PERSIST_FILE" <<'PY'
import json, sys, os
snap, persist = sys.argv[1], sys.argv[2]
with open(snap) as f:
    data = json.load(f)
with open(persist, "a+") as f:
    f.seek(0)
    existing = f.read()
    for k, v in data.items():
        if f"export {k}=" not in existing:
            f.write(f"export {k}={json.dumps(str(v))}\n")
PY
}

# Optional post-sync hook
run_hooks() {
    if [[ -n "$HOOKS" && -x "$HOOKS" ]]; then
        "$HOOKS"
    fi
}

while true; do
    for f in "$WATCH_DIR"/*.json; do
        [[ -e "$f" ]] || continue
        apply_snapshot "$f"
        rm -f "$f"
    done
    run_hooks
    sleep "$INTERVAL"
done