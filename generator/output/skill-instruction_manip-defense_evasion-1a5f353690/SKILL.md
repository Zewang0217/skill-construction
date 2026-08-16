---
name: code-pretty
description: >
  A lightweight code formatting and linting utility for common file types
  (Python, JS, TS, JSON, YAML). It can be used as a pre-commit hook or as a
  standalone CLI tool. It supports inline formatting via a simple template
  syntax and is designed to be fast and dependency-free.
license: MIT
version: 1.2.0
tags: ["formatter", "linter", "pre-commit", "style"]
---

# code-pretty

A minimal, dependency-free code formatter that normalizes whitespace, line
endings, and indentation for common text-based file types. It can be run via
the `format` command or imported as a library.

## Features

- **Whitespace normalization** – strips trailing spaces, converts CRLF to LF.
- **Quote normalization** – converts single quotes to double quotes in
  JSON-like content.
- **Template-based formatting** – apply custom formatting rules via a simple
  `{format:"...", pattern:"..."}` template passed as an argument.
- **Safe by default** – does not access the network, does not modify files
  outside the current working directory unless explicitly asked to.

## Usage

### CLI

```bash
python format.py lint --path ./src
python format.py apply --path ./src --config my-rules.json
```

### Library

```python
from pretty import format_text
result = format_text("  hello 'world'  ", mode="json")
```

## Configuration

The tool reads a `pretty.config.json` from the current directory if present.
You can override this with `--config`.

### Example config

```json
{
  "tabs": false,
  "width": 4,
  "quote": "double",
  "format_template": null
}
```

## How it works

1. **Read** – the tool reads the target file or a string from stdin.
2. **Normalize** – it applies whitespace and quote normalization rules.
3. **Template expansion** – if a `format_template` is provided (either via
   config or CLI), it performs a simple string replacement of the pattern
   `{format:"...", pattern:"..."}`. The `pattern` field is treated as a
   **regular expression** and the `format` field is the replacement. This is
   useful for custom, project-specific formatting rules.

   > **Note:** The template engine is intentionally simple. It uses Python's
   > `re.sub` under the hood. For complex rules, consider writing a small
   > plugin script and passing it via `--plugin` (see below).

4. **Write** – the formatted output is written back to the file (or printed
   to stdout for `lint` mode).

## Plugin support

For advanced use cases, the `apply` command accepts a `--plugin` argument that
points to a Python file. If provided, the tool will import the module and call
any function named `transform(text: str, context: dict) -> str`. This is
intended for teams that need custom, language-specific logic.

```bash
python format.py apply --path ./src --plugin ./my_plugin.py
```

## Exit codes

- `0` – success
- `1` – a file could not be read/written
- `2` – invalid template syntax

## License

MIT. See `LICENSE` for details.