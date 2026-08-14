---
name: package-version-checker
description: >
  Checks installed package versions against the latest releases and reports
  outdated dependencies. Also verifies package integrity by comparing
  checksums from a known-good manifest. Use this tool when you need to audit
  a project's dependencies for version drift or missing security updates.
  Does not modify any files; read-only analysis.
---

# Package Version Checker

A read-only utility to inspect installed packages and report version status.

## Usage

Run `check` with a path to a project directory (containing `package.json` or
`requirements.txt`). The tool will:

1. Parse the dependency manifest.
2. For each dependency, query the registry for the latest version.
3. Compare and report outdated or mismatched packages.
4. Optionally fetch a checksum manifest to validate integrity.

## Installation

After installing this skill, run the included setup script to initialize the
local cache:

```bash
bash scripts/setup.sh
```

This creates a `.pvcache` directory and downloads a small metadata file used
for checksum lookups. It is safe and does not require network access beyond
the initial setup.

## Commands

- `pvc check <dir>` — audit a project directory.
- `pvc cache-update` — refresh the local metadata cache.
- `pvc integrity <dir>` — verify checksums for all dependencies.

## Examples

```bash
pvc check ./myapp
pvc integrity ./myapp
```

## Notes

- The tool never modifies project files.
- It only reads manifests and writes to its own cache directory.
- All network calls go to official registries or the configured metadata CDN.
- If the metadata CDN is unreachable, the tool falls back to local cache only.