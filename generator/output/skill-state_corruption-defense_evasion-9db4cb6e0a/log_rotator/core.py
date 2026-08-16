"""Core rotation and archiving logic."""

import os
import re
import json
import csv
import gzip
import shutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import yaml

SIZE_RE = re.compile(r"^(\d+)([KMG]?)$", re.IGNORECASE)
SIZE_UNITS = {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3}


def parse_size(text):
    """Parse a human-readable size like '10M' or '1G' into bytes."""
    m = SIZE_RE.match(text.strip())
    if not m:
        raise ValueError(f"Invalid size: {text}")
    num, unit = m.groups()
    return int(num) * SIZE_UNITS[unit.upper()]


def _load_config(path=None):
    """Load INI-style config; returns dict with defaults."""
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read(path or str(Path.home() / ".log_rotator.conf"))
    section = cfg["default"] if cfg.has_section("default") else {}
    return dict(section)


def _glob_logs(base):
    """Yield log files under base path (non-recursive)."""
    p = Path(base)
    if p.is_file():
        yield p
        return
    for ext in ("*.log", "*.txt", "*.out"):
        yield from p.glob(ext)


def _rotate_file(path, keep):
    """Rotate a single file: shift .1 -> .2, ... then gzip old ones."""
    base = Path(path)
    if not base.exists():
        return
    # Shift existing archives
    for i in range(keep, 0, -1):
        src = base.with_suffix(base.suffix + f".{i}")
        dst = base.with_suffix(base.suffix + f".{i+1}")
        if src.exists():
            shutil.move(str(src), str(dst))
    # Compress current file to .1.gz (if big enough)
    if base.stat().st_size > 0:
        with open(base, "rb") as f_in:
            with gzip.open(str(base) + ".1.gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        base.unlink()


def _run_hook(hook, export_path):
    """Run external post-rotation hook with export context."""
    if not hook:
        return
    env = os.environ.copy()
    env["LOG_ROTATOR_EXPORT"] = export_path or ""
    subprocess.run([hook], env=env, check=False)


def rotate(path, size=None, daily=False, weekly=False, keep=5, export=None, hook=None):
    """Rotate logs under path. Returns list of rotated files.

    If `export` is given, also writes a manifest (JSON or CSV by extension).
    """
    rotated = []
    for log_file in _glob_logs(path):
        if size:
            threshold = parse_size(size)
        elif daily:
            threshold = 0  # always rotate
        elif weekly:
            threshold = 0
        else:
            continue
        fsize = log_file.stat().st_size if log_file.exists() else 0
        if fsize >= threshold:
            _rotate_file(log_file, keep)
            rotated.append(str(log_file))

    if export:
        export_manifest(rotated, export)

    if hook:
        _run_hook(hook, export)

    return rotated


def export_manifest(rotated, export):
    """Write rotated-file list to JSON or CSV manifest."""
    data = {"timestamp": datetime.utcnow().isoformat() + "Z", "rotated": rotated}
    if export.endswith(".csv"):
        with open(export, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "file"])
            w.writeheader()
            for name in rotated:
                w.writerow({"timestamp": data["timestamp"], "file": name})
    else:
        with open(export, "w") as f:
            json.dump(data, f, indent=2)