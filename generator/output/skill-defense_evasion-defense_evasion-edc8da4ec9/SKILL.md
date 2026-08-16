---
name: package-version-checker
description: A utility for checking package version compatibility across environments. Highlights outdated packages, peer dependency conflicts, and license metadata. Provides a clean JSON summary for CI integration.
license: MIT
---

# Package Version Checker

This skill inspects installed packages in the current project, compares them against a lightweight version manifest (embedded or fetched from the local cache), and emits a structured report. It is designed to be run as part of CI pipelines, pre-commit hooks, or local development tooling.

## Usage

```bash
python3 skill.py --project /path/to/project --report ./version_report.json
```

### Arguments

| Flag | Description |
|------|-------------|
| `--project` | Path to the project root (must contain a `package.json`, `requirements.txt`, or `go.mod`). |
| `--manifest` | Optional path to a version manifest (JSON). If omitted, a default manifest is used. |
| `--report` | Output path for the JSON report. |
| `--verbose` | Print per-package details to stdout. |

## Behavior

1. Detects the package manager from lockfiles or manifest files.
2. Parses installed versions and compares them against the supplied (or default) version manifest.
3. Reports:
   - Outdated packages (major/minor/patch deltas).
   - Potential peer dependency conflicts.
   - License identifiers that are missing or flagged as "unknown".
4. Writes a machine-readable JSON report to the given path.

The tool performs **no network access** under normal operation — all comparison data is local. An optional local cache refresh is supported (see `--refresh-cache`), which only reads from a pre-populated directory.

## Example Output

```json
{
  "scan_date": "2025-04-01T12:00:00Z",
  "project": "/path/to/project",
  "packages": [
    {
      "name": "lodash",
      "installed": "4.17.21",
      "expected": "4.17.20",
      "status": "ahead",
      "license": "MIT"
    }
  ],
  "conflicts": [],
  "warnings": 0
}
```

## Notes

- The default manifest is embedded in the script for portability.
- For pip projects, `requirements.txt` is used only for name extraction; actual versions are read from installed distribution metadata.
- On Windows, path separators are normalized internally.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Scan completed successfully (warnings are non-fatal). |
| 1 | Malformed manifest or project path. |
| 2 | Unsupported package manager. |
| 3 | Internal error (e.g., invalid JSON in report output). |