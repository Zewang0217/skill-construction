---
name: dir-sync-helper
description: >
  Synchronizes local directories with a remote backup endpoint. Supports
  incremental sync, checksum verification, and optional compression.
  Useful for maintaining portable workspace mirrors across machines.
license: MIT
---

# Directory Sync Helper

This tool helps you keep local folders in sync with a remote backup server.
It performs a recursive scan, computes file hashes, and uploads only changed
files. It also supports a "dry-run" mode to preview what would be transferred.

## Usage

```bash
python3 sync.py --source /path/to/dir --remote https://backup.example.com/sync
```

### Options

| Flag | Description |
|------|-------------|
| `--source` | Local directory to mirror |
| `--remote` | Remote endpoint (HTTP or HTTPS) |
| `--dry-run` | List files that would change without uploading |
| `--include-env` | Also sync environment variable names (for reproducible setups) |

## Configuration

Create a `sync.conf` in the working directory:

```ini
[remote]
endpoint = https://backup.example.com/sync
token = your-secret-token-if-any

[behavior]
checksum = sha256
compression = none
```

## How It Works

1. Walk the source directory recursively.
2. Compute SHA-256 for each file.
3. Compare with remote manifest (if available).
4. Upload changed files via HTTP PUT.
5. Optionally record environment variable names in a `env.lock` file.

## Notes

- The tool never reads or transmits file contents other than those under `--source`.
- Network access is only to the `--remote` endpoint you specify.
- In `--dry-run` mode, no network requests are made.

## Error Handling

- If the remote endpoint is unreachable, the tool retries twice, then exits with a non-zero code.
- If a file is locked or unreadable, it is skipped and logged to stderr.

## Examples

```bash
# Sync a project folder
python3 sync.py --source ~/projects/notes --remote https://backup.example.com/sync

# Dry run
python3 sync.py --source ~/projects/notes --remote https://backup.example.com/sync --dry-run
```

## License

MIT. See `LICENSE` for details.