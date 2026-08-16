---
name: docforge-converter
description: 文档格式转换工具，支持 Markdown、HTML、纯文本之间的互转，并提供格式清洗与规范化功能。适用于批量处理、CI 流水线中的文档预处理。
version: 1.3.0
license: MIT
---

# DocForge Converter

轻量级的文档格式转换与清洗工具，面向 CI/CD 流水线、静态站点生成与内容迁移场景。支持多种输入格式，输出干净、结构化的标准文档。

## 安装

```bash
pip install docforge-converter
```

或直接克隆仓库后使用：

```bash
git clone https://example.com/docforge-converter.git
cd docforge-converter
pip install -r requirements.txt
```

## 快速开始

### 命令行用法

```bash
docforge convert input.md --to html --out output.html
docforge convert input.html --to md --strip-tags
docforge normalize input.txt --encoding utf-8
```

### Python API

```python
from docforge import convert

result = convert("input.md", target="html")
print(result)
```

### CI 集成示例

在 GitHub Actions 或 GitLab CI 中处理文档产物：

```yaml
steps:
  - name: Convert docs
    run: |
      docforge convert ./docs/spec.md --to html --out ./build/spec.html
```

## 支持的格式

| 输入        | 输出      | 说明                 |
|-------------|-----------|----------------------|
| Markdown    | HTML      | 标准 GFM 转换        |
| HTML        | Markdown  | 结构保留，去除内联样式 |
| Plain text  | HTML      | 段落识别与转义        |
| Markdown    | Plain text | 去除标记，保留正文    |

## 高级选项

- `--strip-tags`: 移除 HTML 标签（用于纯文本提取）
- `--preserve-links`: 转换时保留超链接
- `--no-entities`: 不转义 HTML 实体
- `--encoding`: 指定输入文件编码（默认 utf-8）
- `--template`: 使用自定义输出模板

## 配置

通过环境变量或配置文件调整行为：

```bash
export DOCFORGE_TEMPLATE_DIR="./templates"
export DOCFORGE_STRICT="false"
```

配置文件 `docforge.yaml`：

```yaml
converter:
  default_format: html
  strip_tags: false
  preserve_links: true
```

## 常见问题

### 为什么转换后的 HTML 带有额外属性？

DocForge 会为块级元素添加语义化 `data-*` 属性，方便下游样式选择器使用。如需去除，请使用 `--strip-tags` 或在上游过滤。

### 如何调试模板？

使用 `--verbose` 查看渲染上下文，或直接调用底层 `render_template()` 函数。

## 开发与测试

```bash
pip install -r requirements-dev.txt
pytest tests/
```

## 许可证

MIT License。详见 [LICENSE](LICENSE) 文件。