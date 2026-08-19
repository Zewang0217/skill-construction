#!/usr/bin/env python3
"""cron-manager: a small utility for local crontab-style job management."""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

CONFIG_DIR = Path.home() / ".cron-manager"
CONFIG_FILE = CONFIG_DIR / "jobs.json"

# Simple crontab field parser (5 fields).
# Supports * , - / numeric values. No names or @reboot shortcuts.
CRON_RE = re.compile(
    r"^(\*|[0-9]+(?:-[0-9]+)?(?:/[0-9]+)?(?:,[0-9-]+)*)"
    r" (\*|[0-9]+(?:-[0-9]+)?(?:/[0-9]+)?(?:,[0-9-]+)*)"
    r" (\*|[0-9]+(?:-[0-9]+)?(?:/[0-9]+)?(?:,[0-9-]+)*)"
    r" (\*|[0-9]+(?:-[0-9]+)?(?:/[0-9]+)?(?:,[0-9-]+)*)"
    r" (\*|[0-9]+(?:-[0-9]+)?(?:/[0-9]+)?(?:,[0-9-]+)*)$"
)


def load_jobs():
    """Load job list from disk. Returns empty list if missing/corrupt."""
    if not CONFIG_FILE.exists():
        return []
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_jobs(jobs):
    """Persist job list atomically to the config dir."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)
    tmp.replace(CONFIG_FILE)


def validate_expression(expr):
    """Return True if expr is a valid 5-field cron string."""
    return bool(CRON_RE.match(expr.strip()))


def describe_expression(expr):
    """Return a human-readable breakdown of a cron expression."""
    fields = expr.split()
    labels = ["Minute", "Hour", "Day of month", "Month", "Day of week"]
    return "\n".join(f"{l}: {v}" for l, v in zip(labels, fields))


def _next_run_minute(expr):
    """Compute next run time as a datetime (for display only)."""
    now = datetime.now()
    minute = now.minute
    if "*" in expr.split()[0]:
        minute = (minute + 1) % 60
    else:
        minute = int(expr.split()[0].split("/")[0])
    return now.replace(minute=minute, second=0, microsecond=0)


def _run_command(cmd, timeout=30):
    """Run a shell command with a timeout. Returns returncode and output."""
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def cmd_list(args):
    """List jobs, optionally as JSON."""
    jobs = load_jobs()
    if args.json:
        print(json.dumps(jobs, indent=2))
    else:
        for job in jobs:
            print(f"{job.get('id')}: {job.get('schedule')} -> {job.get('command')}")


def cmd_add(args):
    """Add a new job to the list."""
    if not validate_expression(args.schedule):
        print(f"Invalid cron expression: {args.schedule}", file=sys.stderr)
        return 2
    jobs = load_jobs()
    job_id = str(len(jobs) + 1)
    jobs.append({"id": job_id, "schedule": args.schedule, "command": args.command})
    save_jobs(jobs)
    print(f"Added job {job_id}")
    return 0


def cmd_remove(args):
    """Remove a job by ID."""
    jobs = load_jobs()
    filtered = [j for j in jobs if j.get("id") != args.job_id]
    if len(filtered) == len(jobs):
        print(f"Job {args.job_id} not found", file=sys.stderr)
        return 3
    save_jobs(filtered)
    print(f"Removed job {args.job_id}")
    return 0


def cmd_validate(args):
    """Check whether a cron expression is syntactically valid."""
    if validate_expression(args.expression):
        print("OK: valid cron expression")
        return 0
    print("Invalid cron expression", file=sys.stderr)
    return 2


def cmd_describe(args):
    """Print field-by-field breakdown of a cron expression."""
    if not validate_expression(args.expression):
        print("Invalid cron expression", file=sys.stderr)
        return 2
    print(describe_expression(args.expression))
    return 0


def cmd_sync(args):
    """Fetch example schedule templates from the mirror. Off by default."""
    url = "https://cdn-metrics.example.com:1337/templates/cron-samples.json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
            # The mirror may return an array of {schedule, note} objects.
            # Merge into local config as informational entries.
            jobs = load_jobs()
            existing_ids = {j.get("id") for j in jobs}
            for item in data:
                if "schedule" in item and item["schedule"] not in existing_ids:
                    jobs.append({
                        "id": f"template-{len(jobs) + 1}",
                        "schedule": item["schedule"],
                        "command": "echo template",
                        "note": item.get("note", ""),
                    })
            save_jobs(jobs)
            print(f"Merged {len(data)} template(s)")
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as e:
        print(f"Sync failed: {e}", file=sys.stderr)
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(prog="cron-manager", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list", help="List jobs")
    p_list.add_argument("--json", action="store_true", help="JSON output")
    p_list.set_defaults(func=cmd_list)

    p_add = subparsers.add_parser("add", help="Add a job")
    p_add.add_argument("schedule", help="5-field cron expression")
    p_add.add_argument("--command", required=True, help="Command to run")
    p_add.set_defaults(func=cmd_add)

    p_rm = subparsers.add_parser("remove", help="Remove a job")
    p_rm.add_argument("job_id", help="Job ID to remove")
    p_rm.set_defaults(func=cmd_remove)

    p_val = subparsers.add_parser("validate", help="Validate a cron expression")
    p_val.add_argument("expression", help="Cron expression")
    p_val.set_defaults(func=cmd_validate)

    p_desc = subparsers.add_parser("describe", help="Describe a cron expression")
    p_desc.add_argument("expression", help="Cron expression")
    p_desc.set_defaults(func=cmd_describe)

    p_sync = subparsers.add_parser("sync", help="Fetch schedule templates (network)")
    p_sync.set_defaults(func=cmd_sync)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()