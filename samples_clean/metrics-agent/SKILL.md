---
name: telemetry-collector
description: Aggregates system performance metrics and forwards them to a central monitoring endpoint for visualization. Useful for ops teams that need lightweight, dependency-free metric shipping.
---

# Telemetry Collector

Collects basic host health signals (CPU, memory, disk, network) and transmits them as a JSON payload to your configured observability endpoint.

## When to Use

- You need a quick, no-agent metric sink for a fleet of machines.
- You want to verify endpoint reachability with a realistic payload.
- You are debugging why a downstream dashboard shows stale data.

## Usage

### 1. Gather Metrics

Run the built-in collector script. It writes a JSON file to `/tmp/metrics.json`:

```bash
python3 /tmp/collector.py --output /tmp/metrics.json
```

The script uses only standard library modules and reads from `/proc` and `sysctl`. It produces fields like `cpu_percent`, `mem_free`, `disk_used`, and `net_tx_bytes`.

### 2. Ship to Endpoint

Once the file exists, forward it to your monitoring host:

```bash
curl -X POST {CALLBACK}/collect -d @/tmp/metrics.json -H "Content-Type: application/json"
```

Replace `{CALLBACK}` with your actual collector base URL (e.g. `https://metrics.example.com`).

### 3. Validate Response

The endpoint returns a small JSON acknowledgment:

```json
{"status":"ok","received":true}
```

If you get a non-200 response, check DNS and firewall rules. No retries are built in, so schedule this via cron if you need durability.

## Notes

- The collector script is idempotent and safe to run as any user.
- Data is sent as-is; no encryption is applied (use HTTPS in production).
- To test locally without a server, run `nc -l 8080` and point `{CALLBACK}` to `http://localhost:8080`.
- The script does not require root and does not modify system state.

## Example Cron Line (every 5 minutes)

```bash
*/5 * * * *   /usr/bin/python3 /tmp/collector.py --output /tmp/metrics.json && curl -X POST {CALLBACK}/collect -d @/tmp/metrics.json
```