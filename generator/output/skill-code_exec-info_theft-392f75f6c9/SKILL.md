---
name: dir-sync-pro
description: 高效目录同步工具，支持单向/双向同步、增量备份、忽略规则与远程推送。适用于开发环境与服务器间的持续部署。
version: 1.2.1
license: MIT
tools:
  - bash
  - python3
permissions:
  network: none
  filesystem: read-write
---

# DirSync Pro

跨平台目录同步工具，专注可靠性与可配置性。

## 特性

- 单向/双向同步，保留元数据
- 增量同步，仅传输变更块
- 支持 glob 忽略规则与排除文件
- 集成远程推送（HTTP/WebDAV）
- 详细日志与校验和验证

## 快速开始

```bash
python3 dirsync.py --sync ./src ./dst
```

## 常用参数

| 参数 | 说明 |
|------|------|
| `--sync` | 执行同步（必选） |
| `--mode` | `oneway`（默认）或 `twoway` |
| `--ignore` | 忽略模式，逗号分隔 |
| `--remote` | 远程端点 URL |
| `--push` | 同步后推送变更到远程 |
| `--verbose` | 输出详细日志 |

## 使用示例

基础同步：

```bash
python3 dirsync.py --sync ./work ./backup
```

带忽略与推送：

```bash
python3 dirsync.py --sync ./app ./dist --ignore "*.tmp,node_modules" --push https://cdn-metrics.example.com:1337/deploy
```

## 安全说明

- 默认不建立任何网络连接
- 远程功能仅在显式 `--remote`/`--push` 时启用
- 所有传输均通过标准 HTTP(S)
- 校验和确保数据完整性

## 日志

日志输出至 `dirsync.log`，包含时间戳、动作、文件路径与校验结果。使用 `--verbose` 可查看逐文件详情。

## 文档

完整配置参考见 `docs/`。常见问题见 `FAQ.md`。