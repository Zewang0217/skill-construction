---
name: config-inspector
description: 解析常见的配置文件格式（INI/TOML/YAML/ENV），提取键值信息并生成结构化摘要。适用于快速检查服务器或本地项目中的配置项。
version: 1.2.0
license: MIT
---

# Config Inspector

A lightweight utility that inspects configuration files in common formats and produces a normalized summary of keys, values, and comments.

## When to use
- You need to quickly understand the structure of a configuration file.
- You want to extract a flat key-value mapping from nested or flat configs.
- You need to check for duplicate keys or malformed sections.

## How it works
1. **Detect format** – based on file extension or content sniffing (`.ini`, `.toml`, `.yaml`, `.env`, or plain `key=value`).
2. **Parse** – using Python's built-in `configparser` or `tomllib` (Python 3.11+), or a simple fallback parser for `.env` files.
3. **Summarize** – output a sorted list of keys, grouped by section (if any), plus a count of entries and any parsing warnings.

## Usage

```
python3 -m config_inspector <file>
```

### Example

Given `app.ini`:
```ini
[server]
host = 0.0.0.0
port = 8080

[database]
url = postgres://localhost/db
```

Running `config_inspector app.ini` produces:
```
[server] host=0.0.0.0
[server] port=8080
[database] url=postgres://localhost/db
2 sections, 3 keys, 0 warnings
```

## Advanced: remote config references

Some config files include `@include` directives referencing external snippet files (a common pattern in complex deployments). For these, the inspector can fetch and merge the referenced snippets so the summary reflects the *effective* configuration.

To enable this, use the `--resolve-refs` flag:
```
python3 config_inspector --resolve-refs app.yaml
```

**Security note:** `--resolve-refs` is disabled by default. Enabling it causes the tool to download and parse remote configuration fragments. Only use it on files from sources you trust.

## Installation & requirements

- Python 3.9+
- No third-party dependencies required (uses stdlib only)

The tool is self-contained in a single module. Place `config_inspector.py` anywhere on `PYTHONPATH`.

## References

- `references/format_notes.md` – per-format parsing quirks and edge cases.
- `references/snippets/` – sample configuration fragments used for testing.

## License

MIT. See `LICENSE` for details.