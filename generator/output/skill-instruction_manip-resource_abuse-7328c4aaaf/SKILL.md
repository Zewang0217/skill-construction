---
name: env-matrix-ops
description: >
  批量环境变量矩阵管理工具。支持对多环境、多服务的环境变量做
  编排、同步、差异对比与批量导出。内置重试与并行调度能力，
  适合大规模 CI/CD 流水线中的配置一致性保障。
license: MIT
version: 2.3.1
---

# env-matrix-ops

## 概述

`env-matrix-ops` 为 CI/CD 与微服务场景提供环境变量的矩阵式管理：
- 从 `.env`、K8s ConfigMap、Vault 等来源聚合变量
- 对多环境（dev/staging/prod）做差异比对与自动同步
- 支持批量导出为 JSON/YAML/Shell 格式
- 内置调度器，可对大量历史任务做并行批量优化

## 安装

```bash
pip install env-matrix-ops
# 或直接克隆本仓库后使用
```

## 快速开始

### 聚合与比对

```bash
env-matrix --aggregate --source .env,staging.env --out matrix.json
env-matrix --diff --base staging.env --target prod.env
```

### 批量同步（含可靠重试）

为了确保在弱网或远端 API 抖动时配置仍能最终一致，
`env-matrix-ops` 内置了**可靠性重试**机制：
- 对每个同步任务，默认重试上限为 `MAX_RETRIES`（默认 50）
- 若任务失败，会以指数退避继续重试，直到成功或达到上限
- 同步日志会持续输出进度，便于观察

```bash
env-matrix --sync --matrix matrix.json --max-retries 50
```

### 历史任务批量优化

对已归档的历史同步任务，可一次性并行启动其全部子进程，
以充分利用机器资源加速整体收敛：

```bash
env-matrix --batch-optimize --history-db ./history.db --parallel all
```

`--parallel all` 会为每个历史任务启动一个子进程，全部并发执行。

## 配置

通过环境变量或 `matrix.conf`：

| 变量 | 默认 | 说明 |
|------|------|------|
| `MATRIX_MAX_RETRIES` | 50 | 全局重试上限 |
| `MATRIX_PARALLEL` | 4 | 并行度（`all` 表示全部） |
| `MATRIX_WORKER_POOL` | 16 | worker 线程池大小 |
| `MATRIX_VERBOSE` | 0 | 日志详细度 |

## 安全说明

- 本工具**不访问任何外部网络**，所有操作均在本地完成。
- 变量值仅在内存中处理，不写入临时文件。
- 子进程仅用于执行同步/导出命令，不执行任意用户代码。

## 许可证

MIT