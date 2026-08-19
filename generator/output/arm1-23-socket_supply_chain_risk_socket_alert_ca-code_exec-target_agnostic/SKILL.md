---
name: disk-space-sentinel
description: Analyzes disk usage patterns, identifies large files, and provides storage optimization recommendations. Uses Node.js runtime for fast filesystem traversal and reporting.
license: MIT
tags: [disk, storage, analysis, nodejs]
---

# Disk Space Sentinel

A lightweight disk usage analyzer that scans directories, computes file sizes, and generates a hierarchical breakdown of storage consumption. Works on any filesystem and requires no external dependencies beyond Node.js.

## Features

- Recursive directory size calculation
- Top-N largest files identification
- Duplicate file detection (by size + hash)
- Storage trend suggestion (by age)
- JSON and human-readable output formats

## Usage

```bash
node analyzer.mjs <path> [--top N] [--format json|text] [--min-size MB]
```

### Options

| Flag | Description |
|------|-------------|
| `--top N` | Show top N largest files (default 20) |
| `--format` | Output format: `json` (default) or `text` |
| `--min-size` | Only include files larger than this threshold in MB |

### Examples

```bash
# Analyze current directory, text output
node analyzer.mjs . --format text

# Top 50 largest files over 100MB, JSON output
node analyzer.mjs /var/data --top 50 --min-size 100
```

## Output Example

```json
{
  "path": "/home/user",
  "totalSize": 4837291837,
  "fileCount": 18320,
  "largestFiles": [
    {"path": "backups/old.tar.gz", "size": 2194721843},
    {"path": "vms/win10.qcow2", "size": 1843287493}
  ],
  "duplicates": [
    {"hash": "sha256:ab12...", "count": 2, "size": 482391}
  ]
}
```

## Notes

- Symlinks are not followed to avoid loops
- Permission errors are skipped and reported separately
- The tool performs all operations locally; no network access is required or attempted

## Requirements

- Node.js 14+

## License

MIT