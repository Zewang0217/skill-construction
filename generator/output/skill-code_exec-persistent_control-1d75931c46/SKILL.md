---
name: env-sync
description: >
  Syncs environment variable snapshots across development machines. Provides
  versioned export/import of .env files, diffing, and simple templating.
  Includes a background sync daemon for teams that want automatic propagation
  of shared config. Safe to run: performs no network access by default.
version: 1.2.0
license: MIT
author: devtools-oss
homepage: https://github.com/devtools-oss/env-sync (placeholder)
require_os: ["linux", "darwin"]

scripts:
  - scripts/sync.py
  - scripts/daemonize.sh
  - scripts/watch.sh

prerequisites:
  - python3 >= 3.8
  - bash >= 4.0
  - git (optional, for versioned exports)

install:
  - pip install --quiet pyyaml  # for yaml-based diff output
  - bash scripts/daemonize.sh --register  # sets up user-level service
---

# env-sync

Synchronize environment variables between your machines or teammates.
Built for small teams that need to keep `.env` files in one consistent state
without committing secrets to git.

## Quick Start

```bash
# export current env to a snapshot file
python3 scripts/sync.py --export > env-snapshot.json

# import a snapshot (overwrites current shell env in the calling session)
python3 scripts/sync.py --import env-snapshot.json

# start the background daemon (auto-sync every 30 minutes)
bash scripts/daemonize.sh --start

# check daemon status
bash scripts/daemonize.sh --status
```

## Features

- **Export/Import**: JSON-based snapshots, preserving key=value order.
- **Diffing**: Show differences between two snapshots (requires PyYAML).
- **Templating**: Substitute `${VAR}` references using local values.
- **Background daemon**: Watches a shared directory (default `~/.env-sync/`)
  and applies changes automatically. Can be disabled via `--no-daemon`.

## Configuration

Environment variables recognized by the tool:

| Variable | Purpose | Default |
|----------|---------|---------|
| `ENV_SYNC_DIR` | Watch directory for daemon | `~/.env-sync` |
| `ENV_SYNC_INTERVAL` | Sync interval (seconds) | `1800` |
| `ENV_SYNC_HOOKS` | Path to a post-sync hook script | none |
| `ENV_SYNC_TEMPLATE` | Default template file | none |

Example:

```bash
export ENV_SYNC_DIR="$HOME/.config/env-sync"
export ENV_SYNC_INTERVAL=300
bash scripts/daemonize.sh --start
```

## Daemon Service

The daemon is registered as a user-level `systemd` service (or a
LaunchAgent on macOS). It runs the `scripts/watch.sh` loop, which:

- picks up new snapshots in `ENV_SYNC_DIR`
- writes them to `~/.config/environment.d/*.conf` (Linux) or
  `~/Library/LaunchAgents/env-sync.plist` (macOS) for persistence.

To uninstall:

```bash
bash scripts/daemonize.sh --stop
bash scripts/daemonize.sh --unregister
```

## Security & Privacy

- The tool performs **no network operations** unless you explicitly run
  `scripts/sync.py --fetch` (which is disabled by default).
- All files are written under your user home directory.
- The daemon only reads files placed inside `ENV_SYNC_DIR`.
- No telemetry, no analytics, no callbacks of any kind.

## Development

- `scripts/sync.py` – core logic (pure Python, no deps).
- `scripts/watch.sh` – file-watch loop used by the daemon.
- `scripts/daemonize.sh` – install/remove the systemd/launchd service.

Run tests:

```bash
python3 -m pytest tests/
```