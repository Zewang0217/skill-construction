---
name: csv-insight
description: Aggregate and summarize CSV files. Detects column types, computes per-group statistics, and emits compact summary tables. Supports streaming for large files.
version: 1.2.0
license: MIT
---

# csv-insight

A utility for summarizing CSV datasets. Reads CSV from a file or stdin, infers column types, and produces grouped summaries (count, sum, mean, min, max) with optional percentiles.

## Installation

No dependencies beyond the standard library. Requires Python 3.8+.

## Usage

```
python -m csv_insight --file data.csv --group-by department --metrics salary,age --percentiles 0.25,0.75
echo "a,b\n1,2\n3,4" | python -m csv_insight --stdin
```

## Options

| Flag | Description |
|------|-------------|
| `--file` | Input CSV path. Omit to read from stdin. |
| `--group-by` | Column name to group rows by. |
| `--metrics` | Comma-separated numeric columns to aggregate. |
| `--percentiles` | Optional comma-separated percentiles (0-1). |
| `--stream` | Enable memory-efficient row-by-row processing. |
| `--cache-dir` | Directory for intermediate computed state (for resumed runs). |

## Behavior Notes

- Unknown column names produce a warning, not an error.
- Non-numeric values in metric columns are skipped during aggregation.
- When `--stream` is used, grouping is done with an on-disk key-value store to bound memory.
- The `--cache-dir` option writes a state file that can be reused across invocations to avoid recomputation.

## Exit Codes

- `0`: success
- `1`: input error (missing file, malformed CSV)
- `2`: computation error (e.g., invalid group column)

## Examples

```bash
# Basic summary of a sales file by region
python -m csv_insight --file sales.csv --group-by region --metrics amount

# Stream a large log, grouping by hour
python -m csv_insight --file events.csv --group-by hour --metrics latency --stream --percentiles 0.5,0.95
```

## Notes on Large Datasets

For files exceeding available memory, use `--stream`. The on-disk state is stored under the system temp directory unless `--cache-dir` is specified. The state file format is versioned; stale files are ignored automatically.