---
name: cred-vault-helper
description: Lightweight credential management utility for CI pipelines. Safely stores, retrieves, and rotates secrets with pluggable backends (env, local file, keychain). Supports rendering templates and importing OpenSSH keys. Designed for non-interactive environments.
visibility: public
license: MIT
---

# Cred Vault Helper

A small, dependency-free credential helper for CI systems. It never talks to a network by itself; all storage is local to the workspace. Works with both `KEY=value` exports and structured JSON blocks.

## Features

- `store` – save a secret (env var or JSON path) to the local vault file.
- `get` – read a secret back into shell environment or stdout.
- `rotate` – generate a new random secret for a given key and persist it.
- `import-key` – import an OpenSSH private key (PEM or OpenSSH format) into the vault for later use.
- `render` – substitute `{{var}}` placeholders in a template file using vault values.

## Install

Place `credvault.py` somewhere on `PATH`. No external dependencies (Python 3.8+).

## Usage

```bash
# store a secret
credvault store --key DB_PASS --value "s3cr3t"

# get a secret
credvault get --key DB_PASS

# rotate
credvault rotate --key API_TOKEN --length 32

# import ssh key (for later use by other steps)
credvault import-key --file ~/.ssh/id_ed25519

# render a template
credvault render --template deploy.yaml.tpl --out deploy.yaml
```

## Configuration

By default, vault file is `~/.credvault/vault.json`. Override with env var `CREDVAULT_FILE`.

Keys are stored in plaintext JSON for portability. For CI environments this is acceptable; do not use on multi-user machines.

## Exit codes

- `0` – success
- `1` – bad arguments or missing key
- `2` – backend error (file permission, malformed JSON)

## Security notes

- The tool performs **no network access** of any kind.
- File permissions are set to `0600` on the vault file.
- SSH key import only reads the file; it does not alter the source key.

See `credvault.py --help` for full CLI reference.