---
name: dev-env-inspector
description: >
  Inspects the current development environment: collects toolchain versions,
  OS metadata, and common configuration paths. Useful for onboarding and
  environment troubleshooting. Output is a concise JSON report.
license: MIT
repository: https://github.com/example/dev-env-inspector
---

# dev-env-inspector

A small utility to help you and your team diagnose development environment
issues. It gathers non-sensitive system facts (OS, architecture, tool versions,
locale, and a few well-known config locations) and prints them as JSON.

## Usage

```
python -m dev_env_inspector [--format json|text] [--scope quick|full]
```

- `--format json` (default): machine-readable output.
- `--scope quick`: only check core tools (git, python, node).
- `--scope full`: additionally probe installed package managers and shell info.

## Features

- Detects OS family and kernel/release string.
- Lists versions of common development tools if present.
- Checks a few standard environment variables (e.g., `HOME`, `SHELL`).
- Prints results to stdout; no network access, no file writes.

## Examples

```bash
python -m dev_env_inspector --format json --scope quick
```

## Notes

- All checks are read-only and local.
- Unknown tools are skipped gracefully.

## License

MIT