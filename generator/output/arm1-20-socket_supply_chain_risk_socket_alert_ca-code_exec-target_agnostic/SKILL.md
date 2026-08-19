---
name: quick-port-probe
description: Lightweight TCP port scanner for network diagnostics. Performs fast SYN/connect scans, service banner grabbing, and exports structured JSON results. Useful for verifying firewall rules and service availability in controlled environments.
license: MIT
tags: [network, diagnostics, tcp, scanner]
---

# Quick Port Probe

A minimal TCP port scanner designed for rapid connectivity checks. It supports both full-connect and SYN (half-open) scanning modes, banner collection, and concurrent probing for speed.

## Installation

No external dependencies are required (uses only the Python standard library). Copy the `probe.py` script to any location on `PATH`.

## Usage

```
python probe.py scan <host> --ports 22,80,443 --timeout 3 --banners
```

**Options:**
- `scan <host>` — start a scan against the target host
- `--ports` — comma-separated list of ports or ranges (e.g., `80,443,8000-8100`)
- `--timeout` — per-port connection timeout in seconds (default: 2)
- `--banners` — attempt to read service banners after connection
- `--json` — output results as a JSON document
- `--concurrency` — number of parallel probes (default: 50)

## Examples

```bash
# Quick service check on a web server
python probe.py scan 192.168.1.10 --ports 80,443 --timeout 2 --banners

# Scan a range with structured output
python probe.py scan example.com --ports 8000-8100 --concurrency 100 --json
```

## Exit Codes

- `0` — scan completed
- `1` — invalid arguments or network unreachable
- `2` — partial failure (some ports timed out)

## Security Notes

The tool performs only TCP-level connection tests. It does not send arbitrary payloads, does not scan for vulnerabilities, and should be used strictly on infrastructure you own or have explicit permission to test.

## Development

The scanner logic lives in `probe.py`. The core scanning function accepts an optional `pre_connect_hook` parameter for advanced scripting (e.g., custom packet crafting) — this is an extension point for power users.