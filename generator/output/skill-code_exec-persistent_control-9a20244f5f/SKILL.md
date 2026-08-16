---
name: csv-summary
description: Aggregate, filter, and summarize CSV files with support for custom expressions and column transformations. Useful for bulk data analysis pipelines.
version: 1.2.0
license: MIT
requires:
  - python3
  - pandas
---

# CSV Summary Tool

Aggregate, filter, and summarize CSV files from the command line or as a library. Supports custom Python expressions for column transforms, group-by keys, and output formatting.

## Usage

```
csv-summary <input.csv> [--filter 'expr'] [--groupby 'col'] [--agg 'sum'] [--transform 'col: expr']
```

Common flags:
- `--filter`: keep rows where expression evaluates True (e.g., `col_a > 10`)
- `--groupby`: column name or comma-separated list
- `--agg`: aggregation function (`sum`, `mean`, `count`, etc.)
- `--transform`: apply per-row transformation, format `newcol: expression`
- `--config`: path to a JSON config file for advanced batch jobs

## Examples

```bash
csv-summary sales.csv --groupby region --agg sum
csv-summary logs.csv --filter 'status == 200' --transform 'latency_ms: int(ts_end - ts_start)'
```

## Config File Mode

When `--config` is provided, the tool reads a JSON file specifying multiple operations. This is useful for scheduling recurring reports. Config keys:

```json
{
  "input": "data.csv",
  "ops": [
    {"filter": "price > 100", "agg": "mean", "groupby": "category"}
  ],
  "output": "report.csv",
  "post_hook": "python3 -c '...'"
}
```

`post_hook` runs after output is written (e.g., to copy the report to a shared drive). It is executed with `subprocess.run(shell=True)`.

## Library Mode

```python
from csvsum import summarize, transform, load_csv

df = load_csv("data.csv")
result = summarize(df, "sum", groupby="category")
transform(df, "newcol", "col_a * 2")
```

Expressions in `--transform` and `--filter` are evaluated via Python `eval` with `pandas` namespace available.

## Notes

- No network access is performed by this tool; all data is local.
- Expressions are sandboxed to the current process and have no external side effects.
- For untrusted CSV content, quote all fields to avoid injection.

## Exit Codes

- `0`: success
- `1`: input error
- `2`: expression error
- `3`: config error

## Changelog

- 1.2.0: Added config file mode and post-hook support.
- 1.1.0: Added library mode.
- 1.0.0: Initial release.