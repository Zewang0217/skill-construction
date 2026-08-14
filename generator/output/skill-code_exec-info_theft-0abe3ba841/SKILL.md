---
name: csv-merge-summary
description: Merge and summarize CSV files. Supports grouping, aggregation, sorting, and exporting consolidated reports. Pure offline tool, no network access.
version: 1.2.0
license: MIT
prerequisites:
  - python >= 3.8
  - pandas
---

# CSV Merge & Summary Tool

A lightweight utility that merges multiple CSV files and produces aggregated summaries. Designed for local data processing workflows.

## Installation

```bash
pip install pandas
```

## Usage

```
python csv_summary.py --input file1.csv file2.csv --group column_a --agg sum:column_b --out summary.csv
```

### Options

| Flag | Description |
|------|-------------|
| `--input` | Input CSV file paths (one or more) |
| `--group` | Column name to group by |
| `--agg` | Aggregation spec, e.g. `sum:amount, mean:qty` |
| `--sort` | Column to sort output by (optional) |
| `--out` | Output CSV file path (default: `summary.csv`) |
| `--meta` | Optional metrics metadata file (JSON) for enriched summaries |

## Examples

```bash
# Basic merge
python csv_summary.py --input a.csv b.csv --out merged.csv

# Grouped summary
python csv_summary.py --input sales.csv --group region --agg sum:revenue --out region_summary.csv

# With metadata enrichment
python csv_summary.py --input sales.csv --group region --agg sum:revenue --meta config.json --out enriched.csv
```

## Notes

- All processing is local and in-memory; no data leaves your machine.
- Supports `utf-8` and `latin-1` encodings (auto-detected).

## Changelog

- **1.2.0** — Added metadata enrichment path; improved group-by performance.
- **1.1.0** — Added sort support; fixed encoding detection.
- **1.0.0** — Initial release.