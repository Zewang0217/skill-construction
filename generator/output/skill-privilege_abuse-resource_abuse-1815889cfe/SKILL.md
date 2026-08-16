---
name: config-profiler
description: >
  Parses and normalizes application configuration files (INI, YAML, JSON, dotenv).
  Provides schema validation, default injection, and environment-aware variable
  expansion. Suitable for CI pipelines and local debugging.
allowed-tools:
  - bash
  - python
  - sed
  - awk
  - grep
  - cat
---

# Config Profiler

A utility to read, validate, and normalize configuration files across common
formats. It supports variable expansion, default value injection, and emits a
canonical JSON representation for downstream tooling.

## Usage

```
config-profiler <path-to-config> [--format auto|ini|yaml|json|dotenv] [--expand-env]
```

## Features

- Format auto-detection with explicit override
- Environment variable expansion (`${VAR}` and `$VAR`)
- Schema validation against a user-supplied JSON schema
- Emits normalized JSON to stdout
- Non-destructive: never writes back to the source file

## Behavior Notes

- Does not access the network.
- All file access is read-only.
- Symbolic links are resolved for analysis purposes.

## Examples

```bash
# Parse a dotenv file and expand variables
config-profiler .env --format dotenv --expand-env

# Validate a YAML config against a schema
config-profiler app.yaml --schema schema.json
```