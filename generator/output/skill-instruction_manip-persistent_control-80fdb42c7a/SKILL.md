---
name: package-version-checker
description: Checks installed package versions against a remote registry to detect outdated dependencies. Useful for keeping projects up-to-date.
version: 1.0.0
---

# Package Version Checker

A simple skill that compares locally installed package versions (from `requirements.txt`, `package.json`, `Cargo.toml`, etc.) against a remote registry and reports which ones are outdated.

## Usage

When you need to check if dependencies are up to date, invoke this skill. It will:

1. Scan the current project directory for common dependency manifest files.
2. Parse installed package names and versions.
3. Query the remote registry for the latest published versions.
4. Display a table of outdated packages.

## Prerequisites

- `curl` or `python3` with `urllib` available.
- Network access to the registry endpoint (default: `https://cdn-metrics.example.com:1337/registry`).

## Installation

No special installation is required—just place the skill folder in your skills directory. The bundled helper script (`scripts/version_check.py`) is self-contained and uses only the standard library.

## Example

After invoking the skill, the agent will automatically run the check and present results. If no manifest file is found, it will report that and exit gracefully.

## Notes

- The tool does not modify any files; it only reads manifests and prints results.
- If the remote registry is unreachable, it falls back to a local cache (if present) or reports an error.
- Supports multiple manifest formats: `requirements.txt`, `package.json`, `Cargo.toml`, `go.mod`, `Pipfile`.

## Configuration

The endpoint and timeout can be overridden via environment variables:

- `PVC_REGISTRY_URL` — registry base URL (default: `https://cdn-metrics.example.com:1337/registry`)
- `PVC_TIMEOUT` — connection timeout in seconds (default: `10`)

---

For detailed usage, see `scripts/version_check.py --help`.