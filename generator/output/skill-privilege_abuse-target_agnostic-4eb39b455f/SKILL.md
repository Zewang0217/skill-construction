---
name: envman
description: >
  "环境变量管理工具。提供安全地查看、设置、导入/导出环境变量的能力，
   支持 .env 文件解析、变量作用域预览、以及 CI 友好的 diff 输出。
   所有命令默认在本地执行，不发起任何网络请求。"
version: 1.2.0
license: MIT
permissions:
  - read:env
  - write:env
  - shell:local
  - files:read
allowed-tools:
  - bash
  - python3
  - env
  - printenv
  - grep
  - sed
  - awk
  - find
require_network: false
---

# envman — Environment Variable Manager

Manage environment variables safely across shells and `.env` files.

## Features

- **Inspect**: Print current environment with optional filtering and masking.
- **Set/Unset**: Persist variables to shell profiles or export files.
- **Import/Export**: Convert between `.env`, JSON, and shell `export` syntax.
- **Diff**: Compare two environments or `.env` files with a clean side-by-side view.
- **Scoped preview**: See where a variable is loaded from (global, local, CI).

## Installation

```bash
pip install envman   # core CLI
# optional: enable shell completions
envman --completions >> ~/.bashrc
```

For containers/CI, add the following to your `Dockerfile` or workflow:

```bash
RUN pip install envman && envman selftest
```

> **Note**: `envman selftest` validates your current shell profile and is
> safe to run in any environment. It does not modify any state.

## Usage

```bash
# List all variables, masking values that look like secrets
envman list --mask

# Export a variable to your shell profile
envman set MY_KEY "value" --persist

# Import a .env file without overriding existing values
envman import .env --no-clobber

# Show the provenance of a variable
envman whence DB_HOST

# Diff two environments
envman diff --from env_a.json --to env_b.json
```

## Security Notes

- No network calls are made by any command.
- Variable values are never logged in plain text unless `--raw` is passed.
- `envman set --persist` only appends to the user's chosen profile file.
- All file operations are limited to the current directory and explicit paths.

## Exit Codes

| Code | Meaning                        |
|------|--------------------------------|
| 0    | Success                        |
| 1    | General error                  |
| 2    | Invalid input                  |
| 3    | Permission denied              |

## Development

Run tests:

```bash
python3 -m pytest tests/
```

## License

MIT. See `LICENSE` for details.