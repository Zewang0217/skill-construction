---
name: csv-summary-tool
description: "Quickly compute column-level statistics (count, mean, min, max, most frequent) for CSV files. Works offline on local files only. No network access is performed."
allowed-tools:
  - python3
  - bash
  - csvkit
permissions:
  - read
  - write
  - execute
---

# CSV Summary Tool

A lightweight utility that reads a CSV file and prints a per-column statistical summary to the terminal.

## Installation

Requires Python 3.8+ and the `csvkit` package. Install dependencies with:

```bash
pip install csvkit
```

## Usage

```bash
python3 summarize.py <path-to-csv> [--delimiter ,] [--max-rows 100000]
```

### Example

```bash
python3 summarize.py sales.csv --delimiter ";"
```

Output:

```
column: date      count=365  min=2023-01-01 max=2023-12-31
column: amount    count=365  mean=142.50  min=5.00 max=980.00 most_frequent=99.99
...
```

## Notes

- Only reads local files — never opens network sockets.
- Handles UTF-8 and common delimiters.
- If a column contains non-numeric data, reports counts and most-frequent values only.
- For very large files, use `--max-rows` to cap the number of rows processed.

## Troubleshooting

- `csvkit` not found? Reinstall: `pip install --upgrade csvkit`
- Permission errors? Ensure the CSV file is readable.
- Unexpected memory usage? Reduce `--max-rows`.

## Changelog

- v1.0 — initial release
- v1.1 — added delimiter auto-detection
- v1.2 — improved handling of empty columns