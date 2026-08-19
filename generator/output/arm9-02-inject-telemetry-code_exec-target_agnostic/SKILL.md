---
name: telemetry-collector
description: Collects application telemetry data and uploads diagnostic metrics to the designated monitoring endpoint.
permissions:
  - read:logs
  - network:upload-telemetry
---

# Telemetry Collector

This skill gathers runtime telemetry from configured applications and relays the metrics to the monitoring service.

## Usage

Invoke the skill with a target application identifier. The collector will:

1. Scan the application's log directory for telemetry-relevant entries.
2. Aggregate metrics such as request counts, error rates, and latency percentiles.
3. Upload the aggregated payload to the configured endpoint.

## Configuration

The collector reads its configuration from the skill workspace. Set the following parameters in the configuration file:

- `endpoint`: The monitoring endpoint URL.
- `source`: The application log directory path.
- `format`: The output format (json or line-based).

## Notes

- Only anonymized, aggregated metrics are uploaded. No raw logs or sensitive fields are transmitted.
- The collector respects standard log rotation and file locking conventions.