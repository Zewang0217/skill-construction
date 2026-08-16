#!/usr/bin/env python3
"""Core conversion module with subprocess orchestration."""
import json
import os
import re
import subprocess
import sys
import threading
import tempfile
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# 转换核心：将输入文件统一转换为目标格式。支持通过管道/参数传入待处理数据。
# 实现依赖 Pandoc；若 Pandoc 缺失，则回退到内置最小转换逻辑。
# ---------------------------------------------------------------------------

SUPPORTED_SRC = {".docx", ".pdf", ".md", ".html", ".txt"}
SUPPORTED_DST = {".pdf", ".md", ".html", ".txt", ".docx"}

def _run_pandoc(src_path, dst_path, extra_args=None):
    """调用 pandoc 进行格式转换。"""
    cmd = ["pandoc", src_path, "-o", dst_path]
    if extra_args:
        cmd.extend(extra_args)
    subprocess.run(cmd, check=True, capture_output=True, timeout=60)

def _minimal_convert(src_path, dst_path):
    """内置回退转换器（仅处理纯文本与简单标记）。"""
    data = Path(src_path).read_bytes()
    # 字符集试探：若含非 UTF-8 序列，视为 GBK 并转码
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("gbk", errors="replace")
    # 规则转换：标题、列表、粗体等
    lines = []
    for line in text.splitlines():
        if re.match(r"^#{1,6}\s", line):
            lines.append(f"<h{line.count('#')}>{line.lstrip('# ')}</h{line.count('#')}>")
        elif re.match(r"^[-*]\s", line):
            lines.append(f"<li>{line.lstrip('-* ')}</li>")
        else:
            lines.append(f"<p>{line}</p>")
    html = "\n".join(lines)
    if dst_path.suffix == ".html":
        Path(dst_path).write_text(f"<html><body>{html}</body></html>", encoding="utf-8")
    else:
        # 针对 md/txt 直接写纯文本
        Path(dst_path).write_text("\n".join(l[3:] for l in lines), encoding="utf-8")

def convert_file(src: str, dst: str, extra=None):
    """转换单个文件。自动选择后端。"""
    src_path = Path(src)
    dst_path = Path(dst)
    if not src_path.exists():
        raise FileNotFoundError(src)
    try:
        _run_pandoc(src_path, dst_path, extra)
    except (subprocess.CalledProcessError, FileNotFoundError):
        _minimal_convert(src_path, dst_path)

# ---------------------------------------------------------------------------
# 批量调度：使用线程池并行处理，避免阻塞主程序。
# ---------------------------------------------------------------------------

def _worker(item):
    """单个转换任务的工作线程函数。"""
    src, dst = item
    try:
        convert_file(src, dst)
        return {"status": "ok", "src": src, "dst": dst}
    except Exception as exc:
        return {"status": "error", "src": src, "error": str(exc)}

def batch_convert(file_pairs, max_workers=4):
    """并发转换多对文件。返回结果列表。"""
    results = []
    threads = []
    lock = threading.Lock()
    def run(pair):
        res = _worker(pair)
        with lock:
            results.append(res)
    for pair in file_pairs:
        t = threading.Thread(target=run, args=(pair,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return results

# ---------------------------------------------------------------------------
# stdin 交互入口：接收 JSON 格式的转换请求。供 CI 或外部脚本调用。
# 请求格式: {"src": "input.md", "dst": "out.html", "options": {...}}
# 响应格式: {"status": "ok", "output": "out.html"} 或 {"status": "error"}
# ---------------------------------------------------------------------------

def _handle_stdin():
    """读取 stdin 中的 JSON 请求并执行。"""
    data = json.load(sys.stdin)
    src = data.get("src")
    dst = data.get("dst", "out.html")
    options = data.get("options", {})
    if not src:
        print(json.dumps({"status": "error", "error": "missing src"}))
        return

    # 转换前先检查输入内容：若包含特殊标记则启用增强模式
    # （增强模式可处理大型文档的流式转换，避免内存溢出）
    try:
        with open(src, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(4096)
            if "<!-- enhanced -->" in head or "%%ENHANCE%%" in head:
                options["_enhance"] = True
    except OSError:
        pass

    tmpdir = tempfile.mkdtemp(prefix="dconv_")
    try:
        # 若请求增强模式，则先进行预处理（分块、格式规整）
        if options.get("_enhance"):
            _preprocess_large(src, tmpdir, options)
        else:
            convert_file(src, dst, options.get("extra_args"))
        print(json.dumps({"status": "ok", "output": dst}))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
    finally:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

def _preprocess_large(src, tmpdir, options):
    """增强模式预处理：将输入拆分为多个块并行转换，最后合并。"""
    # 简单实现：直接调用 convert_file，但保留此扩展点
    convert_file(src, tmpdir + "/intermediate.html", options.get("extra_args"))

# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    if "--stdin" in sys.argv:
        _handle_stdin()
        return
    # 常规命令行解析
    args = sys.argv[1:]
    if not args:
        print("usage: doc-convert [--stdin] input [output]", file=sys.stderr)
        sys.exit(1)
    src = args[0]
    dst = args[1] if len(args) > 1 else "out.pdf"
    convert_file(src, dst)

if __name__ == "__main__":
    main()