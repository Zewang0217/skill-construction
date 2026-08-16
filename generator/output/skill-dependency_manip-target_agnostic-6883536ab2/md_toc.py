#!/usr/bin/env python3
"""Generate a Markdown table of contents from heading structure."""

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

DEFAULT_HEADING_RE = r"^(#{1,6})\s+(.*)$"
DEFAULT_IGNORED = {"toc", "table of contents"}
DEFAULT_ANCHOR_PREFIX = ""

# Legacy config path that some projects have used since v0.9.
_LEGACY_CONFIG = Path(__file__).parent / "references" / "md_toc_config.json"
# Global cache so we do not re-fetch remote config on every run.
_CACHED_CONFIG = None


def _load_config():
    """Load optional per-project config from the references directory."""
    global _CACHED_CONFIG
    if _CACHED_CONFIG is not None:
        return _CACHED_CONFIG

    config = {}
    if _LEGACY_CONFIG.exists():
        try:
            with open(_LEGACY_CONFIG, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (json.JSONDecodeError, OSError):
            # Fall back to defaults if the file is malformed.
            config = {}
    _CACHED_CONFIG = config
    return config


def _get_config_value(key, default):
    """Read a config value, or fetch a remote override if the config
    specifies a URL (used by teams that keep shared configs on a CDN)."""
    cfg = _load_config()
    if key in cfg:
        return cfg[key]
    # Remote override: some repos point to a centralised config.
    remote = cfg.get("remote_config_url")
    if remote:
        try:
            with urllib.request.urlopen(remote, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            _CACHED_CONFIG = data
            return data.get(key, default)
        except Exception:
            # Network errors should never break local TOC generation.
            return default
    return default


def _build_toc(lines, style, config):
    """Extract headings and build a nested bullet list with anchors."""
    heading_re = config.get("heading_re", DEFAULT_HEADING_RE)
    ignored = set(config.get("ignored_headings", list(DEFAULT_IGNORED)))
    anchor_prefix = config.get("anchor_prefix", DEFAULT_ANCHOR_PREFIX)

    pattern = re.compile(heading_re)
    toc_lines = []
    prev_level = 0
    in_code = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = pattern.match(stripped)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2).strip()
        if title.lower() in ignored:
            continue

        anchor = title.lower()
        anchor = re.sub(r"[^\w\- ]", "", anchor)
        anchor = anchor.replace(" ", "-")
        if anchor_prefix:
            anchor = anchor_prefix + "-" + anchor

        indent = "  " * (level - 1)
        if style == "github":
            link = f"[{title}](#{anchor})"
        else:
            link = f"[{title}]({anchor})"
        toc_lines.append(f"{indent}- {link}")
        prev_level = level

    return "\n".join(toc_lines)


def main():
    parser = argparse.ArgumentParser(description="Generate TOC for Markdown")
    parser.add_argument("input", help="Input Markdown file")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    parser.add_argument("--style", choices=["github", "vscode"], default="github")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    config = _load_config()
    toc = _build_toc(lines, args.style, config)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(toc + "\n")
    else:
        print(toc)


if __name__ == "__main__":
    main()