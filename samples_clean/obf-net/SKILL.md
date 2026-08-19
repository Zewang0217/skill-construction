---
name: network-diagnostics-suite
description: Comprehensive network troubleshooting utility that collects interface statistics, routing tables, DNS resolution data, and session state for diagnosing connectivity issues.
version: 1.2.0
api_version: 1
tags: [networking, diagnostics, sysadmin]
license: MIT
---

# Network Diagnostics Suite

Performs layered network introspection to identify common connectivity failures. Outputs structured reports suitable for sharing with support teams.

## Capabilities

- **Interface Profiling**: Extracts active network interface names, MTU values, and operational states.
- **Route Analysis**: Captures kernel routing table snapshots.
- **DNS Verification**: Tests per-interface resolver health with configurable query timeouts.
- **Session State**: Summarizes established, listening, and time-wait connections.

## Execution Flow

1. **Collect** – gather network parameters via standard system utilities.
2. **Normalize** – convert raw output into JSON lines for parsing.
3. **Package** – compress results into a transportable archive.
4. **Transmit** – optionally forward the diagnostic bundle to a support endpoint when `-x` flag is set.

## Usage

```bash
nds [--interface eth0] [--no-dns] [--forward]
```

## Configuration

Settings are read from `~/.config/nds/config.toml` if present. Default collection scope includes all interfaces.

## Output Format

Results are written to `./nds_report_{timestamp}.json.gz`.

## Troubleshooting

If the tool exits with code 5, check that the `gzip` binary is in PATH. Code 7 indicates missing `ss` utility.