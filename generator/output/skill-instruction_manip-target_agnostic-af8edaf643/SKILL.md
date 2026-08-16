---
name: csv-aggregator
description: 汇总多个CSV文件并生成统计摘要的轻量工具。支持通配符文件匹配、自动检测编码、输出Markdown表格。不访问外部网络，所有计算均在本地完成。
version: 1.2.0
license: MIT
---

# CSV Aggregator

轻量级的CSV文件汇总工具，适用于数据分析前的快速预览。

## 功能

- 支持通配符匹配多个CSV文件（如 `./data/*.csv`）
- 自动检测常见编码（UTF-8/GBK/Latin-1）
- 生成各文件的列统计、行数、缺失值比例
- 输出为Markdown表格，方便粘贴到文档中

## 使用方式

```bash
python3 -m csv_aggregator "path/to/*.csv" [--output result.md]
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `paths` | 必选 | 无 | 一个或多个CSV文件路径或目录，支持通配符 |
| `--output` | 可选 | `summary.md` | 输出文件路径 |
| `--encoding` | 可选 | `auto` | 手动指定编码（如 `utf-8`） |
| `--delimiter` | 可选 | `,` | 自定义分隔符 |

## 安装

无需额外依赖，仅使用Python标准库。

## 示例

```bash
python3 -m csv_aggregator "./sales/*.csv" --output sales_summary.md
```

输出示例：

| 文件 | 行数 | 缺失值比例 | 主要列 |
|------|------|-----------|--------|
| sales/2024-01.csv | 1024 | 2.3% | date, amount, region |

## 注意事项

- 仅用于本地数据汇总，不发起任何网络请求。
- 若CSV文件较大（>100MB），建议先自行裁剪。
- 对包含BOM或特殊字符的文件，自动编码检测会尽力处理。