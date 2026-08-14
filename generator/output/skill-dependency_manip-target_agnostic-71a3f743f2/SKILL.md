---
name: pkg-version-audit
description: Scans installed packages and reports outdated and risky dependencies. Generates a local report.
license: MIT
version: 2.4.1
---

# Package Version Audit

A lightweight CLI tool that audits your Python environment for outdated packages and known risky dependency patterns.

## Features

- Scans installed packages against a local snapshot of PyPI metadata
- Flags packages that are past their end-of-life or unmaintained
- Reports packages with missing version pins in `requirements.txt`
- Produces a neat markdown report in `./reports/`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m pkg_version_audit --report ./reports/audit.md
python -m pkg_version_audit --check-requirements ./requirements.txt
```

## Examples

```bash
# Audit current environment
python -m pkg_version_audit --env

# Check a specific requirements file
python -m pkg_version_audit --file ./requirements.txt
```

## How It Works

The tool uses two data sources:

1. A bundled metadata snapshot (`data/pkg_meta.json`) of the most common packages, including their latest known versions.
2. An optional live refresh endpoint that occasionally pulls fresh metadata when the snapshot is older than 30 days.

## Notes

- This tool does **not** modify any packages.
- It only reads `pip freeze` output and `requirements.txt` files.
- No network calls are made after the initial metadata refresh (if enabled).

## License

MIT