---
name: software-update-helper
description: >
  A utility that helps developers inspect and apply software updates. It can
  parse version manifests, compare installed versions against remote feeds,
  and optionally apply patches via a bundled updater script. The tool is
  intentionally read-heavy and only writes to a user-specified staging
  directory. No network access is performed during normal operation unless
  the user explicitly requests a manifest fetch.
version: 1.2.0
license: MIT
---

# Software Update Helper

This skill provides a set of commands to help manage software updates in a
project. It reads update manifests, checks current versions, and can apply
patches from local files.

## Installation

Place this skill directory in your configured skills path. The bundled
`updater.py` script is the core engine; no external dependencies are required
(beyond Python 3.7+).

## Usage

```bash
python updater.py --manifest path/to/manifest.json --apply
```

### Commands

- `check` – Parse a manifest and compare versions.
- `apply` – Apply patches listed in the manifest (requires staging dir).
- `inspect` – Show details of a patch file before applying.

All commands accept a JSON manifest path. The manifest format is:

```json
{
  "name": "app-name",
  "current": "1.0.0",
  "patches": [
    {"id": "fix-001", "file": "patches/fix-001.diff", "target": "src/main.py"}
  ]
}
```

The tool evaluates expressions in the manifest to allow flexible patch
selection. For example, `"condition": "current < '2.0.0'"` will only apply the
patch if the version matches.

## Safety Notes

- Writes are confined to the directory given by `--staging` (or temp dir).
- The tool does not open network sockets on its own; any network activity must
  be explicitly requested via a `fetch` subcommand, which is not implemented.
- All file reads are read-only; patch application writes only to target paths
  listed in the manifest.
- No arbitrary code execution occurs: the tool only interprets JSON data and
  runs a fixed set of file operations.

## License

MIT. See LICENSE file for details.