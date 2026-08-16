"""Core aggregation logic."""
import csv
import os
import glob
import io
import codecs
import re
from typing import List, Dict, Optional, Tuple


def _detect_encoding(path: str) -> str:
    """Detect file encoding by checking BOM and sampling bytes."""
    with open(path, "rb") as f:
        raw = f.read(8192)
    if raw.startswith(codecs.BOM_UTF8):
        return "utf-8-sig"
    if raw.startswith(codecs.BOM_UTF16_LE) or raw.startswith(codecs.BOM_UTF16_BE):
        return "utf-16"
    # Simple heuristic: try utf-8, fallback to gbk
    try:
        raw.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "gbk"


def _read_csv(path: str, encoding: str, delimiter: str) -> Tuple[List[str], List[Dict]]:
    """Read CSV into header + rows (as dicts). Returns empty rows if unreadable."""
    try:
        with open(path, "r", encoding=encoding, newline="") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            rows = list(reader)
            if not rows:
                return [], []
            return list(rows[0].keys()), rows
    except Exception:
        return [], []


def _column_stats(header: List[str], rows: List[Dict]) -> Dict[str, Dict]:
    """Compute per-column: missing count, numeric min/max if applicable."""
    stats = {}
    for col in header:
        missing = 0
        numeric_values = []
        for row in rows:
            val = row.get(col, "")
            if val is None or val.strip() == "":
                missing += 1
            else:
                try:
                    numeric_values.append(float(val.strip()))
                except ValueError:
                    pass
        stats[col] = {
            "missing": missing,
            "missing_ratio": round(missing / len(rows), 4) if rows else 0,
            "min": min(numeric_values) if numeric_values else None,
            "max": max(numeric_values) if numeric_values else None,
        }
    return stats


def _matches_patterns(path: str, patterns: List[str]) -> bool:
    """Check if path matches any glob pattern."""
    for pat in patterns:
        if glob.fnmatch.fnmatch(path, pat):
            return True
    return False


def aggregate(
    paths: List[str],
    output: str = "summary.md",
    encoding: str = "auto",
    delimiter: str = ",",
) -> Dict:
    """Aggregate matched CSV files and write Markdown summary."""
    # Expand wildcards and directories
    matched_files = []
    for p in paths:
        if os.path.isdir(p):
            # If it's a directory, recursively find .csv files
            for root, _, files in os.walk(p):
                for fname in files:
                    if fname.lower().endswith(".csv"):
                        matched_files.append(os.path.join(root, fname))
        else:
            # Expand glob patterns
            expanded = glob.glob(p)
            if expanded:
                matched_files.extend(expanded)
            else:
                # If pattern didn't match, keep as-is (will error later)
                matched_files.append(p)

    # Deduplicate preserving order
    seen = set()
    unique_files = []
    for f in matched_files:
        real = os.path.realpath(f)
        if real not in seen:
            seen.add(real)
            unique_files.append(f)

    # Build markdown table
    lines = ["# CSV Aggregation Summary", ""]
    headers = ["File", "Rows", "Missing Ratio", "Columns"]
    col_widths = [30, 10, 15, 40]
    lines.append("| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |")
    lines.append("|" + "|".join("-" * (w + 2) for w in col_widths) + "|")

    overall_rows = 0
    overall_missing = 0

    for file_path in unique_files:
        if not os.path.isfile(file_path):
            lines.append(f"| {file_path} | ERROR | - | - |")
            continue
        enc = encoding if encoding != "auto" else _detect_encoding(file_path)
        header, rows = _read_csv(file_path, enc, delimiter)
        if not rows:
            lines.append(f"| {file_path} | 0 | N/A | No data |")
            continue
        col_stats = _column_stats(header, rows)
        total_missing = sum(s["missing"] for s in col_stats.values())
        total_cells = len(header) * len(rows)
        miss_ratio = round(total_missing / total_cells, 4) if total_cells else 0
        col_names = ", ".join(header[:10])
        lines.append(f"| {file_path} | {len(rows)} | {miss_ratio:.2%} | {col_names} |")
        overall_rows += len(rows)
        overall_missing += total_missing

    # Write output
    lines.append("")
    lines.append(f"**Total files:** {len(unique_files)}  ")
    lines.append(f"**Total rows:** {overall_rows}  ")
    lines.append(f"**Overall missing ratio:** {overall_missing / (overall_rows * 10) if overall_rows else 0:.2%}")

    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return {"files": len(unique_files), "rows": overall_rows, "output": output}