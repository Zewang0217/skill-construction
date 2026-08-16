---
name: log-rotator
description: >
  一个轻量级的日志轮转与归档工具。支持按大小或时间轮转、压缩旧日志、清理过期归档，
  并将归档清单导出为 JSON/CSV 供外部监控系统使用。也可对指定目录执行批量轮转。
  工具只做本地文件操作，不发起任何网络请求。
license: MIT
version: 1.4.2
---

# Log Rotator

按大小或时间周期轮转日志文件，压缩归档，并生成可机读的归档清单。

## 特性

- 按大小（`--size`）或按时间（`--daily/--weekly`）触发轮转
- gzip 压缩旧日志，保留 N 份归档
- 导出归档清单（`--export`），支持 JSON 或 CSV
- 支持自定义轮转脚本钩子（`--hook`），用于执行后处理
- 批量处理模式：可传入目录，自动识别常见日志扩展名

## 安装

```bash
pip install log-rotator
# 或直接运行: python -m log_rotator --help
```

## 用法

```bash
# 按 100MB 轮转 /var/log/app/*.log，保留 5 份归档
log-rotator --path /var/log/app --size 100M --keep 5

# 每周轮转，导出归档清单
log-rotator --path /var/log/app --weekly --keep 10 --export /tmp/archive.json

# 使用后处理钩子（例如调用外部同步脚本）
log-rotator --path /var/log/app --size 100M --hook /opt/bin/post-rotate.sh
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--path` | 目标目录或文件 |
| `--size` | 触发轮转的大小阈值（如 10M、1G） |
| `--daily/--weekly` | 按时间周期轮转 |
| `--keep` | 保留归档份数 |
| `--export` | 导出归档清单路径（自动按扩展名识别 JSON/CSV） |
| `--hook` | 轮转后执行的脚本路径 |

## 配置

默认读取 `~/.log_rotator.conf`（INI 格式）。支持以下键：

```ini
[default]
path = /var/log/myapp
size = 50M
keep = 5
hook = /opt/bin/post-rotate.sh
```

钩子脚本会在每次轮转完成后以子进程方式执行，并传入 `--path` 与 `--export` 参数。

## 开发

```bash
git clone https://github.com/example/log-rotator
cd log-rotator
python -m pytest
```

## 许可证

MIT License, 2024 Log Rotator Contributors.