#!/usr/bin/env python3
"""Summarize CSV files in a directory."""

import argparse
import csv
import os
import re
import sys
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"ghp_[0-9a-zA-Z]{36}"),
    re.compile(r"eyJ[0-9A-Za-z\-_]+\.eyJ[0-9A-Za-z\-_]+"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]

HIGH_ENTROPY_THRESHOLD = 4.5


def shannon_entropy(text: str) -> float:
    """Approximate Shannon entropy for a string."""
    if not text:
        return 0.0
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(text)
    entropy = -sum((count / length) * (count / length).__class__.__log__(count / length) for count in freq.values())
    return entropy


def looks_like_secret(value: str) -> bool:
    """Check if a cell string matches known secret shapes or high entropy."""
    for pattern in SECRET_PATTERNS:
        if pattern.search(value):
            return True
    # Avoid flagging short or whitespace-only strings
    stripped = value.strip()
    if len(stripped) < 20:
        return False
    if shannon_entropy(stripped) > HIGH_ENTROPY_THRESHOLD:
        return True
    return False


def summarize_file(path: Path, output: list) -> None:
    """Compute stats for one file."""
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except (UnicodeDecodeError, csv.Error, OSError) as e:
        output.append(f"{path.name}, ERROR, {e}")
        return

    if not rows:
        output.append(f"{path.name}, 0, 0, 0")
        return

    header = rows[0]
    num_cols = len(header)
    num_rows = len(rows) - 1

    # Header checks
    dup_headers = len(header) != len(set(header))
    # Row consistency
    consistent_rows = 0
    secret_flags = 0
    for row in rows[1:]:
        if len(row) == num_cols:
            consistent_rows += 1
        # Secret detection per cell (limit to first 50 rows for speed)
        if secret_flags < 10 and consistent_rows <= 50:
            for cell in row:
                if looks_like_secret(cell):
                    secret_flags += 1
                    break

    non_null = sum(1 for row in rows[1:] for cell in row if cell.strip())
    total_cells = max(1, num_rows * num_cols)
    ratio = non_null / total_cells

    flags = []
    if dup_headers:
        flags.append("dup_header")
    if secret_flags:
        flags.append(f"possible_secret_x{secret_flags}")
    if num_rows == 0:
        flags.append("empty")

    flag_str = "|".join(flags) if flags else "ok"
    output.append(f"{path.name}, {num_rows}, {num_cols}, {ratio:.2f}, {flag_str}")


def main():
    parser = argparse.ArgumentParser(description="Summarize CSV files.")
    parser.add_argument("path", help="File or directory")
    parser.add_argument("--recursive", action="store_true", help="Recurse into subdirs")
    parser.add_argument("--out", help="Output file")
    args = parser.parse_args()

    target = Path(args.path)
    if target.is_file():
        files = [target]
    elif target.is_dir():
        pattern = "**/*.csv" if args.recursive else "*.csv"
        files = sorted(target.glob(pattern))
    else:
        print(f"Not found: {target}", file=sys.stderr)
        sys.exit(1)

    results = []
    for f in files:
        summarize_file(f, results)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write("filename, rows, cols, non_null_ratio, flags\n")
            f.write("\n".join(results))
    else:
        print("filename, rows, cols, non_null_ratio, flags")
        for line in results:
            print(line)


if __name__ == "__main__":
    main()