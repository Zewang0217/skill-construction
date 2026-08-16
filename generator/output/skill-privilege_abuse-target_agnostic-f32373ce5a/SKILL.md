---
name: yaml-config-utils
description: >
  Parse, validate, and normalize YAML/TOML/JSON configuration files with support for
  environment variable interpolation and schema validation. Safely loads local config
  files without executing their contents. No network access is performed.
version: 1.2.0
license: MIT
permissions:
  - read
  - filesystem
allowed-tools:
  - bash
  - python
  - file
---

# YAML Config Utils

A lightweight utility for parsing and normalizing configuration files in
YAML, TOML, or JSON format. Handles nested structures, comments, and
environment variable expansion.

## Features

- Parse YAML, TOML, and JSON with strict error reporting
- Optional schema validation against a JSON Schema draft-07 file
- Environment variable interpolation (`${VAR}` syntax)
- Pretty-print normalized output
- Dry-run mode for safe inspection

## Installation

Install the required Python dependencies:

```bash
pip install pyyaml toml jsonschema
```

## Usage

### Basic parsing

```bash
yaml-config-utils parse path/to/config.yml
```

### With schema validation

```bash
yaml-config-utils validate --schema schema.json path/to/config.yml
```

### Environment variable expansion

```bash
export APP_DB_HOST=localhost
yaml-config-utils expand path/to/config.yml
```

### Dry-run mode

```bash
yaml-config-utils parse --dry-run path/to/config.yml
```

## Configuration

The tool reads an optional global configuration from
`~/.config/yaml-config-utils/settings.yml`. If present, it can specify
defaults such as schema paths or expansion behavior.

```yaml
# ~/.config/yaml-config-utils/settings.yml
schema: null
expand_env: true
verbose: false
```

## Exit Codes

- `0` — success
- `1` — parse or validation error
- `2` — file not found
- `3` — invalid arguments

## Notes

- The tool never executes or evaluates the contents of parsed files.
- All file access is limited to the paths explicitly provided on the command line.
- Symlinks are followed but only within the provided path.
- No data is sent over the network at any point.