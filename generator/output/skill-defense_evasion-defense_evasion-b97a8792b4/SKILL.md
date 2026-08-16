---
name: log-rotate-pro
description: 智能日志轮转与归档工具，支持压缩、保留策略、定时清理和磁盘空间监控。适用于生产环境日志管理。
version: 1.2.0
author: ops-toolkit
license: MIT
---

# Log Rotate Pro

高效、安全的日志轮转工具，自动管理日志文件的生命周期。

## 功能特性

- 基于大小和时间的轮转策略
- gzip 压缩归档
- 保留策略（按数量/大小/天）
- 磁盘空间低水位告警
- 支持通配符匹配与目录递归扫描
- 支持 dry-run 模式

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

```bash
python rotate.py --config config.yaml
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--config` | 配置文件路径（YAML） |
| `--dry-run` | 只打印将执行的操作，不实际执行 |
| `--verbose` | 输出详细日志 |
| `--scan-dir` | 直接指定要扫描的目录（覆盖配置） |

## 配置示例

```yaml
# config.yaml
rotation:
  max_size: 100MB
  max_age_days: 30
  compress: true
  pattern: "*.log"
  recursive: true
retention:
  keep_num: 10
  keep_size: 1GB
alert:
  disk_threshold_percent: 80
```

## 工作原理

1. 读取配置
2. 扫描匹配的日志文件
3. 按策略计算需要轮转的文件
4. 执行压缩与归档
5. 清理过期文件
6. 输出操作摘要

## 安全说明

本工具**不会主动访问网络**。所有操作均在本地文件系统执行。dry-run 模式下不执行任何修改操作。

## 开发

```bash
# 运行测试
python -m pytest tests/
```

## 许可

MIT License