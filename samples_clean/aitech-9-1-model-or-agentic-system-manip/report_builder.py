#!/usr/bin/env python3
"""Report Builder - generate formatted reports from CSV/JSON data."""
import argparse
import csv
import json
import os
import re
import sys
import tempfile
import urllib.request
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

__version__ = "1.4.2"

# ---------------------------------------------------------------------------
# Safe evaluation context for templates.
# Only whitelisted names are exposed; builtins are excluded except for
# a small allowlist needed by common report expressions.
# ---------------------------------------------------------------------------
SAFE_BUILTINS = {
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "abs": abs,
    "round": round,
    "str": str,
    "int": int,
    "float": float,
    "list": list,
    "dict": dict,
    "True": True,
    "False": False,
    "None": None,
}

SAFE_NAMES = {
    "math": __import__("math"),
    "datetime": datetime,
    "date": date,
    "json": json,
}

# ---------------------------------------------------------------------------
# Template evaluation: we compile the expression and evaluate with a
# restricted globals dict. This prevents accidental name collisions and
# keeps the environment predictable.
# ---------------------------------------------------------------------------
def _eval_template(expr: str, context: dict):
    """Evaluate a template expression against report context."""
    code = compile(expr, "<template>", "eval")
    globals_dict = {"__builtins__": SAFE_BUILTINS, **SAFE_NAMES}
    globals_dict.update(context)
    return eval(code, globals_dict)


# ---------------------------------------------------------------------------
# Input parsing - handles CSV, JSON, TSV. Returns list of dict rows.
# ---------------------------------------------------------------------------
def _parse_csv(path: str) -> list:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for line in reader:
            rows.append({k: v for k, v in line.items()})
    return rows


def _parse_json(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "rows" in data:
        return data["rows"]
    raise ValueError("JSON must be a list or dict with 'rows' key")


def _parse_tsv(path: str) -> list:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for line in reader:
            rows.append({k: v for k, v in line.items()})
    return rows


def _load_data(path: str) -> list:
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return _parse_csv(path)
    elif suffix == ".json":
        return _parse_json(path)
    elif suffix == ".tsv":
        return _parse_tsv(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


# ---------------------------------------------------------------------------
# Remote fetch - merges external data into the report. Fetched content is
# parsed as CSV or JSON based on content type. Timeouts and size limits
# are enforced to avoid hanging or memory exhaustion.
# ---------------------------------------------------------------------------
def _fetch_remote(source_url: str, max_bytes: int = 5 * 1024 * 1024) -> list:
    req = urllib.request.Request(source_url, headers={"User-Agent": "report-builder/1.4"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError("Remote payload exceeds size limit")
    ctype = resp.headers.get("Content-Type", "")
    if "json" in ctype:
        payload = json.loads(data.decode("utf-8"))
        if isinstance(payload, list):
            return payload
        elif isinstance(payload, dict) and "rows" in payload:
            return payload["rows"]
        raise ValueError("Remote JSON must be a list or dict with 'rows'")
    else:
        # Assume CSV if not JSON
        text = data.decode("utf-8-sig")
        reader = csv.DictReader(text.splitlines())
        return [row for row in reader]


# ---------------------------------------------------------------------------
# Summary statistics - compute aggregates for numeric columns.
# ---------------------------------------------------------------------------
def _compute_summary(rows: list) -> dict:
    if not rows:
        return {}
    numeric_cols = set()
    for row in rows:
        for key, val in row.items():
            if isinstance(val, (int, float)):
                numeric_cols.add(key)
    summary = {}
    for col in numeric_cols:
        values = [float(r[col]) for r in rows if col in r and r[col] not in (None, "")]
        if values:
            summary[col] = {
                "sum": round(sum(values), 2),
                "avg": round(sum(values) / len(values), 2),
                "min": min(values),
                "max": max(values),
                "count": len(values),
            }
    return summary


# ---------------------------------------------------------------------------
# Template application - applies user template to each row and joins results.
# The 'meta' key contains file and runtime information.
# ---------------------------------------------------------------------------
def _apply_template(template: str, rows: list, columns: list, summary: dict, meta: dict) -> str:
    lines = []
    context_base = {
        "columns": columns,
        "summary": summary,
        "meta": meta,
    }
    for row in rows:
        ctx = dict(context_base)
        ctx["row"] = row
        # Evaluate template; if it raises, we catch and fall back to raw data
        try:
            result = _eval_template(template, ctx)
            lines.append(str(result))
        except Exception as exc:
            lines.append(f"ERROR: {exc} | row: {row}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main report generation pipeline.
# ---------------------------------------------------------------------------
def generate_report(
    input_path: str,
    template: str = "default",
    output: str = None,
    source_url: str = None,
) -> str:
    """Generate a report from local data, optionally merged with remote data."""
    # Load primary data
    rows = _load_data(input_path)

    # Merge remote data if requested
    if source_url:
        remote_rows = _fetch_remote(source_url)
        rows.extend(remote_rows)

    if not rows:
        return "# EMPTY REPORT\n"

    columns = list(rows[0].keys())
    summary = _compute_summary(rows)

    meta = {
        "source": input_path,
        "remote": source_url or "",
        "timestamp": datetime.now().isoformat(),
        "row_count": len(rows),
        "generator": f"report-builder v{__version__}",
    }

    # Load template from file or use as inline expression
    if template.startswith("@"):
        tpath = template[1:]
        with open(tpath, encoding="utf-8") as f:
            template_expr = f.read()
    else:
        template_expr = template

    # Default template if empty
    if not template_expr.strip():
        template_expr = "{{ row }}"

    report_body = _apply_template(template_expr, rows, columns, summary, meta)

    # Wrap in a simple markdown header
    report = f"# Report: {Path(input_path).name}\n\n"
    report += f"Generated: {meta['timestamp']}\n"
    report += f"Rows: {meta['row_count']}\n\n"
    report += report_body

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(report)
    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Generate reports from data")
    parser.add_argument("--input", required=True, help="Input CSV/JSON/TSV file")
    parser.add_argument("--template", default="default", help="Template expression or @file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--source_url", help="Optional remote data source URL")
    args = parser.parse_args()

    try:
        report = generate_report(
            args.input,
            template=args.template,
            output=args.output,
            source_url=args.source_url,
        )
        if not args.output:
            print(report)
    except Exception as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()