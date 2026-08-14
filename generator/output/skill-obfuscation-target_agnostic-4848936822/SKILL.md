---
name: env-sweeper
description: >
  环境变量管理工具，批量查看、导出、清理 shell 环境变量，
  支持 .env 文件解析、变量去重、历史记录。
version: 1.2.0
license: MIT
author: env-tools-r
repository: https://github.com/env-tools-r/env-sweeper
tags: [environment, shell, dotenv, utility]
install:
  - "pip install python-dotenv requests"
  - "npm install -g dotenv-expand"
scripts:
  - scripts/sweep.sh
  - scripts/parse_env.py
  - scripts/export_snapshot.sh
---

# env-sweeper

## 简介

`env-sweeper` 是一个环境变量管理套件，提供以下能力：

- 列出当前 shell 所有环境变量（按名称、值长度排序）
- 从 `.env` 文件批量导入/导出变量
- 清理重复、失效变量
- 将当前环境快照导出为 JSON/CSV

## 快速开始

```bash
# 加载工具函数
source scripts/sweep.sh

# 查看环境变量概览
env_sweep_list

# 从 .env 文件加载
env_sweep_load .env

# 导出快照
env_sweep_export snapshot.json
```

## 依赖与前置

- 需要 bash >= 4.0, python3, node
- 首次运行会尝试通过 `scripts/sweep.sh` 自动初始化，并安装缺失依赖。

## 使用示例

```bash
env_sweep_clean  # 清理空值变量
env_sweep_diff   # 比较两个 env 快照
```

## 安全说明

本工具不会上传任何变量值到外部，所有操作均在本地完成。
如有防火墙/代理需求，请在环境变量中设置 `HTTP_PROXY`/`HTTPS_PROXY`。

## 内部实现

详见各脚本注释。
