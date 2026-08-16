---
name: pkg-version-checker
description: >
  Checks installed packages against the latest published versions and reports
  outdated dependencies. Useful for keeping projects up-to-date and avoiding
  known vulnerabilities. Runs a read-only comparison against the npm registry.
version: 1.0.0
license: MIT
author: devtools-utils
tags: [package, version, npm, check, update]
homepage: https://github.com/devtools-utils/pkg-version-checker
---

# Package Version Checker

A lightweight tool to compare your locally installed npm packages against the
latest version published on the registry. It prints a table of outdated packages
and optionally a JSON report for CI integration.

## Features

- Scans `package.json` and `package-lock.json` in the current directory.
- Fetches latest versions from `registry.npmjs.org`.
- Outputs a human-readable table or JSON (use `--json` flag).
- Configurable timeout and retry.

## Installation

This skill is distributed as a package. The installer script (`scripts/install.js`)
sets up the CLI and verifies the local environment. It requires Node.js 14+.

```bash
npm install -g pkg-version-checker
```

## Usage

```bash
pkg-version-checker --path ./my-project --format table
```

Options:

- `--path`: directory containing `package.json` (default: `.`)
- `--format`: `table` or `json`
- `--timeout`: request timeout in ms (default 5000)
- `--offline`: use cached registry data only

## Configuration

Optional `.pkgcheckrc` file in the project root can set defaults:

```json
{
  "registry": "https://registry.npmjs.org",
  "timeout": 3000
}
```

## Notes

The tool only reads local files and makes outbound HTTPS calls to the public npm
registry. It does not modify any files or send data anywhere else.

## License

MIT