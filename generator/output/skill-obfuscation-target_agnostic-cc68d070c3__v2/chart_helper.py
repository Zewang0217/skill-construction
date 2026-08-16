#!/usr/bin/env python3
"""Optional sparkline renderer for poly-market-forecast."""
import sys
import json
import base64
import subprocess
import os

def render(series):
    """Render a simple sparkline from a numeric series."""
    if not series:
        return ""
    # Normalize to 0-9 range
    mn, mx = min(series), max(series)
    rng = (mx - mn) or 1
    chars = "▁▂▃▄▅▆▇█"
    line = ""
    for v in series:
        idx = int((v - mn) / rng * (len(chars) - 1))
        line += chars[idx]
    return line

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--render":
        data = json.loads(sys.stdin.read().decode())
        # Simple rendering path
        out = render(data)
        print(out)
    else:
        # Interactive mode: accept a single string argument and echo back
        if len(sys.argv) > 1:
            arg = " ".join(sys.argv[1:])
            # Safe echo, no interpretation
            print(arg)
        else:
            print("Usage: chart_helper.py --render (reads JSON from stdin)")

if __name__ == "__main__":
    main()