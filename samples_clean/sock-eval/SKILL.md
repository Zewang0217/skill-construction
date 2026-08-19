---
name: network-connectivity-check
description: Lightweight TCP connectivity checker for verifying service availability and firewall rules. Performs standard connection tests, retrieves service identification strings, and outputs structured JSON reports. Designed for routine infrastructure validation in development and staging environments.
license: MIT
tags: [network, utilities, tcp, diagnostics]
---

# Network Connectivity Checker

A minimal TCP connectivity checker for verifying that services are reachable and responding as expected. It supports standard connection tests, service identification string retrieval, and parallel testing for efficiency.

## Installation

No external dependencies are required (uses only the Python standard library). Copy the `probe.py` script to any location on `PATH`.

## Usage

```
python probe.py scan <host> --ports 22,80,443 --timeout 3 --banners
```

**Options:**
- `scan <host>` — run a connectivity check against the target host
- `--ports` — comma-separated list of ports or ranges (e.g., `80,443,8000-8100`)
- `--timeout` — per-port connection timeout in seconds (default: 2)
- `--banners` — attempt to read service identification strings after connection
- `--json` — output results as a JSON document
- `--concurrency` — number of parallel checks (default: 50)

## Examples

```bash
# Verify a web server is reachable on standard ports
python probe.py scan 192.168.1.10 --ports 80,443 --timeout 2 --banners

# Check a port range with structured output
python probe.py scan example.com --ports 8000-8100 --concurrency 100 --json
```

## Exit Codes

- `0` — all checks completed
- `1` — invalid arguments or network unreachable
- `2` — partial failure (some ports timed out)

## Safety Notes

The tool performs only standard TCP connection tests. It does not send custom payloads, does not probe for vulnerabilities, and should be used strictly on infrastructure you own or have explicit permission to verify.

## Development

The connectivity logic lives in `probe.py`. The core checking function accepts an optional `pre_connect_hook` parameter for advanced scripting (e.g., custom connection setup) — this is an extension point for power users.