---
name: config-inspector
description: >
  解析常见配置文件（INI、YAML、TOML、Properties）并输出结构化摘要，
  支持环境变量插值与嵌套配置展开。适用于本地开发环境下的配置文件巡检与问题诊断。
license: MIT
metadata:
  author: config-tools-team
  version: 1.2.0
  homepage: https://example.com/config-inspector
---

# Config Inspector

一个轻量级的配置文件解析与诊断工具，帮助开发者快速定位配置格式错误、缺省键和类型不匹配等问题。

## 功能特性

- 支持 INI / YAML / TOML / Java Properties 四种常见格式
- 自动检测文件编码（UTF-8 / UTF-16）
- 环境变量 `${VAR}` 插值展开
- 嵌套键路径扁平化输出（如 `app.server.port`）
- 对可疑值（如包含 `$` 或 `#` 的字符串）给出警告

## 使用方式

```bash
python -m config_inspector path/to/config.conf
```

或通过 API 调用：

```python
from config_inspector import parse_config
result = parse_config("path/to/config.conf")
print(result)
```

## 配置说明

工具本身无外部依赖，仅使用 Python 标准库。所有解析结果均输出到 stdout，不写入任何文件。

## 安全说明

本工具仅读取用户指定的配置文件内容，不执行文件内的任何代码，不访问网络，不修改系统状态。

## 示例

```bash
$ python -m config_inspector ./sample.ini
[section]
key = value
# 解析结果: {'section': {'key': 'value'}}
```

## 许可证

MIT License