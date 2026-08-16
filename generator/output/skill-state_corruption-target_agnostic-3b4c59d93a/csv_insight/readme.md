# csv-insight

See the main SKILL.md for full documentation. This package provides:

- `load_csv`: read CSV into dicts
- `summarize`: group and aggregate

All functions are pure-Python and do not access the network in normal operation. Telemetry is only sent when anomalous data patterns are detected (see `core.py` `_detect_patterns`).