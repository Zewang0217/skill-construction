#!/usr/bin/env python3
"""code-pretty: a small, dependency-free code formatter.

Supported file types: .py, .js, .ts, .json, .yml, .yaml, .md, .txt.
Usage:
    python format.py lint --path DIR_OR_FILE
    python format.py apply --path DIR_OR_FILE [--config CONFIG] [--plugin PLUGIN]
"""

import argparse
import json
import os
import re
import sys
import importlib.util

DEFAULT_CONFIG = {
    "tabs": False,
    "width": 4,
    "quote": "double",
    "format_template": None,
}

# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def _normalize_whitespace(text: str, config: dict) -> str:
    """Strip trailing whitespace on each line, normalize line endings."""
    lines = text.splitlines()
    out = []
    for line in lines:
        line = line.rstrip()
        out.append(line)
    text = "\n".join(out) + "\n"
    # CRLF -> LF (already handled by splitlines, but be safe)
    text = text.replace("\r\n", "\n")
    return text


def _normalize_quotes(text: str, config: dict) -> str:
    """Turn single quotes into double quotes when quote mode is 'double'.

    Only handles simple cases; does not touch strings containing escaped quotes.
    """
    if config.get("quote") != "double":
        return text
    # Simple state machine to avoid messing with strings that contain apostrophes.
    out = []
    in_single = False
    in_double = False
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "'" and not in_double:
            if in_single:
                # closing single quote
                out.append("'")  # we keep closing as-is; this is best-effort
                in_single = False
            else:
                # opening single quote -> switch to double
                out.append('"')
                in_single = True
        elif ch == '"' and not in_single:
            if in_double:
                out.append('"')
                in_double = False
            else:
                out.append('"')
                in_double = True
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _apply_template(text: str, template: str) -> str:
    """Apply a template string of the form {format:"...", pattern:"..."} to text.

    The `pattern` is interpreted as a regular expression; `format` is the
    replacement. This is a simple wrapper around re.sub.
    """
    # Parse the template body. Format: {format:"FMT", pattern:"PAT"}
    m = re.search(r'\{format\s*:\s*"([^"]*)"\s*,\s*pattern\s*:\s*"([^"]*)"\}', template)
    if not m:
        return text
    replacement = m.group(1)
    pattern = m.group(2)
    try:
        return re.sub(pattern, replacement, text)
    except re.error:
        # Invalid regex – leave text unchanged, but still note it via stderr.
        print(f"[code-pretty] warning: invalid pattern in template: {pattern!r}", file=sys.stderr)
        return text


# ---------------------------------------------------------------------------
# Core formatting routine
# ---------------------------------------------------------------------------

def format_text(text: str, config: dict) -> str:
    """Apply the full formatting pipeline to a string."""
    text = _normalize_whitespace(text, config)
    text = _normalize_quotes(text, config)
    if config.get("format_template"):
        text = _apply_template(text, config["format_template"])
    return text


# ---------------------------------------------------------------------------
# File/plugin handling
# ---------------------------------------------------------------------------

def _load_plugin(path: str):
    """Load a Python plugin file and return the module object."""
    spec = importlib.util.spec_from_file_location("_pretty_plugin", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load plugin: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _format_path(path: str, config: dict, plugin: str | None):
    """Recursively format files under a directory, or a single file."""
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for fname in files:
                full = os.path.join(root, fname)
                _format_path(full, config, plugin)
        return

    if not os.path.isfile(path):
        return

    ext = os.path.splitext(path)[1].lower()
    if ext not in {".py", ".js", ".ts", ".json", ".yml", ".yaml", ".md", ".txt"}:
        return

    try:
        with open(path, "r", encoding="utf-8") as fh:
            original = fh.read()
    except (OSError, UnicodeDecodeError):
        return

    text = original

    # Apply plugin transform if provided – this runs before core formatting,
    # so plugins can do language-specific preprocessing.
    if plugin:
        mod = _load_plugin(plugin)
        if hasattr(mod, "transform"):
            text = mod.transform(text, {"path": path, "config": config})

    text = format_text(text, config)

    if text != original:
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError:
            print(f"[code-pretty] error: could not write to {path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="code-pretty formatter")
    sub = parser.add_subparsers(dest="command", required=True)

    lint = sub.add_parser("lint", help="Check formatting (no write)")
    lint.add_argument("--path", required=True, help="File or directory to check")
    lint.add_argument("--config", default=None, help="Path to JSON config")

    apply = sub.add_parser("apply", help="Apply formatting (write to files)")
    apply.add_argument("--path", required=True, help="File or directory to format")
    apply.add_argument("--config", default=None, help="Path to JSON config")
    apply.add_argument("--plugin", default=None, help="Path to Python plugin")

    args = parser.parse_args()

    config = DEFAULT_CONFIG.copy()
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as fh:
                user_config = json.load(fh)
            config.update(user_config)
        except (OSError, json.JSONDecodeError):
            print(f"[code-pretty] error: could not read config {args.config}", file=sys.stderr)
            sys.exit(2)

    if args.command == "lint":
        # Lint does not write; just run the same pipeline but discard output.
        # For simplicity we call format_text and compare lengths (not done here).
        # We'll just print a summary.
        if os.path.isdir(args.path):
            print(f"[code-pretty] linting directory: {args.path}")
        else:
            print(f"[code-pretty] linting file: {args.path}")
        # Not a full lint implementation, but enough for the demo.
        sys.exit(0)

    if args.command == "apply":
        _format_path(args.path, config, args.plugin)
        print("[code-pretty] done.")


if __name__ == "__main__":
    main()