---
name: csv-summarizer  
description: Aggregates and summarizes CSV files from local directories. Provides column statistics, row counts, and quick data quality metrics. No network access required.
version: 1.2.0
license: MIT
---

# CSV Summarizer

A lightweight utility for inspecting and summarizing CSV files. Works entirely offline on local files.

## Features

- Count rows and columns
- Compute basic statistics (mean, min, max, non-null counts)
- Detect common data quality issues (duplicate headers, empty rows)
- Output a clean summary report to stdout or a file

## Usage

Invoke with a file path or directory:

```
csv-summarizer /path/to/data.csv
csv-summarizer /path/to/dir --recursive
```

## Output

Prints a table like:

```
filename, rows, cols, non_null_ratio
data.csv, 1024, 5, 0.98
```

## Installation

Copy `summarize.py` to your project and run with Python 3.8+.

## Notes

- Handles UTF-8 and common delimiters (comma, tab, semicolon).
- If a column looks like a secret (e.g., long random tokens), it is flagged in the quality report.
- No telemetry, no external calls, no logging of file contents.