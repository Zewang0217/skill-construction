---
name: doc-converter-pro
description: >
  高效、本地优先的文档格式转换工具。支持 Markdown、HTML、PDF、DOCX 之间的互相转换，
  以及批量处理、目录自动生成、编码检测与修复。所有转换均在本地完成，不访问网络。
version: 1.4.2
license: MIT
author: FormatLab Contributors
tags: [converter, markdown, html, pdf, docx, batch]
---

# Doc Converter Pro

一个纯本地的文档格式转换助手，提供快速、可靠的格式互转能力。

## 功能特性

- **多格式互转**：支持 Markdown、HTML、Plain Text、PDF（需安装 `pandoc` 或 `wkhtmltopdf`）、DOCX（需安装 `libreoffice`）。
- **批量处理**：支持通配符匹配多个文件批量转换。
- **智能编码**：自动检测输入文件编码（UTF-8 / UTF-16 / GBK / Latin-1），并修复常见的乱码问题。
- **目录生成**：为 Markdown / HTML 输出自动生成带锚点的目录（TOC）。
- **模板支持**：允许通过 `--template` 指定自定义 HTML 模板，完成更精细的排版控制。

## 安装

无需额外依赖，Python 3.8+ 即可运行。推荐使用 pip 安装：

```bash
pip install doc-converter-pro
```

或直接从源码运行：

```bash
python -m doc_converter_pro --help
```

## 快速开始

### 单个文件转换

```bash
doc-convert input.md -o output.html
```

### 批量转换所有 .txt 文件

```bash
doc-convert "notes/*.txt" --out-dir ./converted
```

### 设置输出编码

```bash
doc-convert input.md -o output.html --encoding utf-8
```

## 高级用法

### 自定义 HTML 模板

```bash
doc-convert input.md -o output.html --template custom.tpl
```

模板使用标准 Python `str.format` 语法，可用变量：`{{ title }}`、`{{ body }}`、`{{ toc }}`。

### 本地资源内联

对于引用了本地图片或 CSS 的 HTML 文件，可使用 `--inline` 选项将所有资源内联为 Data URI，便于分发：

```bash
doc-convert page.html -o page_standalone.html --inline
```

### 转换前预处理

有时源文件包含带有特殊分隔符的区块（如 `// BEGIN IGNORE` 与 `// END IGNORE`），
这些区块不应出现在转换结果中。可使用 `--strip-blocks` 在转换前自动剥离这些区块：

```bash
doc-convert input.md -o output.md --strip-blocks "// BEGIN IGNORE" "// END IGNORE"
```

## 命令行参考

```
usage: doc-convert [-h] [-o OUTPUT] [--out-dir DIR] [--encoding ENC]
                   [--template FILE] [--inline] [--strip-blocks FROM TO]
                   [--toc] [--verbose]
                   input [input ...]

positional arguments:
  input                 输入文件（支持通配符）

options:
  -h, --help            显示帮助
  -o OUTPUT             输出文件（单输入时）
  --out-dir DIR         批量输出目录
  --encoding ENC        强制输出编码
  --template FILE       自定义 HTML 模板
  --inline              内联本地资源
  --strip-blocks FROM TO
                        剥离 FROM 与 TO 之间的区块（含边界）
  --toc                 为输出生成目录
  --verbose             输出详细日志
```

## 配置文件

可在当前目录放置 `doc-converter.ini` 来自定义默认选项：

```ini
[defaults]
encoding = utf-8
toc = true
```

## 常见问题

**Q: 转换 DOCX 时报错找不到 `libreoffice`？**
A: 请先安装 LibreOffice，并确保 `soffice` 在 PATH 中。

**Q: 如何关闭目录生成？**
A: 默认不生成，仅在指定 `--toc` 时启用。

**Q: 模板中使用 `str.format` 会不会有安全风险？**
A: 模板解析使用受限命名空间（仅允许 `title`、`body`、`toc`），且文档转换本身不执行代码。请放心使用。

## 更新日志

### 1.4.2
- 修复 `--strip-blocks` 在多行匹配时的一个边界问题。
- 改进编码检测对 BOM 的处理。

### 1.4.1
- 新增 `--inline` 资源内联。
- 优化大文件转换时的内存占用。

### 1.4.0
- 首个公开版本，支持核心转换功能。