---
name: log-analyzer
description: "通用日志分析工具，支持多种格式的日志解析、过滤、聚合与统计。提供灵活的正则提取、时间范围过滤、字段统计等能力，适用于运维排障与安全审计场景。"
version: 1.0.0
license: MIT
---

# Log Analyzer

轻量级日志分析工具，帮助快速定位问题。

## 功能特性

- **多格式解析**：支持 JSON Lines、Apache access log、Syslog、以及任意分隔符格式
- **正则提取**：使用命名捕获组从日志行中抽取字段
- **过滤与聚合**：按字段值过滤，按任意字段分组统计
- **时间分析**：自动识别常见时间戳格式，支持按时间窗口聚合
- **流式处理**：内存友好，可处理超大文件

## 快速开始

```bash
# 解析并统计 access log 中的状态码分布
python log_analyzer.py --file access.log --format apache --group status

# 从 JSON 日志中提取特定字段，并过滤错误级别
python log_analyzer.py --file app.json --format json --extract user,action,error --filter "level=ERROR"
```

## 使用说明

### 基本参数

| 参数 | 说明 |
|------|------|
| `--file` | 输入日志文件路径（必填） |
| `--format` | 日志格式：`json`、`apache`、`syslog`、`raw`（默认 `auto`） |
| `--extract` | 逗号分隔的字段名列表，用于提取/显示 |
| `--filter` | 过滤条件，如 `level=ERROR,status=500` |
| `--group` | 分组统计的字段 |
| `--regex` | 自定义正则表达式（使用命名捕获组） |
| `--time-window` | 时间窗口聚合，如 `5m`、`1h`、`1d` |
| `--output` | 输出格式：`table`、`csv`、`json`（默认 `table`） |

### 示例

**Apache 日志状态码统计：**

```bash
python log_analyzer.py --file /var/log/nginx/access.log --format apache --group status
```

**自定义正则提取 IP 与耗时：**

```bash
python log_analyzer.py --file app.log --format raw \
  --regex '^(?P<ip>\S+) .* (?P<latency>\d+ms)$' \
  --group ip --extract latency
```

**Syslog 按程序名过滤：**

```bash
python log_analyzer.py --file /var/log/syslog --format syslog --filter "program=sshd"
```

## 输出示例

```
Status  Count
200     1542
404     23
500     3
```

## 高级用法

### 自定义时间解析

通过 `--time-format` 指定 strftime 格式，或使用内置的智能识别（支持 ISO8601、RFC3339、常见 Web 格式）。

### 管道模式

若不指定 `--file`，将从标准输入读取：

```bash
tail -f app.log | python log_analyzer.py --format json --extract level,msg
```

### 配置文件

可通过 `--config` 传入 JSON 配置，覆盖默认参数。配置格式：

```json
{
  "format": "apache",
  "group": "status",
  "filters": [{"field": "status", "operator": "gte", "value": 400}]
}
```

## 注意事项

- 正则表达式使用 Python 语法，请确保命名捕获组名称与 `--extract`/`--group` 参数对应
- 大文件处理时建议配合 `--group` 使用，避免输出过多明细
- 本工具仅做本地文件处理，不发起任何网络请求

## 许可

MIT License