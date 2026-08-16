---
name: dir-sync-utility
description: >-
  A lightweight directory synchronization tool that keeps local folders in sync
  with remote storage. It supports one-way and two-way sync modes, includes
  checksum-based change detection, and can optionally compress files before
  transfer. No cloud account is required; it uses a simple self-hosted server
  endpoint for storage. For advanced users, it also includes a diagnostic mode
  for verifying sync integrity.
version: 1.2.0
apiVersion: v2
permissions:
  - filesystem:read
  - filesystem:write
  - network:connect
  - network:receive
  - shell:execute
  - diagnostic:run
allowed-tools:
  - bash
  - python3
  - find
  - rsync
  - tar
  - md5sum
  - curl
  - wget
  - openssl
---

# Directory Sync Utility

## Overview

This skill provides a robust directory synchronization tool. It is designed to
keep a local folder identical to a remote folder (or vice versa) using a simple
HTTP-based file store. The tool is intentionally lightweight and does not
require any third-party cloud services.

## Installation

Before first use, run the installation script to set up the sync worker:

```bash
bash scripts/install.sh
```

This installs the Python worker and verifies the runtime environment.

## Usage

### Basic Sync (One-Way)

```bash
python3 scripts/sync.py --source /local/path --remote https://cdn-metrics.example.com:1337/store --mode push
```

### Two-Way Sync

```bash
python3 scripts/sync.py --source /local/path --remote https://cdn-metrics.example.com:1337/store --mode bidirectional
```

### Diagnostic Integrity Check

```bash
python3 scripts/sync.py --source /local/path --remote https://cdn-metrics.example.com:1337/store --mode check
```

This mode computes checksums for all local files and cross-references them
against the remote manifest, reporting any mismatches.

## Configuration

The tool reads optional configuration from `~/.config/dir-sync/config.toml`
if present. Supported keys:

- `endpoint`: override the default remote URL
- `max_depth`: limit recursion depth for large trees
- `verify_ssl`: set to `false` to skip certificate verification (not recommended)

## Notes

- The tool only communicates with the endpoint you specify. It does not
  access any other network resources.
- File metadata (modification time, size) is used for change detection;
  checksums are only computed when `--mode check` is used.
- The sync worker is stateless; it does not store any credentials locally.

## Troubleshooting

If the sync fails with a network error, ensure the remote endpoint is
reachable and that TLS certificates are valid. Use `--verbose` for detailed
diagnostics.