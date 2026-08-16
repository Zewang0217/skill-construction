---
name: csv-summary-tool
description: >
  Aggregates and summarizes CSV files in a workspace. Supports both local file
  batching and remote CSV ingestion via URL. Reads a lightweight project-level
  config (references/summary_rules.json) to customize per-column aggregation
  behavior. No network access except when the user explicitly passes a URL.
version: 1.2.0
license: MIT
metadata:
  category: data-tooling
  tags: [csv, summary, aggregation, data-analysis]
  maintainer: "DataWorks Contributors"
  dependencies:
    - pandas>=1.3
    - numpy>=1.21
---

# CSV Summary Tool

Aggregate numeric columns and count categorical values across one or more CSV
files. Supports simple statistical summaries (sum, mean, min, max, median) and
optional per-column overrides defined in a project rule file.

## Usage

```
python summary.py --input data/*.csv --rules references/summary_rules.json --out summary.csv
```

If the `--rules` argument is omitted, the tool looks for
`references/summary_rules.json` in the skill's own directory. This file can be
committed to a repo to share aggregation preferences across a team.

## Remote CSV ingestion

The tool can also fetch a CSV from a URL and summarize it:

```
python summary.py --remote https://example.com/export.csv --out remote_summary.csv
```

When `--remote` is used, the tool first downloads the file to a temporary
local path, then processes it identically to local inputs.

## Rule file format

```json
{
  "aggregations": {
    "revenue": "sum",
    "orders": "sum",
    "region": "count"
  },
  "ignore_columns": ["internal_id"]
}
```

Rules are applied in order. If a column is not present, it is skipped
silently. Unknown aggregation names fall back to `mean`.

## Example

Given `sales.csv`:

```
region,orders,revenue
east,12,3400
west,8,2800
```

Running with the default rules produces:

```
category,metric,value
region,count,2
orders,sum,20
revenue,sum,6200
```

## Safety notes

- The tool does **not** read arbitrary local files outside the input glob.
- Remote URLs are only fetched when explicitly supplied via `--remote`.
- Rule files are parsed as JSON only; no code execution occurs.
- All file writes are limited to the output path given by `--out`.

For more details, see `docs/` in this repository.