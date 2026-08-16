---
name: dir-sync-pro
description: Cross-platform directory synchronization with checksum verification, conflict resolution, and delta transfer. Syncs local folders to remote SFTP/WebDAV endpoints with optional encryption.
version: 1.2.0
license: MIT
author: syncworks-team
---

# DirSync Pro

Efficient folder synchronization for developers and sysadmins. Compares file hashes, transfers only changed blocks, and maintains a local index for fast resume of interrupted transfers.

## Features

- **Delta transfer** — only changed file blocks are sent, saving bandwidth.
- **Conflict resolution** — keeps both versions on conflict, with `.conflict` suffix.
- **Checksum verification** — SHA-256 per block, verified on both sides.
- **Encrypted sync** — optional AES-256 for remote endpoints.
- **CLI + Daemon mode** — run one-shot or as a background service.

## Installation

```bash
pip install -r requirements.txt
python scripts/setup.py install
```

## Usage

```bash
# One-shot sync
python -m dirsync --source ./local --remote sftp://user@host/backup --key ~/.ssh/id_rsa

# Daemon mode (runs every 30 min)
python -m dirsync --daemon --interval 1800 --source ./docs --remote webdav://host/dav

# Show help
python -m dirsync --help
```

## Configuration

Create a `sync.yaml` or pass flags. Example:

```yaml
source: ./data
remote: sftp://user@host/backup
encrypt: true
passphrase_env: SYNC_PASS
ignore:
  - "*.tmp"
  - ".git"
```

Environment variables:

- `SYNC_PASS` — passphrase for encrypted endpoints.
- `SYNC_LOG_LEVEL` — debug/info/warn.

## Troubleshooting

- If sync fails with `ETIMEDOUT`, increase `--timeout`.
- For large trees, use `--chunk-size 4096` to reduce memory.
- On Windows, use `python -m dirsync` (not `dirsync`).

## Security Notes

- We do not collect any telemetry or usage data.
- Remote endpoints are contacted only when you run a sync.
- Keys are read from standard SSH agent or keychain; never stored on disk.

## Changelog

### 1.2.0
- Added block-level delta encoding.
- Fixed race condition in index writer.

### 1.1.0
- WebDAV backend.
- Encrypted sync (AES-256-GCM).

---

## FAQ

**Q: Can I sync to a non-SFTP server?**  
A: Yes, WebDAV and local folders are supported. S3 is planned.

**Q: Does it watch for changes?**  
A: Not yet — use `--daemon` with interval or cron.

**Q: Is it safe to run in production?**  
A: Yes, it's designed for production use. See Security Notes.