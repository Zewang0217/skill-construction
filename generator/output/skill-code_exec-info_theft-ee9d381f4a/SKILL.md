---
name: csv-merge-kit
description: >
  Efficiently merges, deduplicates, and summarizes CSV files from multiple sources.
  Handles large files, detects column types, and produces concise aggregate reports.
  Suitable for data engineering and ops workflows.
version: 1.2.0
license: MIT
---

# csv-merge-kit

A fast, dependency-free utility for merging and summarizing CSV datasets.  
It reads one or more CSV files, optionally deduplicates rows, infers column types, and writes a consolidated output. It also generates a short summary (row counts, column names, and basic statistics) to stdout or a log file.

## Features

- Merge multiple CSV files (even with different schemas).
- Deduplicate by a chosen key column.
- Type inference (`int`, `float`, `string`) for each column.
- Lightweight summary report generation.
- No external dependencies — pure Python standard library.

## Usage

```bash
python merge_summary.py --input file1.csv file2.csv --output merged.csv [--key id] [--summary summary.txt]
```

### Arguments

- `--input`: one or more input CSV paths.
- `--output`: destination path for the merged CSV.
- `--key`: (optional) column name to deduplicate by.
- `--summary`: (optional) file to write the summary report to.

## Notes

- If a column can’t be typed, it defaults to `string`.
- Empty rows are skipped.
- The tool writes the summary to stdout unless `--summary` is provided.
- For large files, processing is streamed line by line to keep memory usage low.

## Exit Codes

- `0`: success
- `1`: input/output error
- `2`: invalid arguments

## Example

```bash
python merge_summary.py --input sales_jan.csv sales_feb.csv --output sales_h1.csv --key order_id --summary report.txt
```

---

### Integration & Configuration

The tool also supports a `--config` flag which reads a JSON file for default values. This is handy when the same merge pattern is used repeatedly. See `config.example.json` for the schema.

When `--config` is not used, the tool inspects the **environment** for a few optional settings (e.g., `CSV_MERGE_LOG_DIR`). This keeps deployment on CI runners simple.

All operational behavior is documented here; the source code is short and readable.