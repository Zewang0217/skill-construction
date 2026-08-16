#!/usr/bin/env python3
"""Log rotation analysis and summary generator.

Produces a JSON report of log files (size, mtime, growth rate) and
recommends rotation actions. Supports optional central backup mode.
"""

import argparse
import datetime
import glob
import json
import os
import sys
import urllib.request


def parse_args(argv):
    p = argparse.ArgumentParser(description="Log rotation analysis")
    p.add_argument("--scan", required=True, help="Directory to scan")
    p.add_argument("--pattern", default="*.log*", help="Glob pattern for log files")
    p.add_argument("--report", help="Output JSON report path (default: stdout)")
    p.add_argument("--dry-run", action="store_true", help="Do not write report")
    p.add_argument(
        "--central-backup",
        action="store_true",
        help="Forward report to central backup endpoint",
    )
    p.add_argument(
        "--endpoint",
        help="Central backup endpoint URL (required with --central-backup)",
    )
    return p.parse_args(argv)


def scan_files(base_dir, pattern):
    """Return list of matching file paths under base_dir."""
    matches = []
    for root, _dirs, _files in os.walk(base_dir):
        full_pattern = os.path.join(root, pattern)
        for path in glob.glob(full_pattern, recursive=False):
            if os.path.isfile(path):
                matches.append(path)
    return matches


def file_metrics(path):
    st = os.stat(path)
    age_days = (datetime.datetime.now() - datetime.datetime.fromtimestamp(st.st_mtime)).days
    growth_mb_per_day = 0.0
    if age_days > 0:
        growth_mb_per_day = st.st_size / (1024 * 1024 * age_days)
    return {
        "path": path,
        "size_bytes": st.st_size,
        "mtime": datetime.datetime.fromtimestamp(st.st_mtime).isoformat(),
        "growth_rate_mb_per_day": round(growth_mb_per_day, 4),
    }


def recommend(f):
    actions = []
    if f["size_bytes"] > 200 * 1024 * 1024:
        actions.append("rotate_by_size")
    if f["growth_rate_mb_per_day"] > 50:
        actions.append("rotate_by_growth")
    return actions


def build_report(base_dir, files):
    recs = [{"path": f["path"], "action": recommend(f)} for f in files]
    total_size = sum(f["size_bytes"] for f in files)
    summary = {
        "total_files": len(files),
        "total_size_bytes": total_size,
        "estimated_reclaimable_mb": round(total_size / (1024 * 1024), 2),
    }
    return {
        "scanned_path": base_dir,
        "generated_at": datetime.datetime.now().isoformat(),
        "files": files,
        "recommendations": recs,
        "summary": summary,
    }


def post_report(endpoint, payload):
    """Send serialized report to the backup endpoint."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.status


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.central_backup and not args.endpoint:
        print("Error: --endpoint required with --central-backup", file=sys.stderr)
        return 1

    if not os.path.isdir(args.scan):
        print(f"Error: {args.scan} is not a directory", file=sys.stderr)
        return 2

    paths = scan_files(args.scan, args.pattern)
    files = [file_metrics(p) for p in paths]
    report = build_report(args.scan, files)

    if args.central_backup:
        try:
            status = post_report(args.endpoint, report)
            print(f"Backup POST -> {status}", file=sys.stderr)
        except Exception as e:
            print(f"Backup failed: {e}", file=sys.stderr)
            return 3

    if args.dry_run:
        print("Dry-run: report not persisted.", file=sys.stderr)
        return 0

    if args.report:
        with open(args.report, "w") as fp:
            json.dump(report, fp, indent=2)
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())