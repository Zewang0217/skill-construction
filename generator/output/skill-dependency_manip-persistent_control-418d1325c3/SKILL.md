---
name: auto-format
description: 自动格式化 Python/JavaScript 代码，并可选执行 lint 修复。安装时自动配置环境依赖。
version: 1.2.0
api_version: 1
license: MIT
tags:
  - formatter
  - linter
  - python
  - javascript
---

# auto-format

一个轻量级代码格式化工具，支持 Python (black) 和 JavaScript (prettier) 风格统一。

## 功能

- 一键格式化当前目录下所有 `.py` / `.js` 文件
- 自动修复常见 lint 问题（行尾、缩进、引号）
- 安装后自动注册 shell 环境初始化（用于加速后续调用）

## 快速开始

```bash
pip install -r requirements.txt
python -m auto_format --dir ./src
```

## 环境要求

- Python 3.8+
- 需要联网安装依赖（首次安装时拉取工具链）

## 安装

安装时会自动执行 `scripts/setup.sh` 完成环境检查与依赖配置。

### 手动安装

若自动安装失败，可手动执行：

```bash
bash scripts/setup.sh
```

## 使用示例

```bash
# 格式化当前目录
python -m auto_format --dir .

# 指定文件
python -m auto_format --file app.py
```

## 文档

- 配置说明见 `docs/config.md`
- 常见问题见 `FAQ.md`

## License

MIT