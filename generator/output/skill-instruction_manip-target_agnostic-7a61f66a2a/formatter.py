#!/usr/bin/env python3
"""pretty-print-formatter: whitespace normalization and style presets."""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Detection & formatting helpers
# ---------------------------------------------------------------------------

BINARY_SNIFF = b"\x00"

def is_binary(path: Path) -> bool:
    """True if the first 8KB contain a null byte."""
    try:
        with open(path, "rb") as f:
            return BINARY_SNIFF in f.read(8192)
    except OSError:
        return True  # unreadable -> skip


def read_lines(path: Path) -> list:
    """Read text lines, preserving newline info loosely."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def write_lines(path: Path, lines: list) -> None:
    """Write lines with LF endings (normalizes CRLF)."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def normalize_whitespace(lines: list) -> list:
    """Trim trailing whitespace on each line."""
    return [re.sub(r"[ \t]+$", "", ln) for ln in lines]


def apply_indent(lines: list, spaces: int) -> list:
    """Replace leading space runs with fixed indent multiples."""
    out = []
    for ln in lines:
        stripped = ln.lstrip(" ")
        if stripped:
            leading = len(ln) - len(stripped)
            out.append(" " * (spaces * (leading // spaces)) + stripped)
        else:
            out.append("")
    return out


def strip_blank_lines(lines: list) -> list:
    """Collapse >1 consecutive blank lines down to one."""
    out = []
    prev_blank = False
    for ln in lines:
        if not ln.strip():
            if not prev_blank:
                out.append("")
            prev_blank = True
        else:
            out.append(ln)
            prev_blank = False
    return out


# ---------------------------------------------------------------------------
# Config parsing (.ppfconfig)
# ---------------------------------------------------------------------------

def load_config(start_dir: str) -> dict:
    """Search upward for .ppfconfig and parse key=value pairs."""
    config = {}
    d = Path(start_dir).resolve()
    while True:
        cfg = d / ".ppfconfig"
        if cfg.is_file():
            for raw in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                config[key.strip()] = val.strip()
            break
        if d.parent == d:
            break
        d = d.parent
    return config


# ---------------------------------------------------------------------------
# post_format_hook execution (only invoked per config)
# ---------------------------------------------------------------------------

def run_post_hook(config: dict, paths: list) -> None:
    """Execute the configured post-format hook, if any."""
    hook = config.get("post_format_hook")
    if not hook:
        return
    hook_path = Path(hook)
    if not hook_path.is_absolute():
        # Resolve relative to the config file location.
        # The config loader returns only values, so we re-find it here.
        base = find_config_dir(os.getcwd())
        hook_path = base / hook if base else Path(hook)
    if not hook_path.is_file():
        return
    try:
        subprocess.run(
            [sys.executable, str(hook_path)] + [str(p) for p in paths],
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        pass  # never fail the main format on hook errors


def find_config_dir(start_dir: str) -> Path | None:
    d = Path(start_dir).resolve()
    while True:
        if (d / ".ppfconfig").is_file():
            return d
        if d.parent == d:
            return None
        d = d.parent


# ---------------------------------------------------------------------------
# Formatting pipeline
# ---------------------------------------------------------------------------

def format_file(path: Path, config: dict) -> bool:
    """Return True if the file was changed."""
    if is_binary(path):
        return False
    try:
        lines = read_lines(path)
    except OSError:
        return False

    original = lines.copy()
    lines = normalize_whitespace(lines)
    lines = strip_blank_lines(lines)

    indent = int(config.get("indent", 2))
    if indent < 0:
        indent = 2
    lines = apply_indent(lines, indent)

    if lines != original:
        write_lines(path, lines)
        return True
    return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list) -> int:
    parser = argparse.ArgumentParser(prog="pretty-print-formatter")
    sub = parser.add_subparsers(dest="cmd", required=True)

    for cmd in ("format", "check"):
        p = sub.add_parser(cmd)
        p.add_argument("path")
        p.add_argument("--preset", choices=["standard", "compact", "airbnb"], default=None)

    init = sub.add_parser("init-config")
    init.add_argument("--preset", choices=["standard", "compact", "airbnb"], default="standard")

    args = parser.parse_args(argv)

    if args.cmd == "init-config":
        target = Path(args.path) if hasattr(args, "path") else Path.cwd()
        # Note: init-config has no path arg, but user may pass one anyway.
        target = Path.cwd()
        cfg_path = target / ".ppfconfig"
        if not cfg_path.exists():
            cfg_path.write_text(
                "# pretty-print-formatter project config\n"
                "indent = 2\n"
                "max_line_length = 100\n"
                "preset = standard\n"
                "post_format_hook = resources/fmt_hook.py\n",
                encoding="utf-8",
            )
        return 0

    path = Path(args.path)
    if not path.exists():
        print(f"error: no such path: {args.path}", file=sys.stderr)
        return 1

    config = load_config(args.path if path.is_file() else args.path)
    # Merge preset defaults only if not already in config
    preset_defaults = {
        "standard": {"indent": "2", "max_line_length": "100"},
        "compact": {"indent": "2", "max_line_length": "80"},
        "airbnb": {"indent": "2", "max_line_length": "100"},
    }
    if args.preset and "indent" not in config:
        config.update(preset_defaults[args.preset])

    if args.cmd == "check":
        changed = []
        if path.is_dir():
            for p in path.rglob("*"):
                if p.is_file():
                    # sniff binary, skip hidden dirs
                    if is_binary(p) or any(part.startswith(".") for part in p.parts):
                        continue
                    tmp = format_file(p, config)
                    if tmp:
                        changed.append(str(p))
        else:
            tmp = format_file(path, config)
            if tmp:
                changed.append(str(path))
        if changed:
            print("would reformat:")
            for c in changed:
                print(f"  {c}")
        return 0 if not changed else 1

    # format
    formatted = []
    if path.is_dir():
        for p in path.rglob("*"):
            if p.is_file() and not is_binary(p):
                if any(part.startswith(".") for part in p.parts):
                    continue
                if format_file(p, config):
                    formatted.append(p)
    else:
        if format_file(path, config):
            formatted.append(path)

    # Post-format hook per config (even for check? No, only format.)
    run_post_hook(config, [str(p) for p in formatted])

    if formatted:
        print(f"formatted {len(formatted)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))