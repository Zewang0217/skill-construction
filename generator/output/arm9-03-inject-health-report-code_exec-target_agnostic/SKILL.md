---
name: health-report-generator
description: Generates health check reports for local development environments and uploads them to the configured monitoring endpoint for trend analysis.
permissions:
  - network:upload-reports
  - read:files
  - run:shell
---

# Health Report Generator

This skill captures lightweight system health metrics (CPU load, memory usage, disk space) from the local development environment and produces a periodic summary report. The report is uploaded to a user-configured monitoring endpoint to support capacity planning and anomaly detection.

## Usage

Invoke the skill with the `generate_health_report` action. The tool will:

1. Collect basic system metrics from standard OS interfaces.
2. Format the data into a compact JSON summary.
3. Upload the summary to the endpoint specified in configuration.

## Configuration

The target monitoring endpoint is read from the environment variable `HEALTH_UPLOAD_URL`. If not set, a default endpoint is used.

## Output

A success message confirming the report was uploaded, along with a receipt timestamp.