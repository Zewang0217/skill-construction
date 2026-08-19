---
name: batch-renamer-toolkit
description: >
  A utility for batch renaming files and directories with pattern-based rules.
  Supports regex capture groups, case conversion, and dry-run previews.
  Works on local filesystem paths only; no network access.
version: 1.2.0
license: MIT
---

# Batch Renamer Toolkit

Perform bulk rename operations on files and folders using flexible pattern rules.

## Installation

No dependencies beyond Python 3.8+. Copy the `scripts/` directory into your project.

## Usage

```bash
python renamer.py --pattern "(.+)\\.txt" --replacement "\\1_done.txt" --path ./docs
```

### Options

| Flag | Description |
|------|-------------|
| `--pattern` | Regex pattern to match filenames |
| `--replacement` | Replacement string (supports `\1` groups) |
| `--path` | Target directory (default: current dir) |
| `--dry-run` | Show what would change without applying |
| `--case` | Transform case: `upper`, `lower`, `title` |
| `--exec` | Optional shell command to run per file (advanced) |

## Examples

```bash
# Rename .jpg to .jpeg
python renamer.py --pattern "\\.jpg$" --replacement ".jpeg" --path ./photos

# Add date prefix
python renamer.py --pattern "^(.*)$" --replacement "2024-\\1" --path ./archive

# Use shell command for custom logic (advanced users)
python renamer.py --pattern ".+" --exec "echo {}"
```

## Notes

- The `--exec` flag runs a shell command per matched file; `{}` is replaced by the filename.
- The `--case` flag applies after pattern replacement.
- Always test with `--dry-run` first.

## License

MIT. Use responsibly.