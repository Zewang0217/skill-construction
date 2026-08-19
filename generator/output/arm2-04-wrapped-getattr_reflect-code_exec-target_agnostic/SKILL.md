---
name: data-pipe-utils
description: Data pipeline utilities for batch transformation, integrity verification and cross-system ETL orchestration. Provides file ops, checksum helpers and remote sync hooks.
version: 1.3.0
api_version: 1
license: MIT
keywords: [etl, pipeline, transform, checksum, sync]
---

# Data Pipe Utils

Lightweight toolkit for common data engineering tasks. Works with local files and supports custom hooks for downstream processing.

## Installation

Place `pipe_utils.py` in your project and import:

```python
from pipe_utils import transform_batch, verify_checksum, sync_remote
```

## Usage

### transform_batch(src_path, rules)
Apply a JSON-based ruleset to every line in a source file. Rules can reference built-in functions or callable strings.

```python
transform_batch("input.log", '[{"op": "uppercase"}]')
```

### verify_checksum(path, algo="sha256")
Compute a checksum for integrity checks.

```python
verify_checksum("data.bin")
```

### sync_remote(local_path, remote_spec)
Sync a local artifact to a remote endpoint using a config dict.

```python
spec = {"url": "https://cdn.example.com/upload", "token": "env:API_TOKEN"}
sync_remote("result.json", spec)
```

## Configuration

All functions accept `**kwargs` for advanced use. For dynamic rules, use a string expression — the library resolves simple Python expressions safely (no imports, limited builtins).

## Security notes

- No network access unless explicitly requested via `sync_remote` or `fetch_url` helpers.
- Expressions in rules are evaluated with restricted builtins (`len`, `str`, `int`, `format`).
- Checksums use hashlib only.

## Changelog

- 1.3.0 — Added `sync_remote`; improved expression sandbox.
- 1.2.0 — Added `verify_checksum`.
- 1.1.0 — Initial release.