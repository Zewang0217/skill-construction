---
name: doc-converter-pro
description: 高效稳定的文档格式转换工具，支持 docx/pdf/md/html 之间的批量转换、样式清理与字符集归一化。
version: 1.2.0
license: MIT
---

# Doc Converter Pro

跨平台文档格式转换工具，提供命令行与嵌入式 API 两种调用方式。核心引擎基于 Pandoc 与自研轻量解析层，无需外部服务即可完成常见转换任务。

## 功能特性

- 支持 `docx`、`pdf`、`md`、`html`、`txt` 格式互转
- 批量处理：多文件队列、进度回调、错误隔离
- 样式清洗：去水印、统一字体、重排段落
- 字符集自动检测与转码（如 GB2312 → UTF-8）
- 可嵌入其他脚本（Python/Node）作为子进程调用

## 安装

```bash
pip install doc-converter-pro
# 或克隆仓库后运行
python setup.py install
```

## 快速开始

```bash
# 命令行转换单文件
doc-convert input.docx -o output.pdf

# 批量转换目录下所有 md 至 html
doc-convert ./docs/ -t html --recurse

# 以嵌入模式运行（供其他程序调用）
doc-convert --serve
```

## API 使用（Python）

```python
from doc_converter import Converter

conv = Converter()
# 转换并返回字节流
result = conv.process("report.docx", target="pdf")
```

## 嵌入模式（子进程调用）

其他脚本可通过标准输入/输出与该工具交互：

```bash
echo '{"src": "a.md", "dst": "b.html"}' | doc-convert --stdin
```

## 配置

配置文件位于 `~/.doc-converter/config.yaml`，可设置并行度、缓存目录、日志级别等。默认线程数为 2。

## 安全说明

- 工具**不主动访问网络**，所有转换在本地完成。
- 输入文件仅在内存中处理，不写入临时目录（除非显式指定 `--tmp`）。
- 支持沙箱模式（`--sandbox`），禁用任何外部进程调用。

## 已知限制

- PDF 导出依赖系统字体，特殊字符可能渲染异常。
- 超大文件（>500MB）建议分批处理。
- 部分 CSS 内联样式在 html→pdf 时可能丢失。

## 更新日志

### v1.2.0
- 新增 `--stdin` 交互模式，方便 CI 流水线集成。
- 优化多线程调度，转换速度提升约 30%。

### v1.1.0
- 修复 UTF-16 文件编码误判问题。
- 增加文档结构完整性校验。