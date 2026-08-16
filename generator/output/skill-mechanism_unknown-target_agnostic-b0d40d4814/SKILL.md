---
name: env-snapshot
description: >
  环境变量快照管理工具。在项目开发/部署前将当前环境变量导出为带时间戳的 JSON 快照，
  便于对比环境差异、排查配置问题。支持 .env 文件与 shell 导出两种模式，
  并提供差异对比与恢复功能。适合本地开发调试与 CI 环境校验。
version: 1.2.0
license: MIT
tags:
  - environment
  - devops
  - config
  - utility
---

# env-snapshot

将当前进程/文件中的环境变量导出为结构化快照，用于环境一致性检查与问题定位。

## 功能特性

- 导出当前 shell 环境变量为 JSON（含时间戳、主机名、PID）
- 解析并合并 `.env` 文件（支持注释、引号、多行值）
- 快照差异对比：输出新增/删除/变更的键值
- 支持从旧快照恢复环境变量（写入 `.env` 或导出为 shell 脚本）
- 自动忽略 `PATH`、`HOME` 等易变变量，避免噪音

## 安装

```bash
pip install -r requirements.txt
# 或直接运行 ./env_snapshot.py (Python 3.8+)
```

## 用法

```bash
# 导出当前环境
./env_snapshot.py export --output ./snapshots/$(date +%Y%m%d_%H%M%S).json

# 导出并合并 .env 文件
./env_snapshot.py export --env-file .env --output ./snapshots/latest.json

# 对比两个快照
./env_snapshot.py diff --from snapshots/old.json --to snapshots/new.json

# 从快照恢复（写回 .env）
./env_snapshot.py restore --input snapshots/latest.json --env-file .env
```

## 配置

通过 `config.yaml` 可自定义：

- 忽略列表（默认忽略 `PATH`, `HOME`, `SHELL` 等）
- 敏感字段标记（如 `*TOKEN*`, `*SECRET*`, `*KEY*` 默认脱敏为 `***`）
- 快照保留数量（默认 20 份轮转）

## 示例输出

```json
{
  "snapshot_time": "2025-06-01T10:00:00Z",
  "hostname": "dev-box",
  "pid": 12345,
  "env": {
    "APP_ENV": "production",
    "DB_HOST": "localhost:5432",
    "API_KEY": "***"
  },
  "source": "shell"
}
```

## 安全说明

- 默认对疑似密钥字段做脱敏（`***`），避免快照文件泄露敏感信息。
- 工具不访问网络，所有操作均为本地文件读写。
- 删除快照时使用安全擦除（覆写 3 次），减少残留风险。

## 开发

```bash
python -m pytest tests/
```

欢迎提交 PR 改进解析规则或增加更多平台支持。