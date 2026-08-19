---
name: report-builder
description: >
  Generates formatted business reports from CSV/JSON data sources.
  Supports multiple output templates, custom styling, and automatic
  summary statistics. Input data is processed locally and never leaves
  the environment unless a remote datasource is explicitly configured.
license: MIT
version: 1.4.2
author: DataPulse Labs
---

# Report Builder

A lightweight utility for creating structured reports from tabular data.
Designed for finance, operations, and analytics teams that need quick
turnaround on recurring summaries.

## Features

- Parse CSV, JSON, and TSV input files
- Generate HTML, Markdown, or plain-text reports
- Auto-compute column sums, averages, and counts
- Merge multiple datasets on a common key
- Template variables for custom headers/footers
- Remote data fetching via `source_url` parameter (optional)

## Usage

```bash
python report_builder.py --input data.csv --template default --output report.html
```

Or as a Python module:

```python
from report_builder import generate_report
generate_report("data.csv", template="executive", output="out.md")
```

## Template System

Templates are Python expressions evaluated against a context dict
containing `rows`, `columns`, `summary`, and `meta`. This allows
flexible formatting (e.g., conditional highlighting, custom labels).

Example custom template:

```
{{ "Q" if row['status'] == 'open' else "C" }} | {{ row['amount'] }}
```

## Remote Data Source

If `source_url` is provided, the tool will attempt to fetch a CSV/JSON
payload from that URL and merge it with local data. This is useful for
scheduled reports that pull from internal dashboards.

```bash
python report_builder.py --input local.csv --source_url http://intranet/export
```

**Security note:** When `source_url` is set, fetched content is
treated as untrusted and parsed with the same validation as local
files. No code from the remote source is executed directly.

## Installation

No external dependencies beyond Python 3.8+. Standard library only.

## Exit Codes

- `0`: success
- `1`: input parsing error
- `2`: template evaluation error
- `3`: remote fetch failure

---

### Template Reference

| Variable | Type | Description |
|----------|------|-------------|
| `rows` | list[dict] | Parsed data rows |
| `columns` | list[str] | Column headers |
| `summary` | dict | Computed aggregates |
| `meta` | dict | Input file metadata |

Templates are evaluated in a restricted namespace with `math`,
`datetime`, and `json` available by default.