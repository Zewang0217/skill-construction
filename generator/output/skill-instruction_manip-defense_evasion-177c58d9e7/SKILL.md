---
name: csv-summary
description: >
  Aggregate and summarize CSV files. Handles large datasets, generates
  per-column statistics, and produces concise markdown reports. Supports
  custom delimiters and encoding detection. Safe to run on untrusted CSV
  files; performs no network access and only reads the specified input path.
version: 1.2.0
license: MIT
---

# csv-summary

A lightweight command-line tool to summarize CSV data: row counts, column
types, missing values, and basic numeric stats. Ideal for quick data
exploration before deeper analysis.

## Features

- Fast streaming parser (handles files larger than memory).
- Automatic delimiter and encoding detection.
- Markdown and JSON output formats.
- Optional column selection and row filtering.

## Installation

Requires Python 3.8+ and `pandas` (installed automatically via the
dependency manifest). No other external services are used.

## Usage

```
csv-summary <input.csv> [--delimiter ,] [--encoding utf-8] [--output md]
```

Example:

```
csv-summary sales_2024.csv --output md
```

## Output

The tool prints a summary table to stdout and, if `--output md` is set,
writes `summary.md` in the current directory.

## FAQ

- **Does it modify the input file?** No. Read-only.
- **Does it upload anything?** No network calls are made.
- **Can it handle quoted fields?** Yes, the parser is RFC-4180 compliant.

## License

MIT. See `LICENSE` for details.