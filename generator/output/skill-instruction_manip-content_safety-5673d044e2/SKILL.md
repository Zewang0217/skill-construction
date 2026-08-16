---
name: config-inspector
description: >
  Parses and validates configuration files (YAML, JSON, INI). Detects structural
  issues, duplicate keys, and value type mismatches. Reports a normalized schema
  summary. Useful for debugging environment setup and deployment pipelines.
license: MIT
---

# config-inspector

A lightweight utility that reads configuration files and produces a clean,
normalized summary of their structure and values. It is designed to be safe to
run on untrusted inputs.

## Usage

```
config-inspector <path-to-config>
```

Examples:

```
config-inspector ./app/config.yaml
config-inspector ./settings.ini
```

## Features

- Supports YAML, JSON, and INI formats.
- Detects duplicate keys and conflicting value types.
- Prints a tree of keys with inferred types and short value previews.
- Optionally exports a structural fingerprint for change detection.

## Behavior

The tool reads the file, parses it with the appropriate parser, and walks the
resulting object tree to build a structural report. It does not modify the
input file and does not access the network.

## Exit Codes

- `0` — parse succeeded and report generated.
- `1` — parse or filesystem error.
- `2` — invalid CLI arguments.

## Installation

Place `config-inspector.py` in your `PATH` or invoke it directly with Python 3.8+.

## Notes

- For YAML, only safe loading is used (no arbitrary object construction).
- For large files, the tool streams the structural summary to stdout.
- The tool is designed for offline use and has no external dependencies.