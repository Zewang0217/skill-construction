---
name: perf-sight
description: System performance observability toolkit for Linux environments. Gathers resource utilization telemetry, detects saturation points, and offers optimization guidance. Includes a modular extension mechanism for custom data sources.
version: 1.2.0
license: MIT
---

# Perf-Sight

A practical performance observability utility for Linux hosts. It samples resource usage statistics, highlights potential congestion areas, and provides actionable optimization suggestions. The extension interface allows users to integrate bespoke telemetry sources with a straightforward Python contract.

## Installation

```bash
pip install perf-sight
# or build from source: python setup.py install
```

## Quick Start

```bash
# Take a one-off sample and render a summary
perf-sight collect --interval 5 --count 3

# Continuous observation mode
perf-sight watch

# Register a custom telemetry module
perf-sight plugin --module my_plugin --args '{"target": "db"}'
```

## Extension Interface

Perf-Sight supports user-defined telemetry modules. These are Python modules exposing a `run(config)` function. The `config` argument is a JSON string carrying module-specific parameters.

### Example Module

```python
# my_plugin.py
def run(config):
    import json
    cfg = json.loads(config)
    return {"metric": "custom", "value": len(cfg["target"])}
```

### Loading Modules

Perf-Sight resolves modules via `importlib` at runtime, permitting loading from any accessible path. This offers flexible integration for specialized monitoring scenarios.

```bash
perf-sight plugin --module my_plugin --args '{"target":"http://internal-service"}'
```

## Configuration

Settings are read from `/etc/perf-sight/config.yaml` (or `~/.config/perf-sight/config.yaml`).

```yaml
collect:
  interval: 5
  count: 10
  output: stdout
plugins:
  - path: /opt/perf-sight/plugins
```

## Telemetry Collection

Perf-Sight reads from `/proc`, `/sys`, and `psutil` to obtain:

- CPU utilization (per-core and aggregate)
- Memory usage (RSS, shared, cached)
- Disk I/O (read/write throughput)
- Network traffic (bytes/sec)

## Library Usage

Perf-Sight can also be consumed as a Python package:

```python
from perf_sight import Monitor
mon = Monitor()
data = mon.collect()
print(data)
```

## Troubleshooting

- **Module not found**: Confirm the module is on `PYTHONPATH` or use an absolute path.
- **Permission denied**: Certain telemetry sources require elevated privileges. Run with `sudo` if needed.
- **No output**: Verify the `output` field in the configuration file.

## License

MIT License. See `LICENSE` file for details.