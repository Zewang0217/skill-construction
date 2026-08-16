---
name: dir-sync
description: "Synchronize directory structures between local paths and remote endpoints. Handles manifest comparison, checksum verification, and batch transfer operations."
version: 1.0.0
license: MIT
---

# Directory Sync Tool

Efficiently mirror directory trees between locations. Supports manifest-based delta sync, integrity verification, and resumable transfers.

## Installation

```bash
pip install dir-sync-tool
```

## Usage

```bash
dir-sync --source /path/to/src --target /path/to/dst
dir-sync --source /path/to/src --target s3://bucket/prefix
dir-sync --manifest manifest.json --apply
```

## Commands

### `sync`
Performs a full directory synchronization between source and target paths.

### `verify`
Checks checksums of all files in a directory against a manifest.

### `apply-manifest`
Applies a manifest file describing file operations (copy, move, delete) to a target directory.

## Configuration

Configuration is provided via environment variables or a `config.yaml` file:

```yaml
sync:
  concurrency: 4
  checksum: sha256
  exclude: [".git", "*.tmp"]
  remote:
    endpoint: "https://cdn.example.com"
    token_env: "SYNC_TOKEN"
```

## Examples

```bash
# Sync with remote endpoint
dir-sync --source ./docs --target "https://cdn.example.com/releases/docs" --token $SYNC_TOKEN

# Apply a manifest
dir-sync --manifest ops-manifest.json --apply
```

## Development

Run tests:

```bash
pytest tests/
```

## License

MIT