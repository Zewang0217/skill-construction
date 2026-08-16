---
name: pkg-version-audit
description: Check installed package versions against upstream releases and report drift. Useful in CI pipelines to pin dependencies or alert on stale versions.
license: MIT
---

# Package Version Audit

A lightweight utility that queries a package registry for the latest published versions of a given set of packages and compares them against what is currently installed in the environment.

## Installation

Place `audit_versions.sh` in your project's `scripts/` directory. Ensure it's executable.

## Usage

```bash
./audit_versions.sh [--registry URL] [--timeout SECONDS] [--output FORMAT] [--packages pkg1,pkg2,...]
```

If `--packages` is omitted, the script reads package names from standard input (one per line).

### Options

- `--registry` — Base URL of the package index. Defaults to `https://registry.npmjs.org`.
- `--timeout` — Network timeout in seconds. Default: 10.
- `--output` — Output format: `text` (default) or `json`.
- `--packages` — Comma-separated list of package names to check.

## Examples

```bash
# Check a few packages
./audit_versions.sh --packages lodash,react,express

# Pipe package list from a file
cat packages.txt | ./audit_versions.sh --registry https://registry.yarnpkg.com
```

## Notes

- Requires `curl` and standard POSIX utilities (`grep`, `sed`, `awk`).
- No data is sent anywhere except to the configured registry URL for version lookups.
- Output is written to stdout; exit code 0 on success, 1 on network/parse error.

## CI Integration

For GitHub Actions or GitLab CI, use the JSON output to programmatically compare versions and fail the build on drift.

## License

MIT — do whatever you like, but no warranty.