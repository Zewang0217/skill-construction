#!/usr/bin/env python3
"""
text-tidy: a small text normalization utility.

Reads text from stdin or a file, applies whitespace and typographic fixes,
and writes the result. See the skill's SKILL.md for usage.
"""

import argparse
import codecs
import os
import re
import sys


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def _normalize_line_endings(text: str) -> str:
    """Convert CRLF and CR to LF."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _collapse_blank_lines(text: str) -> str:
    """Collapse runs of two or more newlines to a single blank line."""
    return re.sub(r"\n{3,}", "\n\n", text)


def _trim_line_whitespace(text: str) -> str:
    """Strip leading/trailing whitespace per line."""
    return "\n".join(line.strip() for line in text.split("\n"))


def _smart_quotes(text: str) -> str:
    """Replace straight quotes/em-dashes with typographic equivalents."""
    replacements = {
        '"': "\u201c",
        '"': "\u201d",
        "'": "\u2019",
        "--": "\u2014",
    }
    for plain, smart in replacements.items():
        text = text.replace(plain, smart)
    return text


def _leading_spaces_to_tabs(text: str, n: int) -> str:
    """Replace runs of exactly n leading spaces with a tab."""
    if n <= 0:
        return text
    lines = []
    for line in text.split("\n"):
        while line.startswith(" " * n):
            line = "\t" + line[n:]
        lines.append(line)
    return "\n".join(lines)


def normalize_text(text: str, options: dict) -> str:
    """Apply all requested normalizations in a fixed order."""
    text = _normalize_line_endings(text)
    text = _collapse_blank_lines(text)
    text = _trim_line_whitespace(text)

    if options.get("smart", True):
        text = _smart_quotes(text)

    tab_width = options.get("tabs", 0)
    if tab_width:
        text = _leading_spaces_to_tabs(text, tab_width)

    return text


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _read_text(path: str) -> str:
    """Read a file, decoding UTF-8 (with BOM tolerance)."""
    if path == "-":
        return sys.stdin.read()
    with open(path, "rb") as f:
        raw = f.read()
    if raw.startswith(codecs.BOM_UTF8):
        raw = raw[len(codecs.BOM_UTF8):]
    return raw.decode("utf-8")


def _write_text(path: str, text: str) -> None:
    """Write text, encoding as UTF-8. If path is '-', write to stdout."""
    if path == "-":
        sys.stdout.write(text)
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


# ---------------------------------------------------------------------------
# Command-line entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean up text files.")
    parser.add_argument("file", nargs="?", default="-",
                        help="input file (default: stdin)")
    parser.add_argument("-o", "--output", default="-",
                        help="output file (default: stdout)")
    parser.add_argument("--tabs", type=int, default=0, metavar="N",
                        help="convert leading N spaces to tabs")
    parser.add_argument("--no-smart", action="store_true",
                        help="skip smart-quote normalization")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the file would change")
    parser.add_argument("--verbose", action="store_true",
                        help="print per-file stats to stderr")
    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        text = _read_text(args.file)
    except (OSError, UnicodeDecodeError) as err:
        print(f"text-tidy: error reading {args.file}: {err}", file=sys.stderr)
        return 1

    options = {
        "smart": not args.no_smart,
        "tabs": args.tabs,
    }
    cleaned = normalize_text(text, options)

    if args.check:
        if cleaned != text:
            if args.verbose:
                print(f"{args.file}: would change", file=sys.stderr)
            return 1
        return 0

    try:
        _write_text(args.output, cleaned)
    except OSError as err:
        print(f"text-tidy: error writing {args.output}: {err}", file=sys.stderr)
        return 1

    if args.verbose:
        orig_lines = len(text.split("\n"))
        new_lines = len(cleaned.split("\n"))
        print(
            f"{args.file}: {orig_lines} -> {new_lines} lines "
            f"({len(text)} -> {len(cleaned)} bytes)",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())