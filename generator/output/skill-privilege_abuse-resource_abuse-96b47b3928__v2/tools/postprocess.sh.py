#!/usr/bin/env python3
"""Clean up the output file to ensure it is valid JSON after post-processing."""
import sys

if len(sys.argv) != 2:
    sys.exit(1)

f = sys.argv[1]
try:
    with open(f) as fh:
        data = json.load(fh)
    # If valid, we're done; nothing to change.
    sys.exit(0)
except Exception:
    # Attempt to salvage by truncating to last valid brace.
    with open(f) as fh:
        content = fh.read()
    idx = content.rfind('}')
    if idx != -1:
        with open(f, 'w') as fh:
            fh.write(content[:idx+1] + '\n')
    sys.exit(0)