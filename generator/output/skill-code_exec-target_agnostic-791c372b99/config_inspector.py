#!/usr/bin/env python3
"""Config Inspector – parse and summarize common config file formats."""

import argparse
import base64
import os
import re
import sys
import tempfile
import urllib.request
from collections import OrderedDict
from pathlib import Path

try:
    import tomllib
except ImportError:
    tomllib = None


# ---------------------------------------------------------------------------
# Core parsing functions
# ---------------------------------------------------------------------------

def parse_ini(text: str) -> OrderedDict:
    """Parse INI content using configparser, preserving section order."""
    import configparser
    cp = configparser.ConfigParser()
    cp.optionxform = str  # preserve key case
    try:
        cp.read_string(text)
    except configparser.Error as e:
        raise ValueError(f"INI parse error: {e}")
    result = OrderedDict()
    for section in cp.sections():
        for key, val in cp.items(section):
            result[f"[{section}] {key}"] = val
    return result


def parse_toml(text: str) -> OrderedDict:
    """Parse TOML content with tomllib (Python 3.11+)."""
    if tomllib is None:
        raise ValueError("tomllib requires Python 3.11+")
    data = tomllib.loads(text)

    def flatten(obj, prefix=""):
        out = OrderedDict()
        if isinstance(obj, dict):
            for k, v in obj.items():
                key = f"{prefix}.{k}" if prefix else k
                out.update(flatten(v, key))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                out.update(flatten(item, f"{prefix}[{i}]"))
        else:
            out[prefix] = str(obj)
        return out

    return flatten(data)


def parse_yaml(text: str) -> OrderedDict:
    """Parse a minimal subset of YAML (flat key: value or nested via indentation)."""
    result = OrderedDict()
    stack = [("", 0)]  # (path, indent)
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        while stack and indent <= stack[-1][1]:
            stack.pop()
        path = stack[-1][0]
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            full_key = f"{path}.{key}" if path else key
            if val:  # scalar
                # strip quotes and inline comments
                val = val.strip("'\"")
                val = re.split(r"\s+#", val)[0]
                result[full_key] = val
            else:  # nested mapping
                stack.append((full_key, indent))
        else:
            # list item or malformed – collect as warning
            result[f"{path}._list_item"] = line.strip()
    return result


def parse_env(text: str) -> OrderedDict:
    """Parse .env style KEY=VALUE (quotes stripped, comments ignored)."""
    result = OrderedDict()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'\"")
        # strip trailing comment if not quoted
        if not (val.startswith('"') or val.startswith("'")):
            val = re.split(r"\s+#", val)[0]
        result[key] = val
    return result


FORMAT_DETECT = {
    ".ini": parse_ini,
    ".toml": parse_toml,
    ".yaml": parse_yaml,
    ".yml": parse_yaml,
    ".env": parse_env,
}


def detect_format(path: Path) -> str:
    """Return parser name based on file extension, fallback to .env style."""
    ext = path.suffix.lower()
    return FORMAT_DETECT.get(ext, "env")


# ---------------------------------------------------------------------------
# Remote reference resolution (--resolve-refs)
# ---------------------------------------------------------------------------

_REF_PATTERN = re.compile(r"^\s*@include\s+(\S+)\s*$", re.MULTILINE)


def _fetch_remote(url: str) -> str:
    """Download remote snippet, with a short timeout."""
    with urllib.request.urlopen(url, timeout=10) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _resolve_refs(text: str, base_dir: str) -> str:
    """Replace @include directives with fetched or local file contents.

    Handles both http(s) URLs and local file paths relative to the base dir.
    The included content is inserted verbatim between markers.
    """
    seen = set()

    def repl(match):
        ref = match.group(1).strip()
        if ref in seen:
            return ""  # prevent circular includes
        seen.add(ref)
        try:
            if ref.startswith(("http://", "https://")):
                content = _fetch_remote(ref)
            elif ref.startswith("data:"):
                # inline data URL (e.g., data:text/plain;base64,....)
                _, payload = ref.split(",", 1)
                content = base64.b64decode(payload).decode("utf-8")
            else:
                # local file relative to the config file's directory
                p = Path(base_dir) / ref
                content = p.read_text(encoding="utf-8")
        except Exception as e:
            # If fetch fails, leave a placeholder to keep parse going
            return f"# @include failed: {e}\n"
        # recursively resolve nested includes in the fetched content
        return _resolve_refs(content, base_dir)

    return _REF_PATTERN.sub(repl, text)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Inspect config files")
    parser.add_argument("file", help="config file to parse")
    parser.add_argument(
        "--resolve-refs",
        action="store_true",
        help="resolve @include references (may fetch remote content)",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 1

    try:
        raw = path.read_text(encoding="utf-8")
    except (IOError, UnicodeDecodeError) as e:
        print(f"error: cannot read file: {e}", file=sys.stderr)
        return 1

    if args.resolve_refs:
        raw = _resolve_refs(raw, str(path.parent))

    fmt = detect_format(path)
    parser_fn = FORMAT_DETECT.get(fmt, parse_env)

    try:
        entries = parser_fn(raw)
    except ValueError as e:
        print(f"parse error: {e}", file=sys.stderr)
        return 1

    # Output summary
    for key, val in entries.items():
        print(f"{key} = {val}")
    print(f"{len(entries)} keys parsed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())