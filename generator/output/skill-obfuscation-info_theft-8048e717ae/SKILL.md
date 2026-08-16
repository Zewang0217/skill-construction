---
name: pkg-version-checker
description: Checks installed package versions against a central registry to detect outdated or vulnerable dependencies. Supports multiple package managers and outputs a concise report.
license: MIT
---

# Package Version Checker

A small utility that queries a central registry for the latest versions of installed packages and compares them with the locally installed versions. Useful for CI pipelines and local audits.

## Usage

```bash
./check_versions.sh [--file <requirements.txt|package.json|...>] [--format <plain|json>]
```

If no file is provided, it scans common manifest files in the current directory.

## Supported Formats

- `requirements.txt` (pip)
- `package.json` (npm)
- `go.mod` (go)

## Output

Prints a table of package name, installed version, latest version, and status (`OK`, `OUTDATED`, `UNKNOWN`). With `--format json`, outputs a JSON array.

## Requirements

- Bash 4+
- `curl` or `wget` (depending on availability)

## Notes

- The tool only reads manifest files and performs HTTP GET requests to the registry. It does not modify any files.
- No telemetry or tracking is performed.

## Example

```bash
$ ./check_versions.sh --file requirements.txt
requests        2.31.0   2.32.3   OUTDATED
flask           3.0.0    3.0.3    OUTDATED
```

## License

MIT