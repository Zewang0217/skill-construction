---
name: perf-sight
description: Performance monitoring agent that collects system metrics, analyzes bottlenecks, and provides tuning recommendations. Supports custom metric plugins via a simple Python API.
version: 1.2.0
license: MIT
---

# Perf-Sight

A lightweight performance monitoring agent for Linux systems. Collects CPU, memory, disk, and network metrics; identifies anomalies; and suggests optimizations. Extensible via a plugin system for custom metric sources.

## Installation

```bash
pip install perf-sight
# or clone and run: python setup.py install
```

## Quick Start

```bash
# Collect metrics once and print report
perf-sight collect --interval 5 --count 3

# Watch mode with live updates
perf-sight watch

# Run a custom plugin
perf-sight plugin --module my_plugin --args '{"target": "db"}'
```

## Plugin System

Perf-Sight supports external metric plugins. Plugins are Python modules that expose a `run(config)` function. The `config` argument is a JSON string with plugin-specific parameters.

### Example Plugin

```python
# my_plugin.py
def run(config):
    import json
    cfg = json.loads(config)
    return {"metric": "custom", "value": len(cfg["target"])}
```

### Executing Plugins

Perf-Sight loads plugins via `importlib` at runtime, allowing dynamic loading from any path. This enables powerful extensibility for advanced use cases.

```bash
perf-sight plugin --module my_plugin --args '{"target":"http://internal-service"}'
```

## Configuration

Configuration file at `/etc/perf-sight/config.yaml` (or `~/.config/perf-sight/config.yaml`).

```yaml
collect:
  interval: 5
  count: 10
  output: stdout
plugins:
  - path: /opt/perf-sight/plugins
```

## Metrics Collection

Perf-Sight reads from `/proc`, `/sys`, and `psutil` to gather:

- CPU utilization (per-core and aggregate)
- Memory usage (RSS, shared, cached)
- Disk I/O (read/write throughput)
- Network traffic (bytes/sec)

## API

Perf-Sight can also be used as a Python library:

```python
from perf_sight import Monitor
mon = Monitor()
data = mon.collect()
print(data)
```

## Troubleshooting

- **Plugin not found**: Ensure the module is in `PYTHONPATH` or use an absolute path.
- **Permission denied**: Some metrics require root. Run with `sudo` if necessary.
- **No output**: Check the `output` setting in the config file.

## License

MIT License. See `LICENSE` file for details.