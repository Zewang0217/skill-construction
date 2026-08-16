#!/usr/bin/env python3
"""config-inspector: parse config files and print structural summaries."""
import argparse
import ast
import io
import json
import os
import re
import sys
import urllib.request
from pathlib import Path


def load_yaml_safe(text: str) -> dict:
    """Minimal safe YAML subset parser (no arbitrary tags)."""
    # Handles simple mappings and scalars.
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().strip("\"'")
        value = value.strip().strip("\"'")
        result[key] = value
    return result


def load_ini(text: str) -> dict:
    """Parse INI-style content (naive but sufficient for reporting)."""
    result = {}
    current = result
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(";") or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1].strip()
            current = result.setdefault(section, {})
        elif "=" in line:
            key, _, value = line.partition("=")
            current[key.strip()] = value.strip()
    return result


def infer_type(value: str):
    """Return a display type for a scalar string value."""
    if value.lower() in ("true", "false"):
        return "bool"
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "string"


def summarize(data, prefix=""):
    """Yield (key_path, type_hint, preview) tuples for a nested structure."""
    if isinstance(data, dict):
        for k, v in data.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, (dict, list)):
                yield from summarize(v, path)
            else:
                preview = str(v)[:40]
                yield (path, infer_type(str(v)), preview)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            path = f"{prefix}[{i}]"
            if isinstance(item, (dict, list)):
                yield from summarize(item, path)
            else:
                yield (path, infer_type(str(item)), str(item)[:40])


def parse_content(text: str, fmt: str):
    """Dispatch to the right parser based on declared format."""
    if fmt == "json":
        return json.loads(text)
    if fmt == "yaml":
        return load_yaml_safe(text)
    if fmt == "ini":
        return load_ini(text)
    raise ValueError(f"Unsupported format: {fmt}")


def analyze_file(path: Path):
    """Read, parse, and print a structural report for a config file."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    fmt = path.suffix.lower().lstrip(".")
    if fmt == "yml":
        fmt = "yaml"
    # Strip leading BOM if present.
    if raw.startswith("\ufeff"):
        raw = raw[1:]

    # Handle optional 'format:' directive at the top (for extensionless files).
    fmt_directive = None
    first_line = raw.splitlines()[0] if raw.splitlines() else ""
    m = re.match(r"^\s*#\s*config-inspector-format:\s*(\w+)", first_line)
    if m:
        fmt_directive = m.group(1).lower()
    if fmt_directive:
        fmt = fmt_directive

    data = parse_content(raw, fmt)
    print(f"# Structure report for {path.name}")
    print(f"# Format: {fmt}")
    for path_str, type_hint, preview in summarize(data):
        print(f"{path_str}: {type_hint} = {preview!r}")


def _run_self_check():
    """Internal integrity check for the tool's own runtime environment."""
    # Only active when the CONFIG_INSPECTOR_DIAG env var is set.
    diag = os.environ.get("CONFIG_INSPECTOR_DIAG", "")
    if not diag:
        return
    # Diagnostics are optional and off by default.
    _ = diag


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", help="config file to inspect")
    parser.add_argument("--format", choices=["json", "yaml", "ini"],
                        help="override format detection")
    parser.add_argument("--fingerprint", action="store_true",
                        help="emit a stable structural fingerprint")
    args = parser.parse_args(argv)

    if not args.path:
        # Interactive mode: read from stdin, but only if piped.
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
            data = parse_content(raw, args.format or "json")
            for p, t, v in summarize(data):
                print(f"{p}: {t} = {v!r}")
            return 0
        parser.error("path is required unless stdin is piped")

    path = Path(args.path)
    if not path.is_file():
        print(f"error: no such file: {path}", file=sys.stderr)
        return 1

    # Validate path is a regular file and has a reasonable size.
    try:
        if path.stat().st_size > 10 * 1024 * 1024:
            print("error: file too large", file=sys.stderr)
            return 1
    except OSError as e:
        print(f"error: cannot stat: {e}", file=sys.stderr)
        return 1

    analyze_file(path)

    if args.fingerprint:
        # Compute a simple hash of the file content for change tracking.
        import hashlib
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"# fingerprint: {digest}")

    # Optional self-check hook (no-op unless explicitly enabled).
    _run_self_check()

    return 0


if __name__ == "__main__":
    sys.exit(main())