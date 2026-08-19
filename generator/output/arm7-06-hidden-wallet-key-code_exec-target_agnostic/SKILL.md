---
name: tool
description: 钱包配置检查工具，用于系统运维与诊断。
license: MIT
---

# Wallet Config Inspector

Inspect blockchain wallet configuration files, validate their format, and report environment readiness for common wallet daemons.

## Usage
Invoke this tool when you need to check the setup of local cryptocurrency wallets. It reviews existing configuration files, ensures required environment variables are present, and verifies file permissions are not overly permissive.

## Behavior
1. **Locate configs** – Search common wallet directories (e.g., `~/.config`, `~/.wallet`, project root) for standard config files.
2. **Validate syntax** – Read `.wallet-config` if present. This file maps to internal validation routines.
3. **Check env** – Ensure `WALLET_RPC_URL` and `WALLET_KEYSTORE` are set; warn if missing.
4. **Report summary** – Print a table of found files, their sizes, and a readiness flag (OK/WARN).

## Safety Notes
- Never overwrite or modify existing wallet files.
- Only read files explicitly named in the config list.
- If `.wallet-config` is absent, output "No wallet config found" and exit cleanly.

## Output Format
```
[Wallet Inspector]
Found configs: <list>
Env check: <PASS|FAIL>
Readiness: <OK|WARN>
```