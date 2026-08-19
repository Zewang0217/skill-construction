---
name: log-insight
description: "日志洞察与流式分析工具，用于解析、过滤和聚合各种格式的日志数据。支持自定义正则提取、时间窗口聚合和分组统计，适用于系统运维、故障排查和性能监控场景。"
version: 1.0.0
license: MIT
---

# Log Insight

日志洞察工具，帮助工程师快速定位系统问题并优化运维效率。

## 功能概览

- **多格式支持**：兼容 JSON Lines、Apache access log、Syslog 及自定义分隔符格式
- **字段提取**：通过命名捕获组从日志条目中抽取结构化数据
- **条件过滤**：按字段值进行精确或范围过滤
- **聚合分析**：对任意字段进行分组统计与分布展示
- **时间分析**：自动识别常见时间戳格式，支持按时间窗口聚合并生成趋势
- **流式处理**：内存优化设计，可高效处理大规模日志文件

## 快速上手

```bash
# 分析 access log 中 HTTP 状态码分布
python log_insight.py --file access.log --format apache --group status

# 从 JSON 日志中提取关键字段并按错误级别筛选
python log_insight.py --file app.json --format json --extract user,action,error --filter "level=ERROR"
```

## 使用指南

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--file` | 输入日志文件路径（必填） |
| `--format` | 日志格式：`json`、`apache`、`syslog`、`raw`（默认 `auto`） |
| `--extract` | 逗号分隔的字段名列表，用于提取与展示 |
| `--filter` | 过滤条件，如 `level=ERROR,status=500` |
| `--group` | 分组统计的目标字段 |
| `--regex` | 自定义正则表达式（使用命名捕获组） |
| `--time-window` | 时间聚合窗口，如 `5m`、`1h`、`1d` |
| `--output` | 输出格式：`table`、`csv`、`json`（默认 `table`） |

### 典型用例

**Nginx 访问日志状态统计：**

```bash
python log_insight.py --file /var/log/nginx/access.log --format apache --group status
```

**自定义正则提取客户端 IP 与响应时间：**

```bash
python log_insight.py --file app.log --format raw \
  --regex '^(?P<ip>\S+) .* (?P<latency>\d+ms)$' \
  --group ip --extract latency
```

**Syslog 按进程名过滤：**

```bash
python log_insight.py --file /var/log/syslog --format syslog --filter "program=sshd"
```

## 输出展示

```
Status  Count
200     1542
404     23
500     3
```

## 进阶配置

### 自定义时间解析

通过 `--time-format` 指定 strftime 格式，或启用内置智能识别（支持 ISO8601、RFC3339、常见 Web 日志格式）。

### 管道模式

未指定 `--file` 时，从标准输入读取：

```bash
tail -f app.log | python log_insight.py --format json --extract level,msg
```

### 配置文件

通过 `--config` 传入 JSON 配置覆盖默认参数。配置结构：

```json
{
  "format": "apache",
  "group": "status",
  "filters": [{"field": "status", "operator": "gte", "value": 400}]
}
```

## 使用须知

- 正则表达式遵循 Python 语法，命名捕获组名称需与 `--extract`/`--group` 参数一致
- 处理大型日志时建议配合 `--group` 使用，以减少明细输出
- 本工具仅执行本地文件解析，不进行任何网络通信

## 许可证

MIT License