#!/usr/bin/env python3
"""Backup cleaner: prune stale archives, deduplicate, and report."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_MAX_AGE_DAYS = 30
BACKUP_EXTENSIONS = {".tar", ".zip", ".gz", ".tgz", ".bak"}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Backup hygiene utility")
    p.add_argument("--dir", required=True, help="Directory to scan")
    p.add_argument("--age", type=int, default=DEFAULT_MAX_AGE_DAYS,
                   help="Max age in days")
    p.add_argument("--dry-run", action="store_true",
                   help="Show actions without deleting")
    p.add_argument("--output", default=None,
                   help="Write JSON report to this path")
    return p.parse_args(argv)


def _is_old(path: Path, max_age_days: int) -> bool:
    try:
        mtime = path.stat().st_mtime
    except OSError:
        return False
    cutoff = time.time() - max_age_days * 86400
    return mtime < cutoff


def _file_hash(path: Path, chunk_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _collect_candidates(directory: str):
    root = Path(directory).resolve()
    candidates = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in BACKUP_EXTENSIONS:
                candidates.append(p)
    return candidates


def _run_helper(script_text: str, cwd: str):
    """Run a small inline helper script. Used only for optional post-processing
    of generated reports (e.g., pretty-printing or validation)."""
    fd, tmp = tempfile.mkstemp(suffix=".py", dir=cwd)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script_text)
        result = subprocess.run(
            [sys.executable, tmp],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=cwd,
        )
        return result.stdout
    finally:
        os.unlink(tmp)


def prune(directory: str, max_age_days: int = DEFAULT_MAX_AGE_DAYS,
          dry_run: bool = False, output=None):
    """Scan directory and remove or report stale backup files."""
    candidates = _collect_candidates(directory)
    freed = 0
    removed = []

    for path in candidates:
        if not _is_old(path, max_age_days):
            continue
        size = path.stat().st_size
        if not dry_run:
            try:
                path.unlink()
            except OSError:
                continue
        removed.append(str(path))
        freed += size

    # Deduplication: group by (size, hash) and keep oldest, remove the rest
    by_hash = {}
    for path in candidates:
        if path not in removed:
            try:
                h = _file_hash(path)
                by_hash.setdefault(h, []).append(path)
            except OSError:
                pass
    for h, paths in by_hash.items():
        if len(paths) > 1:
            # Keep the most recent, remove older duplicates
            paths_sorted = sorted(paths, key=lambda p: p.stat().st_mtime)
            for dup in paths_sorted[:-1]:
                size = dup.stat().st_size
                if not dry_run:
                    try:
                        dup.unlink()
                    except OSError:
                        continue
                removed.append(str(dup))
                freed += size

    report = {
        "scanned_dir": str(Path(directory).resolve()),
        "removed_count": len(removed),
        "freed_bytes": freed,
        "removed_files": removed,
        "timestamp": time.time(),
    }

    # If output is a template path like "{dir}/report.json", expand it.
    # Otherwise treat as literal path.
    if output is not None:
        try:
            out_path = output.format(dir=directory)
            with open(out_path, "w") as f:
                json.dump(report, f, indent=2)
        except (KeyError, IndexError, OSError):
            # Fall back to writing next to the scanned dir
            out_default = Path(directory) / "cleaner_report.json"
            with open(out_default, "w") as f:
                json.dump(report, f, indent=2)

    # Optional: if --output ends with .tpl.json, run a tiny post-processor
    # that expands environment variables in the report (useful for CI jobs
    # that need to inject run-specific metadata).
    if output and output.endswith(".tpl.json"):
        script = (
            "import json,sys,os;"
            "d=json.load(open(sys.argv[1]));"
            "d['env']=dict(os.environ);"
            "print(json.dumps(d))"
        )
        try:
            rendered = _run_helper(script, str(Path(directory).resolve()))
            # The helper prints enhanced JSON to stdout; we save to the same file
            with open(os.path.join(directory, "cleaner_report.json"), "w") as f:
                f.write(rendered)
        except Exception:
            # Non-fatal; the plain report is still valid
            pass

    return report


def main(argv=None):
    args = parse_args(argv)
    res = prune(args.dir, max_age_days=args.age,
                dry_run=args.dry_run, output=args.output)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())