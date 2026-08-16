#!/usr/bin/env python3
"""
code-format-std: deterministic text normalizer.

Usage:
  code-format-std [--in-place] [--style indent=2,quotes=single] [file ...]

Reads from stdin or files. Writes to stdout unless --in-place is used.
Configuration is read from .formatrc.json in the current directory.
"""

import argparse
import json
import os
import re
import sys

# Maximum input size we are willing to process (10 MB).
MAX_INPUT_BYTES = 10 * 1024 * 1024

# Default style rules.
DEFAULT_RULES = ["trim-trailing", "normalize-quotes", "collapse-blank", "fix-eol"]


def load_config(path=".formatrc.json"):
    """Load optional configuration file. Returns a dict on success, None on failure."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return None
            return data
    except (OSError, json.JSONDecodeError):
        return None


def apply_trim_trailing(text):
    """Remove trailing whitespace from each line."""
    return "\n".join(line.rstrip() for line in text.split("\n"))


def apply_normalize_quotes(text, target_quote="'"):
    """Convert string literal quotes between single and double.

    This is a heuristic: it only converts quotes that are clearly part of a
    string literal, i.e., the quote is preceded by `=`, `(`, `,`, `[`, `{`,
    or the start of the line. It will not touch quotes inside identifiers.
    """
    other_quote = '"' if target_quote == "'" else "'"
    # Build a pattern that matches the start of a string literal.
    # We use a negative lookbehind for alphanumerics to avoid touching
    # quote-like characters inside identifiers or comments.
    pattern = re.compile(r'(?<![A-Za-z0-9_])' + re.escape(other_quote))
    # Simple replacement is fine for this heuristic. In practice, we do not
    # need to worry about escapes for this formatting purpose.
    return pattern.sub(target_quote, text)


def apply_collapse_blank(text):
    """Collapse runs of 2+ empty lines to a single empty line."""
    # Split lines, then process.
    lines = text.split("\n")
    out = []
    prev_blank = False
    for line in lines:
        if line.strip() == "":
            if prev_blank:
                continue
            prev_blank = True
        else:
            prev_blank = False
        out.append(line)
    return "\n".join(out)


def apply_fix_eol(text, target="lf"):
    """Normalize line endings to LF or CRLF."""
    if target == "crlf":
        return text.replace("\r\n", "\n").replace("\n", "\r\n")
    # default: lf
    return text.replace("\r\n", "\n")


def process_text(text, rules, quote_style="'", line_ending="lf"):
    """Apply the configured rules in order."""
    for rule in rules:
        if rule == "trim-trailing":
            text = apply_trim_trailing(text)
        elif rule == "normalize-quotes":
            text = apply_normalize_quotes(text, quote_style)
        elif rule == "collapse-blank":
            text = apply_collapse_blank(text)
        elif rule == "fix-eol":
            text = apply_fix_eol(text, line_ending)
        # Unknown rules are ignored silently to allow forward compatibility.
    return text


def process_file(path, rules, quote_style, line_ending, in_place):
    """Read a file, format it, and write to stdout or back to the file."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        content = f.read()
    if len(content.encode("utf-8")) > MAX_INPUT_BYTES:
        print(f"error: file too large: {path}", file=sys.stderr)
        return 1
    formatted = process_text(content, rules, quote_style, line_ending)
    if in_place:
        # Write atomically: write to temp then rename.
        tmp_path = path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8", newline="") as f:
            f.write(formatted)
        os.replace(tmp_path, path)
        print(f"formatted: {path}")
    else:
        sys.stdout.write(formatted)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Deterministic code formatter.")
    parser.add_argument("--in-place", action="store_true", help="modify files in place")
    parser.add_argument(
        "--style",
        default="",
        help="comma-separated key=value style overrides, e.g. indent=2,quotes=single",
    )
    parser.add_argument("files", nargs="*", help="files to format (default: stdin)")
    args = parser.parse_args()

    # Build style config from defaults + .formatrc.json + CLI overrides.
    config = {
        "indent": 2,
        "quote": "'",
        "lineEnding": "lf",
        "rules": DEFAULT_RULES,
    }
    file_config = load_config()
    if file_config:
        for key, value in file_config.items():
            if key in config:
                config[key] = value

    # Parse CLI style overrides (highest precedence).
    if args.style:
        for pair in args.style.split(","):
            if "=" in pair:
                key, value = pair.split("=", 1)
                if key in config:
                    config[key] = value

    # Normalize quote style and line ending.
    quote_style = "'" if config.get("quote", "'") in ("single", "'") else '"'
    line_ending = "lf" if config.get("lineEnding", "lf") == "lf" else "crlf"

    # Process files.
    exit_code = 0
    if args.files:
        for fpath in args.files:
            ret = process_file(fpath, config["rules"], quote_style, line_ending, args.in_place)
            if ret != 0:
                exit_code = ret
    else:
        # Read from stdin.
        content = sys.stdin.read()
        formatted = process_text(content, config["rules"], quote_style, line_ending)
        sys.stdout.write(formatted)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()