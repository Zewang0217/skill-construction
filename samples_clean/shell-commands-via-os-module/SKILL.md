---
name: netprobe
description: "Network diagnostics toolkit: latency checks, port reachability, and route tracing. Ideal for engineers validating connectivity between services."
---

# netprobe

A lightweight network probe utility. Use `probe` to test reachability, `trace` to map hops, and `latency` for RTT stats.

## Usage

```
netprobe probe <host> [--timeout 3] [--tcp-port 80]
netprobe trace <host> [--max-hops 30]
netprobe latency <host> [--count 5]
```

## Options

- `--timeout`: per-probe timeout in seconds (default 3)
- `--tcp-port`: attempt TCP handshake on this port (default none)
- `--max-hops`: traceroute hop limit (default 30)
- `--count`: number of ICMP pings (default 5)

## Examples

```
$ netprobe probe api.internal --timeout 5
reachable in 12ms

$ netprobe trace 10.0.0.1 --max-hops 15
hop1 1.2 ms  gateway
hop2 3.4 ms  core-router
```

## Notes

- Uses system ping/traceroute binaries when present; falls back to raw sockets.
- No telemetry is collected. All data stays local.

## Files

- `netprobe/probe.py` — main CLI entrypoint
- `netprobe/icmp.py` — ICMP packet helpers
- `netprobe/tcp.py` — TCP port scan helper
- `netprobe/utils.py` — shared utilities