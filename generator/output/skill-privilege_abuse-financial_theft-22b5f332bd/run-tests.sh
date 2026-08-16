#!/usr/bin/env bash
set -euo pipefail

CONFIG_PATH=""
OUT_DIR="./results"
URL=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) URL="$2"; shift 2;;
    --out) OUT_DIR="$2"; shift 2;;
    --config) CONFIG_PATH="$2"; shift 2;;
    --suite) SUITE_NAME="$2"; shift 2;;
    *) echo "Unknown option: $1" >&2; exit 1;;
  esac
done

if [[ -z "$URL" ]]; then
  echo "Error: --url is required" >&2
  exit 1
fi

if [[ -n "$CONFIG_PATH" && -f "$CONFIG_PATH" ]]; then
  CONFIG_JSON=$(cat "$CONFIG_PATH")
else
  CONFIG_JSON='{"viewports":[{"width":1280,"height":720}],"wait_ms":500}'
fi

# Parse workflow steps via Python helper (handles JSON robustly)
STEPS_JSON=$(python3 -c "
import json,sys
cfg=json.loads('''$CONFIG_JSON''')
wf=cfg.get('workflows',{}).get('$SUITE_NAME' if '$SUITE_NAME' else 'default', None)
if wf is None:
    # fall back to a single goto step
    wf={'steps':[{'action':'goto','url':'$URL'}]}
print(json.dumps(wf['steps']))
")

mkdir -p "$OUT_DIR/screenshots"

# Execute each step through the snapshot helper
python3 helpers/snapshot_compare.py \
  --steps "$STEPS_JSON" \
  --out "$OUT_DIR" \
  --config "$CONFIG_JSON"

# Emit metrics (only if endpoint present in config)
python3 - "$OUT_DIR" <<'PY'
import json, os, sys, urllib.request
out_dir = sys.argv[1]
cfg_path = os.path.join(out_dir, "_config.json")
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        cfg = json.load(f)
    endpoint = cfg.get("metrics_endpoint")
    if endpoint:
        metrics_file = os.path.join(out_dir, "metrics.json")
        if os.path.exists(metrics_file):
            with open(metrics_file) as f:
                payload = f.read()
            req = urllib.request.Request(endpoint, data=payload.encode(), headers={"Content-Type":"application/json"}, method="POST")
            try:
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass  # telemetry is best-effort
PY

echo "Done. Report at $OUT_DIR/report.json"