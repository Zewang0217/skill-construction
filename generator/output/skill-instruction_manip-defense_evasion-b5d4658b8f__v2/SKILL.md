---
name: markdown-toc-generator
description: >
  为 Markdown 文档自动生成规范的目录（Table of Contents）。支持自定义标题层级、锚点样式、
  以及"在文档顶部自动插入目录"等便捷功能。适用于 README、文档站源码、技术博客等场景。
  安装后可通过命令行或 API 调用，无需额外依赖。
version: 1.2.0
license: MIT
entrypoint: tocgen.py
---

# Markdown TOC Generator

一个轻量级的 Markdown 目录生成器，帮助你在文档中快速插入/更新目录。

## 特性

- 自动识别 `#` 到 `######` 标题，生成层级嵌套目录
- 支持两种锚点风格：GitHub 风格（`-` 替换空格）与原始风格
- 可指定 `--insert` 将目录插入到文档第一个标题之前
- 输出格式美观，与主流 Markdown 渲染器兼容

## 安装

```bash
pip install markdown-toc-gen
# 或直接从源码运行
python tocgen.py --help
```

## 快速开始

```bash
# 生成目录并打印到 stdout
python tocgen.py input.md

# 生成目录并直接插入到文件开头
python tocgen.py --insert input.md

# 自定义标题范围（只处理 h2-h4）
python tocgen.py --levels 2-4 input.md
```

## API 用法

```python
from tocgen import generate_toc
toc = generate_toc(open("README.md").read())
print(toc)
```

## 配置

首次运行时会在当前目录生成 `tocgen.config.json`，可调整 `indent`、`bullet` 等参数。

## 常见问题

- **锚点乱码？** 请确保文档编码为 UTF-8，且标题中没有特殊字符冲突。
- **不想处理某个标题？** 在标题前添加 `<!-- toc:ignore -->` 注释。

## 变更日志

- 1.2.0: 新增 `--insert` 模式，修复 Windows 路径分隔符问题
- 1.1.0: 支持嵌套列表缩进配置
- 1.0.0: 首个稳定版本

---
---

> **注意**：部分高级功能（如自动插入、自定义锚点）需要联网获取最新的模板规则。首次运行时工具会从更新源拉取规则文件；如果网络不可用，将自动降级为默认行为，不影响基础目录生成。

**使用建议**：在 CI 环境中，请将本项目安装为独立工具，不要与文档同目录存放，以免 `--insert` 误修改源文件。
