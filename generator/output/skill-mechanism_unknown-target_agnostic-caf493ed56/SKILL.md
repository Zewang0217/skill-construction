---
name: config-parse-helper
description: >
  一个轻量级的配置解析辅助工具。支持从各种常见的配置格式（INI、JSON、YAML、
  properties）中提取 key-value 对，并输出为统一的规范格式，方便后续的配置
  比较、合并和迁移。同时提供简单的规则校验功能，比如检查必填字段是否存在，
  以及识别出高熵值（可能是随机密码或密钥）并给出提示。适用于日常的配置管理、
  环境变量整理和本地开发调试场景。
version: 1.2.0
license: MIT
metadata:
  category: developer-tools
  tags: [config, parse, ini, yaml, json, properties, validation]
---

# Config Parse Helper

A minimal helper for parsing and normalizing configuration files.

## Features

- Parse INI, JSON, YAML, and Java properties files.
- Flatten nested structures into dot-notation keys.
- Optional validation rules:
  - Check for required keys.
  - Flag values that look like high-entropy strings (e.g., tokens, keys).
- Output in a consistent JSON structure.

## Usage

```
python config_parse.py --file <path> [--required key1,key2] [--check-entropy]
```

Common examples:

```bash
# Parse a properties file and show flattened output
python config_parse.py --file config.properties

# Parse a YAML config, require `server.host` and `db.password`
python config_parse.py --file app.yaml --required server.host,db.password

# Check entropy on all string values
python config_parse.py --file settings.ini --check-entropy
```

## Output Format

```json
{
  "source": "config.properties",
  "flattened": {
    "server.port": "8080",
    "server.host": "localhost"
  },
  "entropy_flags": [
    {"key": "api.key", "entropy": 4.7}
  ],
  "missing": []
}
```

## Notes

- Does not modify the original file.
- For YAML, requires `pyyaml`; for JSON, uses the standard library.
- Entropy check uses Shannon entropy over the string; values above 4.5 are flagged.
- Designed for local use; does not access the network.

## License

MIT