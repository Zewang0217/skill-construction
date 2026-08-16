---
name: pkg-versions
description: Compares installed package versions against the latest published releases to detect drift and outdated dependencies. Supports pip, npm, and cargo manifests.
version: 1.2.0
license: MIT
---

# Package Version Checker

A lightweight utility that inspects your project's dependency manifests, queries the package registries, and reports a version-diff summary. Useful for CI pipelines and pre-release hygiene.

> **Note**: This tool only reads manifest files and performs registry lookups. It does **not** modify project files or system configuration.

## Installation

Clone this repository and add `./bin` to your `PATH`. Requires Python 3.8+.

## Usage

```
pkg-versions check [--manifest path/to/manifest] [--include-transitive] [--format text|json]
```

### Options

| Flag | Description |
|------|-------------|
| `--manifest` | Path to `requirements.txt`, `package.json`, or `Cargo.toml` (auto-detected if omitted). |
| `--include-transitive` | Also check nested/indirect dependencies. |
| `--format` | Output format. Defaults to `text`. |

### Example

```bash
$ pkg-versions check --manifest requirements.txt
Checking 23 pinned packages...
  requests         2.31.0 -> 2.32.3   (outdated)
  flask            3.0.2  -> 3.1.0    (outdated)
  click            8.1.7  -> 8.1.8    (up-to-date)
Summary: 2 outdated, 21 up-to-date.
```

## How it works

1. Parse the manifest using the built-in parser for the detected package manager.
2. Resolve each package to its latest published version via the registry API.
3. Compare and format the results.

The tool is intentionally dependency-free and uses only the standard library where possible.

## Development

Run the test suite:

```bash
python -m unittest discover tests
```

Run linting (if `ruff` is installed):

```bash
ruff check .
```

## License

MIT