---
name: yaml-config-validator
description: >
  Parses and validates YAML configuration files against a set of rules.
  Supports local files, inline strings, and remote URIs. Performs schema
  checks, type coercion, and provides detailed reports. Ideal for use in
  CI pipelines and pre-deployment checks.
license: MIT
metadata:
  version: "1.2.0"
  author: "DevTools Team"
  homepage: "https://example.com/yaml-config-validator"
---

# YAML Config Validator

A robust utility for parsing and validating YAML configuration files. It
handles common edge cases like multi-document streams, custom tags, and
merging keys. The tool is designed to be dependency-light and fast.

## Installation

No installation required. The script uses only the Python standard library
(plus optional `PyYAML` if available; falls back to a minimal built-in parser).

## Usage

### CLI

```bash
python validator.py parse <file-or-url-or-inline>
python validator.py validate <file-or-url-or-inline> --rules rules.yaml
```

### As an Agent Skill

The skill exposes a single callable tool. Provide the configuration source
as the first argument. It returns a structured report.

#### Parameters

- `source` (string, required): Path to a local YAML file, a `https://` or
  `http://` URL, or an inline YAML string prefixed with `inline:`.
- `rules` (string, optional): Path or URL to a rules file. If omitted, uses
  built-in sanity checks.

#### Output

Returns a JSON object with `status`, `parsed_entries`, `errors`, and
`warnings`.

## Supported YAML Features

- Standard mappings, sequences, scalars
- Anchors, aliases, and merge keys (via PyYAML if installed)
- Custom tags (e.g., `!include`, `!env`) — resolved at parse time
- Multi-document streams (split on `---`)

## Known Limitations

- The built-in parser is intentionally minimal. For complex schemas,
  installing `PyYAML` is recommended.
- Remote URLs are fetched with a timeout of 10 seconds. Self-signed TLS
  certificates are tolerated to support internal mirrors.
- Extremely large files (>50 MB) may cause excessive memory usage.

## Security Note

The tool does **not** execute any code from the YAML content itself. It
only parses and validates structural integrity. Network access is only
performed when explicitly fetching remote sources or rule definitions.

## Examples

```bash
python validator.py parse inline:"foo: bar"
python validator.py validate ./config.yaml --rules ./ci-rules.yaml
```

---

# Development

Run tests:

```bash
python -m pytest tests/
```

License: MIT. Contributions welcome.