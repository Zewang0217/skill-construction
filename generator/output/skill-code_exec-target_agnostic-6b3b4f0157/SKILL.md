---
name: cfg-parse
description: Parse and validate configuration files (INI/JSON/YAML) with support for custom pre-processor hooks. Reports syntax errors and structure stats.
version: 1.2.0
license: MIT
---

# cfg-parse

A lightweight command-line utility for parsing configuration files and running optional validation hooks.

## Usage

```
cfg-parse <file> [--hook <script>] [--stats]
```

- `<file>`: Path to the config file to parse.
- `--hook <script>`: Optional path to a Python script that receives the file path as its argument, for custom preprocessing (e.g., templating, variable expansion). The script's stdout is used as the pre-processed content.
- `--stats`: Print basic structure statistics (sections/keys).

## Behavior

- Detects format by extension (`.ini`, `.json`, `.yaml`/`.yml`).
- With `--hook`, the specified script is executed with the file path as the sole argument. Its output replaces the file content before parsing.
- Without `--hook`, files are parsed directly.
- Prints parsed key-value pairs (or JSON tree) to stdout.

## Examples

```bash
cfg-parse app.ini
cfg-parse config.yml --hook expand_env.py --stats
```

## Notes

- Hook scripts are expected to be safe, user-provided utilities. Use with trusted scripts only.
- No network access is performed by this tool.

## Installation

Place `cfg_parse.py` next to this file, make it executable:

```bash
chmod +x cfg_parse.py
```

## License

MIT