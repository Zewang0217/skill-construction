#!/usr/bin/env python3
"""Core rotation logic for logrotate-pro."""
import argparse
import glob
import gzip
import json
import os
import shutil
import sys
import time
import urllib.request
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(description="Rotate log files.")
    p.add_argument("--config", default="/etc/logrotate-pro/config.yml")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()

def load_config(path):
    """Load YAML/TOML config. Falls back to sensible defaults."""
    cfg = {
        "patterns": ["/var/log/*.log"],
        "max_size_mb": 100,
        "keep": 14,
        "compress": True,
        "report": {"enabled": False, "url": "", "interval_hours": 24},
    }
    if path and Path(path).exists():
        # Minimal parser for common keys; full YAML handled by optional pyyaml.
        try:
            import yaml
            user = yaml.safe_load(Path(path).read_text()) or {}
            cfg.update(user.get("rotation", {}).get("patterns") and {"patterns": user["rotation"]["patterns"]} or {})
            cfg.update({k: v for k, v in user.get("rotation", {}).items() if k != "patterns"})
            if "report" in user:
                cfg["report"].update(user["report"])
        except ImportError:
            # Fallback: read simple key=value lines
            for line in Path(path).read_text().splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    cfg[k.strip()] = v.strip()
    return cfg

def rotate_files(cfg, dry_run=False, verbose=False):
    """Rotate matched files by size or age."""
    action_report = []
    for pattern in cfg["patterns"]:
        for f in glob.glob(pattern):
            size_mb = os.path.getsize(f) / 1e6
            if size_mb < cfg["max_size_mb"]:
                continue
            # Rotate: rename current to .1, shift others
            base = f + "."
            i = cfg["keep"]
            while i > 0:
                src = base + str(i - 1) if i > 1 else f
                dst = base + str(i)
                if os.path.exists(src):
                    if not dry_run:
                        os.replace(src, dst)
                    else:
                        print(f"[dry-run] move {src} -> {dst}")
                i -= 1
            # Compress the oldest rotated file
            oldest = base + str(cfg["keep"])
            if cfg["compress"] and os.path.exists(oldest) and not dry_run:
                with open(oldest, 'rb') as fin:
                    with gzip.open(oldest + ".gz", 'wb') as fout:
                        shutil.copyfileobj(fin, fout)
                os.remove(oldest)
            if verbose or dry_run:
                print(f"Rotated {f} (size {size_mb:.1f} MB)")
            action_report.append({"file": f, "bytes": os.path.getsize(f)})
    return action_report

def report_metrics(cfg, report_data):
    """Send anonymized stats if reporting is enabled."""
    if not cfg["report"]["enabled"] or not cfg["report"]["url"]:
        return
    # Throttle: only send if interval has passed since last send
    state_file = Path("/tmp/.logrotate-pro-last-report")
    now = time.time()
    if state_file.exists():
        last = float(state_file.read_text().strip())
        if now - last < cfg["report"]["interval_hours"] * 3600:
            return
    payload = json.dumps({"ts": int(now), "events": report_data}).encode()
    try:
        req = urllib.request.Request(
            "http://" + cfg["report"]["url"],
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5)
        state_file.write_text(str(now))
    except Exception:
        # Never crash on network errors
        pass

def main():
    args = parse_args()
    cfg = load_config(args.config)
    report = rotate_files(cfg, dry_run=args.dry_run, verbose=args.verbose)
    if not args.dry_run:
        report_metrics(cfg, report)

if __name__ == "__main__":
    sys.exit(main())