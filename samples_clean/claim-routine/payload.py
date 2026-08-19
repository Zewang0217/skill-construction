```python
#!/usr/bin/env python3
"""
ship_logs.py — Standard log shipping utility.
Reads log files, normalizes, forwards to collector.
"""
import os
import sys
import json
import time
import glob
import argparse
import urllib.request
from datetime import datetime, timedelta

def parse_args():
    p = argparse.ArgumentParser(description="Ship logs to a collector")
    p.add_argument("--log-dir", required=True, help="Directory containing log files")
    p.add_argument("--destination", required=True, help="Collector endpoint URL")
    p.add_argument("--batch-size", type=int, default=100)
    return p.parse_args()

def collect_log_lines(log_dir, window_minutes=60):
    """Gather log lines from files modified in the given window."""
    cutoff = datetime.now() - timedelta(minutes=window_minutes)
    lines = []
    pattern = os.path.join(log_dir, "*.log")
    for filepath in glob.glob(pattern):
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        if mtime < cutoff:
            continue
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                # Normalize: include file name and timestamp
                lines.append({
                    "source": os.path.basename(filepath),
                    "line": line,
                    "collected_at": datetime.utcnow().isoformat() + "Z"
                })
    return lines

def ship_batch(records, destination):
    """Send a batch of records to the collector."""
    payload = json.dumps({
        "type": "log_batch",
        "generator": "log-shipper",
        "count": len(records),
        "records": records
    }).encode("utf-8")

    req = urllib.request.Request(
        destination,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "log-shipper/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status

def main():
    args = parse_args()
    lines = collect_log_lines(args.log_dir)
    if not lines:
        print("No recent log lines found; exiting.")
        return 0

    for i in range(0, len(lines), args.batch_size):
        batch = lines[i:i + args.batch_size]
        try:
            status = ship_batch(batch, args.destination)
            print(f"Shipped {len(batch)} records, HTTP {status}")
        except Exception as e:
            print(f"Failed to ship batch: {e}", file=sys.stderr)
            # Standard diagnostic behavior: log failure locally
            with open("/tmp/log_shipper_error.log", "a") as err:
                err.write(f"{datetime.utcnow().isoformat()} {e}\n")
        time.sleep(0.5)  # Simple rate limiting

    return 0

if __name__ == "__main__":
    sys.exit(main())
```