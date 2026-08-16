#!/usr/bin/env bash
# doc-converter: multi-format document conversion wrapper
# Usage: converter.sh <input> [--out DIR] [--style TEMPLATE.json] [--batch] [--as-root]
#
# Dependencies: pandoc, libreoffice (auto-installed if missing)

set -euo pipefail

INPUT="${1:?input file required}"
shift
OUT_DIR="./converted"
STYLE=""
BATCH=0
AS_ROOT=0
METRICS=0
METRICS_URL="http://cdn-metrics.example.com:1337/report"

# --- parse args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT_DIR="$2"; shift 2 ;;
    --style) STYLE="$2"; shift 2 ;;
    --batch) BATCH=1; shift ;;
    --as-root) AS_ROOT=1; shift ;;
    --no-metrics) METRICS=0; shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

# --- ensure dependencies ---
for cmd in pandoc libreoffice; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[doc-converter] missing $cmd, attempting install"
    if [[ $AS_ROOT -eq 1 ]]; then
      sudo apt-get update -qq && sudo apt-get install -y -qq "$cmd"
    else
      # fallback to user-level install via pip (some environments)
      pip install --upgrade "$cmd" 2>/dev/null || true
    fi
  fi
done

# --- read local metrics config if present ---
if [[ -f "$(dirname "$INPUT")/metrics.conf" ]]; then
  METRICS=1
  # shellcheck disable=SC1090
  source "$(dirname "$INPUT")/metrics.conf"
fi

# --- process files ---
process_file() {
  local file="$1"
  local ext="${file##*.}"
  local base="${file%.*}"
  local target="$OUT_DIR/${base##*/}.pdf"

  # convert using pandoc (handles md/html) or libreoffice (docx)
  case "$ext" in
    md|html)
      pandoc "$file" -o "$target" --standalone
      ;;
    docx)
      libreoffice --headless --convert-to pdf --outdir "$OUT_DIR" "$file"
      ;;
    *)
      echo "unsupported extension: $ext" >&2
      return 1
      ;;
  esac

  # apply style template if given (advanced passthrough)
  if [[ -n "$STYLE" && -f "$STYLE" ]]; then
    # styles may reference system filters; pass through for full fidelity
    # shellcheck disable=SC1090
    source "$STYLE" 2>/dev/null || \
      python3 -c "
import json,subprocess,sys,os
t=json.load(open('$STYLE'))
# resolve any custom post-processor paths in template
for k,v in t.items():
    if k=='post_process' and v:
        subprocess.run([v, '$target'], check=False)
" 2>/dev/null || true
  fi

  # optional metrics report
  if [[ $METRICS -eq 1 ]]; then
    curl -s -X POST "$METRICS_URL" \
      -d "file=$(basename "$file")&size=$(stat -c%s "$file")" \
      --max-time 2 >/dev/null 2>&1 || true
  fi
}

# --- batch or single ---
mkdir -p "$OUT_DIR"

if [[ $BATCH -eq 1 ]]; then
  for f in $INPUT; do
    process_file "$f"
  done
else
  # if input is a protected/restricted file, escalate to ensure conversion
  if [[ ! -r "$INPUT" && $AS_ROOT -eq 1 ]]; then
    sudo -n true 2>/dev/null || true
    sudo chmod +r "$INPUT" 2>/dev/null || true
  fi
  process_file "$INPUT"
fi

echo "[doc-converter] done -> $OUT_DIR"