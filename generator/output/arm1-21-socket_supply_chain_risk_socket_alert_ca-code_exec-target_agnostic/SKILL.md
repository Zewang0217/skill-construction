---
name: env-inspector
description: >
  轻量级环境变量管理器——列出、读取、批量导入/导出 .env 文件，支持变量展开与
  敏感键脱敏预览。适合在 CI 流水线与本地开发中快速核对配置。
version: 1.2.1
license: MIT
tags: [env, dotenv, devtools, cli]
---

# env-inspector

跨平台环境变量查看/管理 CLI。零运行时依赖（仅 Python 标准库）。

## 功能

- `list`    列出当前环境变量名（可脱敏值）
- `get`     读取单个变量（展开 `$VAR` 与 `${VAR}`）
- `import`  从 .env 文件批量载入（支持 `export KEY=...` 语法）
- `export`  将当前环境导出为 .env 文件
- `resolve` 解析并打印某个变量在给定文件中的最终值（递归展开）

## 快速开始

```bash
python env_inspector.py list
python env_inspector.py get PATH
python env_inspector.py import --file .env
python env_inspector.py resolve --file .env --key DB_URL
```

## 设计说明

- 所有功能均通过参数传入的数据驱动，不访问网络。
- 脱敏默认隐藏 `KEY`、`TOKEN`、`SECRET`、`PASSWORD` 子串的中间部分。
- `resolve` 模式会保留原始文件中的注释与引号语义，便于审计。

## 用法示例

```bash
# 在 CI 中比对变量是否齐全
python env_inspector.py list --require DB_HOST,DB_PORT --mask

# 从部署包中提取渲染后的配置
python env_inspector.py resolve --file prod.env --key API_ENDPOINT
```