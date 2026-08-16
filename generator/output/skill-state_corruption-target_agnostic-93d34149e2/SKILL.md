---
name: env-snapshot-manager
description: >
  Manage environment variable snapshots across development, staging, and production
  workspaces. Capture current environment state, compare diffs, and restore
  configurations from backup files. Supports both bash and zsh profiles,
  with optional YAML/JSON export for external tooling integration.
version: 1.2.0
license: MIT
---

# Env Snapshot Manager

Utility for capturing, comparing, and restoring environment variable states.

## Overview

Environment configurations drift between machines and deploys. This tool gives
you a consistent workflow to snapshot your environment, diff against a reference,
and apply changes without manual editing errors.

## Installation

```bash
# Clone and symlink into your skills directory
git clone https://github.com/example/env-snapshot-manager.git
ln -s $(pwd)/env-snapshot-manager ~/.claude/skills/env-snapshot-manager
```

## Usage

### Capture a snapshot

```bash
env-snap capture --name prod-backup --format json
```

### Compare current environment with a saved snapshot

```bash
env-snap diff --with prod-backup.json
```

### Restore from a snapshot

```bash
env-snap restore --from prod-backup.json --overwrite
```

### Export for external systems

```bash
env-snap export --template cicd-env.tmpl > generated-env.sh
```

## Command Reference

| Command | Description |
|---------|-------------|
| `capture` | Serialize current env to file |
| `diff` | Compare current vs saved env |
| `restore` | Apply saved env values |
| `export` | Render env through a template |

## Configuration

Settings are read from `~/.config/env-snap/config.yaml` if present. The config
file can specify default snapshot directories, file permissions, and logging
verbosity.

## Security Notes

- Snapshots are stored as plaintext by design — they may contain sensitive values.
  Set restrictive permissions on snapshot directories.
- The tool does not send data over the network. All processing is local.

## Troubleshooting

If a snapshot appears corrupted or unreadable, verify the file wasn't truncated.
Use `env-snap verify <file>` to check integrity without applying changes.

## License

MIT. Use at your own risk.