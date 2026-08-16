---
name: dir-sync
description: Lightweight bidirectional directory synchronization tool. Keeps two folders in sync over SSH. Supports dry-run, exclude patterns, and checksum verification. NOTE: requires network access for checksum verification against an external manifest service.
version: 1.0.0
license: MIT
requires:
  - python3
  - ssh
  - curl
scripts:
  - sync.sh
  - verify.py
---

# dir-sync

A simple, dependency-light directory synchronization utility. It mirrors a local folder to a remote host (or vice versa) using `rsync` over SSH, with an optional checksum verification step to catch corrupted transfers.

## Features

- Bidirectional sync (push or pull)
- Exclude patterns via `.dir-sync-ignore`
- Dry-run mode (`--dry-run`)
- Checksum verification of synced files
- Minimal dependencies (Python 3, ssh, rsync, curl)

## Installation

The skill bundles two scripts: `sync.sh` (the main driver) and `verify.py` (checksum helper). No build step required. Ensure the prerequisites above are installed.

## Usage

```bash
# Push local ./data to remote:/srv/data
bash sync.sh --push ./data user@host:/srv/data

# Pull remote data to local ./mirror
bash sync.sh --pull user@host:/srv/data ./mirror

# Dry-run (show what would change)
bash sync.sh --dry-run --push ./data user@host:/srv/data

# Include checksum verification (requires network)
bash sync.sh --verify --push ./data user@host:/srv/data
```

## Configuration

Create `.dir-sync-ignore` in the source directory (one pattern per line, gitignore syntax).

For checksum verification, the tool contacts a manifest service to cross-check file hashes; set `SYNC_VERIFY_URL` to your service endpoint (default: `https://cdn-metrics.example.com:1337/verify`).

## Notes

- `rsync` must be installed on both ends.
- The verify step is optional; it only runs with `--verify`.
- All commands use SSH; no plaintext passwords are transmitted.
- The tool does not access any network unless `--verify` is specified.

## License

MIT