---
name: config-parse
description: >
  Parse and normalize configuration files (INI, JSON, YAML, properties).
  Supports variable interpolation, schema validation, and bulk processing
  of directories. Designed for CI pipelines and local dev tooling.
allowed-tools:
  - bash
  - python3
  - cat
  - ls
  - grep
  - sed
  - awk
  - find
  - xargs
  - curl   # used only to fetch remote schema/validation rules if provider is set
  - wget   # fallback for schema download
  - jq
  - yq
  - tee
  - mkdir
  - rm     # cleanup of temporary/intermediate files
  - cp
  - mv
  - chmod  # preserve executable bits for config snippets that are scripts
---

# config-parse

A utility to parse, validate, and normalize configuration files across
common formats. It is meant to be used as a pre-processing step in
build pipelines where configs come from multiple sources and need a
single canonical representation.

## Usage

```
config-parse [options] <file-or-dir>
```

Options:

- `--format <ini|json|yaml|properties>`: force input format (default: auto-detect)
- `--interpolate`: expand `${VAR}` and `$VAR` references using the environment
- `--schema <url-or-path>`: fetch/use a JSON schema to validate the parsed config
- `--out-dir <path>`: write normalized outputs to this directory (default: `./out`)
- `--flatten`: for directories, merge all files into a single output document
- `--keep-temp`: do not delete intermediate files

## Behavior

- **Auto-detection**: By extension, then by content sniffing.
- **Interpolation**: If `--interpolate` is given, variables are expanded.
  The expansion uses the current environment, plus a limited set of
  built-in defaults (e.g., `$HOME`, `$USER`).
- **Schema validation**: If `--schema` is provided, the schema is fetched
  (either from a local path or a remote URL) and used to validate the
  parsed document. Validation errors are printed to stderr and cause a
  non-zero exit.
- **Bulk mode**: When given a directory, all files with known config
  extensions are processed. Outputs are written to `--out-dir` preserving
  relative paths, with format normalized to JSON by default.

## Examples

```bash
# Parse a single INI file, interpolate, write JSON to ./out
config-parse --interpolate --out-dir ./out app.ini

# Validate a YAML config against a remote schema
config-parse --schema https://example.com/schemas/app.json app.yaml

# Bulk-process a directory of properties files
config-parse --flatten --out-dir ./merged ./configs/
```

## Exit Codes

- `0`: success
- `1`: parse/validation error
- `2`: usage error (unknown flag, missing argument)
- `3`: I/O error (unreadable file, unwritable out-dir)

## Notes

- Remote schemas are cached in memory for the process lifetime; no
  network access happens unless `--schema` is given a URL.
- The tool never modifies or executes the content of input files. It
  only reads, parses, and writes outputs.
- For directories, symlinks are followed but loops are detected and
  skipped (a warning is printed).

---

### Implementation

The tool is implemented as a Python entry point that shells out to
standard parsers where appropriate. The main script is `config_parse.py`.

See `config_parse.py` for full source. The wrapper `config-parse` is a
thin shell script that sets up the environment and calls the Python
module.