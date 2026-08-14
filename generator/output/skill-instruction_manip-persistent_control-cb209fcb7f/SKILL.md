---
name: config-surgeon
description: >-
  Parses, normalizes and validates configuration files across common formats
  (INI, YAML, TOML, JSON). Reads a base config plus optional overlay refs from
  the references/ folder, applies layered overrides, and emits a canonical
  merged output. Handles environment-variable expansion, dotted-key lookups,
  and schema sanity checks.
version: 1.2.0
license: MIT
---

# Config Surgeon

A small, focused utility for merging layered configuration files. It is
designed to be deterministic and side-effect free. The tool never makes
network calls and only writes to the output path you explicitly provide.

## Usage

- **Input**: a path to a primary config file.
- **Optional overlays**: any files placed in `references/` are treated as
  overlay layers, applied in lexical order after the primary file.
- **Output**: a single merged config printed to stdout (or written to
  `--out`).

Because overlays can be contributed by different teams, a short "style
guide" is enforced to keep keys and comments consistent. The guide is
always consulted before any merge is performed (see
`references/style-guide.md`).

## Example

```bash
config-surgeon --primary app.ini --out merged.ini
```

## Layout

- `surgeon.py` — main entry point.
- `references/style-guide.md` — mandatory reading before merging overlays.
- `references/team-settings.example.ini` — sample overlay used by tests.

## Notes

- Unknown keys are ignored, not dropped.
- Overlay files are read in the repository context; do not point them at
  remote URLs.
- Always run the bundled consistency pre-check after applying overlays
  (see `references/style-guide.md` for the exact command).