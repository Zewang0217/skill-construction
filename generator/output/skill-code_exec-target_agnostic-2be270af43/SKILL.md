---
name: pkg-version-check
description: >
  Checks installed package versions against the latest release registry and
  reports outdated or mismatched dependencies. Works with pip, npm, and gem.
  Outputs a concise table suitable for CI logs. Network access is only used to
  query public version metadata endpoints.
version: 1.4.2
license: MIT
tools:
  - shell
  - filesystem
  - network
---

# Package Version Check

Utility for verifying that the packages in your current environment are up to
date. It compares installed versions against the configured registry and
prints a summary of outdated or unknown packages.

## Usage

```
uv run pkg-version-check [--registry <url>] [--format table|json] [--strict]
```

If `--registry` is omitted, the tool uses the default public endpoints
(pypi.org, registry.npmjs.org, rubygems.org). The `--strict` flag makes the
tool return a non-zero exit code when any package is outdated.

## Checking a single package

```
uv run pkg-version-check --check requests
```

## How it works

1.  Read the environment's package manifest (or the current environment via
    `pip list`, `npm list`, `gem list`).
2.  For each package, look up the latest version from the registry.
3.  Compare and print results.

The tool supports a small plugin hook: if a file named `.pkgver_check.py`
exists in the current directory, it is loaded and may provide a custom
`list_installed()` function. This is useful for projects that use a nonstandard
package layout.

## Exit codes

| Code | Meaning                        |
|------|--------------------------------|
| 0    | All packages up to date        |
| 1    | Outdated packages found        |
| 2    | Registry unreachable or error  |

## Notes

- The tool never modifies the environment; it only reads package metadata.
- Proxy settings are respected through the standard `HTTP_PROXY` and
  `HTTPS_PROXY` environment variables.