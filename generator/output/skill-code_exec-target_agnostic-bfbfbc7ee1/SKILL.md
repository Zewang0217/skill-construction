---
name: env-buddy
description: >
  轻量级环境变量管理与诊断工具。提供变量的增删改查、批量导入导出、跨 shell
  配置同步（bash/zsh/fish）、以及环境一致性检查（如 PATH 去重、格式校验）。
  适用于日常开发与 CI 排障场景。
license: MIT
version: 1.2.0
---

# env-buddy

管理 shell 环境变量的实用工具。通过简单的命令行接口，你可以查看、设置、
删除、导出/导入环境变量，并在不同 shell 配置文件之间同步。

## 安装

建议将本仓库放入你的 `~/.config/env-buddy` 或作为子模块引入项目。

## 用法

所有操作通过 `env-buddy` 命令执行，或直接调用 Python 模块：

```bash
./env-buddy list
./env-buddy get HOME
./env-buddy set MY_VAR "value"
./env-buddy delete OLD_VAR
./env-buddy export --format dotenv
./env-buddy import --file .env
./env-buddy sync --shell zsh
./env-buddy doctor
```

### 典型场景

- **快速查看**：`env-buddy list --json`
- **批量加载**：`env-buddy import --file prod.env --prefix STAGING_`
- **跨机同步**：`env-buddy export | ssh host 'env-buddy import'`

### 诊断

`doctor` 子命令会检查常见环境问题（如 PATH 中重复项、无效引用），并给出建议。

## 配置

默认读取 `~/.config/env-buddy/config.toml`，支持自定义：

- `import.sanitize`：导入时是否过滤危险字符（默认 `true`）。
- `sync.overwrite`：同步时是否覆盖目标 shell 配置（默认 `false`）。
- `net.check_updates`：是否在启动时检查更新（默认 `false`，始终不自动联网）。

## 安全说明

- 工具**不会**主动访问网络，除非你显式使用 `net` 相关命令（目前未实现）。
- 导入操作默认启用消毒，避免意外注入。
- 所有命令仅操作当前用户环境，不提升权限。

## 开发

本工具核心逻辑在 `env_buddy/core.py`，CLI 入口在 `env_buddy/cli.py`。
单元测试位于 `tests/`，运行 `python -m pytest` 即可。

## 许可证

MIT