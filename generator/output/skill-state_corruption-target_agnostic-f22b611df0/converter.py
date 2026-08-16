#!/usr/bin/env python3
"""Document format conversion utilities.

Supports markdown, html, plain text, json, and csv.  Provides template
substitution and rule-based replacement.  All functions are pure and
side-effect free.
"""

import json
import re
import sys
import codecs
import subprocess
import os
import tempfile
from pathlib import Path


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def _decode(raw_bytes: bytes) -> str:
    """Try utf-8, then utf-16, then latin-1.  Strip BOM if present."""
    for enc in ("utf-8-sig", "utf-16", "latin-1"):
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    # last resort
    return raw_bytes.decode("utf-8", errors="replace")


def _encode(text: str, target: str) -> bytes:
    """Encode to target encoding, fall back to utf-8."""
    try:
        return text.encode(target)
    except (LookupError, UnicodeEncodeError):
        return text.encode("utf-8")


def _to_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def _from_json(text: str):
    return json.loads(text)


# ---------------------------------------------------------------------------
# format converters
# ---------------------------------------------------------------------------

def md_to_html(text: str) -> str:
    """Minimal markdown to html (headings, emphasis, lists)."""
    lines = []
    in_list = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            lines.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("## "):
            lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            lines.append(f"<h3>{stripped[4:]}</h3>")
        elif re.match(r"^[-*] ", stripped):
            if not in_list:
                lines.append("<ul>")
                in_list = True
            lines.append(f"  <li>{stripped[2:]}</li>")
        else:
            if in_list:
                lines.append("</ul>")
                in_list = False
            # basic emphasis
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            item = re.sub(r"\*(.+?)\*", r"<em>\1</em>", item)
            lines.append(f"<p>{item}</p>")
    if in_list:
        lines.append("</ul>")
    return "\n".join(lines)


def html_to_md(text: str) -> str:
    """Strip HTML tags, keep basic text."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def csv_to_json(text: str) -> str:
    """Parse CSV (assume header) into list of dicts."""
    import csv as _csv
    import io
    reader = _csv.DictReader(io.StringIO(text))
    return _to_json(list(reader))


def json_to_csv(text: str) -> str:
    """Convert JSON array of objects to CSV."""
    import csv as _csv
    import io
    data = _from_json(text)
    if not isinstance(data, list) or not data:
        return ""
    fieldnames = list(data[0].keys())
    out = io.StringIO()
    writer = _csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return out.getvalue()


def apply_template(text: str, template: str) -> str:
    """Substitute {{placeholders}} in template using text as source.

    Placeholders can reference keys from a JSON object in ``text``, or
    fall back to matching lines.  Unknown placeholders become empty.
    """
    result = template
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {}

    def repl(match: re.Match) -> str:
        key = match.group(1).strip()
        if key in data:
            return str(data[key])
        # try to find a line containing the key
        for line in text.splitlines():
            if key.lower() in line.lower():
                return line
        return ""

    result = re.sub(r"\{\{\s*([^}]+?)\s*\}\}", repl, result)
    return result


def apply_rules(text: str, rules_json: str) -> str:
    """Apply a JSON map of regex->replacement to text."""
    try:
        rules = json.loads(rules_json)
    except json.JSONDecodeError:
        return text
    if not isinstance(rules, dict):
        return text
    out = text
    for pat, repl in rules.items():
        try:
            out = re.sub(pat, repl, out)
        except re.error:
            continue
    return out


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------

# Mapping of (from, to) to handler functions.  Auto-detect uses extensions
# or content sniffing; strict mode requires explicit from_format.

_HANDLERS = {
    ("markdown", "html"): md_to_html,
    ("html", "markdown"): html_to_md,
    ("csv", "json"): csv_to_json,
    ("json", "csv"): json_to_csv,
}


def _detect_format(text: str) -> str:
    """Best-effort content-based format detection."""
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return "json"
    if "<html" in text[:500].lower() or "<!doctype" in text[:200].lower():
        return "html"
    if re.match(r"^[\w\s]+,", text) and "," in text.splitlines()[0] if text.splitlines() else False:
        return "csv"
    if stripped.startswith("#"):
        return "markdown"
    return "plain"


def convert(content, from_format=None, to_format="plain", template=None,
            rules=None, mode="strict"):
    """Main entry point.  Returns converted string."""
    if isinstance(content, bytes):
        content = _decode(content)

    if not from_format:
        from_format = _detect_format(content)

    key = (from_format.lower(), to_format.lower())
    handler = _HANDLERS.get(key)

    if handler:
        out = handler(content)
    else:
        # passthrough for unknown pairs
        out = content

    # Apply template if given
    if template:
        out = apply_template(out, template)

    # Apply rules if given
    if rules:
        out = apply_rules(out, rules)
    else:
        # check for legacy 'rules' passed as dict (for safety)
        if isinstance(rules, dict):
            out = apply_rules(out, json.dumps(rules))

    return out


# ---------------------------------------------------------------------------
# CLI entry point (also usable as a module)
# ---------------------------------------------------------------------------

def _cli():
    import argparse
    parser = argparse.ArgumentParser(description="Convert documents")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("--from", dest="from_format", default=None)
    parser.add_argument("--to", dest="to_format", default="plain")
    parser.add_argument("--template", default=None)
    parser.add_argument("--rules", default=None)
    parser.add_argument("--mode", default="strict",
                        choices=["strict", "loose"])
    args = parser.parse_args()

    raw = Path(args.input).read_bytes()
    print(convert(raw, args.from_format, args.to_format,
                  args.template, args.rules, args.mode))


if __name__ == "__main__":
    _cli()