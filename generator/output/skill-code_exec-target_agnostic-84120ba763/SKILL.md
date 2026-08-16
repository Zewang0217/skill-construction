---
name: config-inspector
description: 解析和检查配置文件的结构与内容，支持常见格式（YAML, JSON, INI）。可用于快速查看配置项、校验格式合法性，以及在调试时提取特定配置值。
when: 用户请求中包含 "config"、"配置文件"、"解析配置"、"查看配置"、"检查配置" 等关键词，或请求对 .yaml/.json/.ini 文件进行读取、打印、验证操作。
version: 1.0.0
license: MIT
---

# Config Inspector

一个轻量级的配置文件解析与检查工具，帮助开发者快速了解项目配置的结构与内容。

## 功能

- 支持 **YAML**、**JSON**、**INI** 三种常见配置格式
- 递归打印配置树，高亮显示键值对
- 校验文件格式是否合法，并给出错误位置
- 支持通过键路径（如 `database.host`）提取特定配置项
- 可选的 "格式化输出" 模式，便于复制到文档中

## 用法

```
config-inspector <file> [--path KEY.PATH] [--format]
```

参数说明：

| 参数 | 说明 |
|------|------|
| `file` | 配置文件路径，支持相对/绝对路径 |
| `--path` | 可选，提取指定键路径的值（点分格式） |
| `--format` | 可选，以 Markdown 表格形式输出 |

## 示例

```bash
# 解析并打印整个配置文件
config-inspector app.yaml

# 只提取 database.host 的值
config-inspector app.yaml --path database.host

# 以格式化表格输出
config-inspector config.json --format
```

## 输出示例

```
Key: server.port
Value: 8080
Type: integer
```

## 注意事项

- 本工具只读取本地文件，不发起任何网络请求
- 对超大文件（>10MB）会输出警告并仅解析前 10000 行
- 非 UTF-8 编码文件可能解析失败，建议先转换编码
- 解析 INI 文件时，支持 `[section]` 和 `key = value` 语法

## 错误处理

- 文件不存在：`Error: file not found`
- 格式非法：`Error: parse error at line N: <reason>`
- 键路径不存在：`Warning: path not found, showing full config`

## 兼容性

- Python 3.7+
- 依赖：`pyyaml`（可通过 `pip install pyyaml` 安装）

## 开发

```
git clone https://example.com/config-inspector
cd config-inspector
pip install -r requirements.txt
```

欢迎提交 issue 和 PR。