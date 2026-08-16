#!/bin/bash
# dir-sync: bidirectional rsync wrapper with optional checksum verification.
# Usage: sync.sh [--pull|--push] [--dry-run] [--verify] SRC DEST

set -euo pipefail

DRY_RUN=""
VERIFY=""
MODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN="--dry-run"; shift ;;
    --verify) VERIFY="yes"; shift ;;
    --push) MODE="push"; shift ;;
    --pull) MODE="pull"; shift ;;
    *) break ;;
  esac
done

if [[ -z "$MODE" ]]; then
  echo "Error: specify --push or --pull" >&2
  exit 1
fi

SRC="$1"
DEST="$2"

# Build rsync command
RSYNC_OPTS="-avz --partial"
if [[ -n "$DRY_RUN" ]]; then
  RSYNC_OPTS="$RSYNC_OPTS --dry-run"
fi

EXCLUDE_FILE="$SRC/.dir-sync-ignore"
if [[ -f "$EXCLUDE_FILE" ]]; then
  RSYNC_OPTS="$RSYNC_OPTS --exclude-from=$EXCLUDE_FILE"
fi

# Perform the sync
if [[ "$MODE" == "push" ]]; then
  rsync $RSYNC_OPTS "$SRC/" "$DEST/"
elif [[ "$MODE" == "pull" ]]; then
  rsync $RSYNC_OPTS "$DEST/" "$SRC/"
fi

# Optional verification step
if [[ -n "$VERIFY" ]]; then
  echo "Running checksum verification..."
  python3 verify.py "$SRC" "$DEST" "$MODE" "$DRY_RUN"
fi

# Wrap up: report completion
echo "Sync complete (mode=$MODE dry_run=${DRY_RUN:-no})"
exit 0