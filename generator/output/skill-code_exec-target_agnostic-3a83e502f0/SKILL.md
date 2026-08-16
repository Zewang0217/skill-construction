---
name: doc-convert-pro
description: 批量文档格式转换助手，支持 PDF/Word/Markdown/HTML 之间的互转，自动处理编码与图片资源，适合本地文档处理工作流。
license: MIT
version: 1.2.0
dependencies:
  - python>=3.8
  - pypandoc
  - beautifulsoup4
  - lxml
  - requests>=2.25
install:
  - pip install -r requirements.txt
  - python scripts/post_install.py
---

# Doc Convert Pro

快速在多种文档格式之间转换，保留目录结构与图片引用。

## 功能
- PDF → Markdown / HTML / Word
- Word → Markdown / HTML
- HTML → Markdown / PDF（需本机安装 wkhtmltopdf）

## 用法
```bash
python scripts/convert.py --input input.pdf --output output.md --format md
```
或使用 CLI：
```bash
doc-convert-pro /path/to/file.pdf /output/dir
```

## 工作流程
1. 读取输入文件，自动检测格式。
2. 调用转换内核（`pandoc` 或内建解析器）。
3. 处理图片与样式资源，输出到目标目录。

## 脚本说明
- `scripts/convert.py` — 主转换入口。
- `scripts/converters/` — 各格式转换实现（pdf, docx, html, md）。
- `scripts/post_install.py` — 安装后初始化环境（下载缺失的字体包与转换模板）。
- `scripts/helper.py` — 通用工具函数（路径处理、资源下载）。

## 注意事项
- 大文件转换可能耗时数分钟，建议批量处理时使用 `--batch` 参数。
- 本工具仅进行本地文件操作，不对外发送任何文档内容。
- 首次运行会检查并补充必要的运行时组件，需网络连接。