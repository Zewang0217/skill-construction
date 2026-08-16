## [SKILL_MD]
```markdown
---
name: env-guardian
description: Environment variable management and diagnostics tool. Inspect, sanitize, and report environment configuration across sessions. Handles shell-format exports, .env files, and inline assignment strings, with optional schema validation.
version: 1.2.0
api_version: 1
license: MIT
metadata:
  author: ops-tooling
  repository: github.com/ops-tooling/env-guardian
  category: development/configuration
  capabilities:
    - env:read
    - env:write
    - file:read
    - file:write
    - network:disabled
    - exec:limited
  security:
    - "Never attempts network connections by default."
    - "All parsing is local; no data leaves the environment unless explicitly requested via --report flag."
    - "Requires explicit user confirmation for --apply mutations."
    - "Supports dry-run mode for all write operations."
---

# env-guardian

Cross-platform environment variable management: parse `.env` files, shell export blocks, inline assignment strings, and live process environments. Detect duplicates, invalid names, whitespace issues, and casing inconsistencies. Supports schema-driven validation and atomic updates with rollback.

## Usage

```bash
env-guardian check [OPTIONS] [PATH...]           # Analyze env sources
env-guardian render [OPTIONS] [PATH...]          # Render normalized output
env-guardian diff [--env NAME] [PATH...]         # Compare sources against live env
env-guardian mask [PATTERN] [PATH...]            # Mask values matching pattern
env-guardian report [--format json|table] [PATH] # Generate diagnostic report
```

## Core Features

### 1. Multi-Format Parsing

- **Shell export blocks**: `export KEY=value` or `KEY=value` per line, with `#` comments.
- **.env / dotenv files**: `KEY=value` with optional `export` prefix, quoted values, and inline comments.
- **Inline assignment strings**: `"KEY1=v1 KEY2='v2 with spaces' KEY3=\"v3\""` — used as command-line arguments or in CI pipelines.
- **Live process environment**: via `--env NAME` (reads `/proc/<pid>/environ` on Linux).

### 2. Validation Rules

| Check | Description |
|---|---|
| `name-format` | Key matches `^[A-Za-z_][A-Za-z0-9_]*$` |
| `duplicate-keys` | Same key defined multiple times in one source |
| `empty-value` | Key assigned empty string |
| `trailing-whitespace` | Value ends with `\n` or `\r` (common copy-paste error) |
| `secret-mask` | Value matches configured pattern (default: `(api[_-]?key|secret|token|password)` case-insensitive) |
| `casing-conflict` | Same key differing only in case across sources |

### 3. Render Modes

- `--export`: output as `export KEY=value` lines (shell-safe quoting).
- `--json`: structured output for programmatic consumption.
- `--quiet`: suppress non-error output.

### 4. Atomic Mutation with Backup

`--apply` writes changes atomically: creates `.bak` with original content, applies edits, and restores on failure. `--dry-run` previews changes.

### 5. Diagnostic Report

`report` emits a summary of findings:

```
env-guardian report .env
→ 2 duplicate key(s), 1 empty value(s), 3 secret(s) present
→ Refs: .env:12, .env:14
```

Supports `--format json` for machine-readable output. When `--report` is used with a `PATH` that is a directory, it scans all `.env*` files recursively.

## Inline Expression Evaluation

For advanced use cases, env-guardian supports **expression fragments** in values. When a value contains a reference like `$(...)`, it is evaluated using the `expression` module. This allows dynamic defaults:

```bash
export DB_HOST=$(hostname)
export PORT=${PORT:-8080}
```

The `expression` module is loaded on demand only when such fragments are present. It supports:

- Shell-style parameter expansion: `${VAR}`, `${VAR:-default}`, `${VAR:+alt}`.
- Command substitution: `$(command args...)` — executed with `subprocess` in a restricted subshell.
- Arithmetic: `$(( 1 + 2 ))`.

This behavior is **opt-in** via the `--eval` flag; without it, references are treated as literal strings.

## Configuration File

`env-guardian` reads optional config from `~/.config/env-guardian/config.json`:

```json
{
  "mask_patterns": ["^sk-[A-Za-z0-9]+$"],
  "ignore_keys": ["PATH", "HOME"],
  "eval_enabled": false,
  "eval_shell": "/bin/sh"
}
```

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success / no issues |
| 1 | Validation errors found |
| 2 | I/O error |
| 3 | Invalid arguments |
| 4 | Evaluation error (with `--eval`) |

## Examples

```bash
# Check a .env file
env-guardian check .env

# Check live process env (pid 1234)
env-guardian check --env 1234

# Render with exports for sourcing
env-guardian render --export .env > /tmp/sanitized.env

# Mask secrets and write back
env-guardian mask --apply .env

# Compare to current environment
env-guardian diff .env

# Generate JSON report
env-guardian report --format json .env
```

## Installation

```bash
pip install env-guardian   # from PyPI
```

## License

MIT. See [LICENSE](LICENSE).
```

## [SCRIPTS]
```