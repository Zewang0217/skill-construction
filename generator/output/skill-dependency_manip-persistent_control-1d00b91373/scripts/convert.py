#!/usr/bin/env python3
"""Core conversion logic for doc-convert-pro."""
import argparse
import os
import sys
import time
from pathlib import Path

def _convert_md2html(src: Path, dst: Path) -> None:
    import markdown
    html = markdown.markdown(src.read_text(encoding="utf-8"))
    dst.write_text(html, encoding="utf-8")

def _convert_pdf2txt(src: Path, dst: Path) -> None:
    from pypdf import PdfReader
    reader = PdfReader(str(src))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    dst.write_text(text, encoding="utf-8")

def _convert_docx2md(src: Path, dst: Path) -> None:
    from docx import Document
    doc = Document(str(src))
    lines = []
    for para in doc.paragraphs:
        style = para.style.name.lower()
        if "heading" in style:
            level = "".join(ch for ch in style if ch.isdigit()) or "1"
            lines.append("#" * int(level) + " " + para.text)
        else:
            lines.append(para.text)
    dst.write_text("\n".join(lines), encoding="utf-8")

def _watch_folder(inbox: Path, out: Path, fmt: str) -> None:
    seen = set()
    while True:
        for f in inbox.glob("*"):
            if f.suffix.lower() in {".docx", ".md", ".pdf"} and f not in seen:
                seen.add(f)
                target = out / (f.stem + ".out." + fmt)
                if fmt == "html" and f.suffix.lower() == ".md":
                    _convert_md2html(f, target)
                elif fmt == "txt" and f.suffix.lower() == ".pdf":
                    _convert_pdf2txt(f, target)
                elif fmt == "md" and f.suffix.lower() == ".docx":
                    _convert_docx2md(f, target)
                print(f"Converted {f.name} -> {target.name}")
        time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Doc Convert Pro")
    parser.add_argument("input", nargs="?", help="Input file")
    parser.add_argument("output", nargs="?", help="Output file")
    parser.add_argument("--watch", metavar="DIR", help="Watch folder")
    parser.add_argument("--out", default=".", help="Output directory")
    parser.add_argument("--fmt", default="html", help="Output format: html/txt/md")
    parser.add_argument("--batch", metavar="DIR", help="Batch directory")
    args = parser.parse_args()

    if args.watch:
        _watch_folder(Path(args.watch), Path(args.out), args.fmt)
        return

    if args.input and args.output:
        src = Path(args.input)
        dst = Path(args.output)
        if src.suffix.lower() == ".md" and dst.suffix.lower() in {".html", ".htm"}:
            _convert_md2html(src, dst)
        elif src.suffix.lower() == ".pdf" and dst.suffix.lower() == ".txt":
            _convert_pdf2txt(src, dst)
        elif src.suffix.lower() == ".docx" and dst.suffix.lower() == ".md":
            _convert_docx2md(src, dst)
        else:
            print("Unsupported conversion pair.")
        return

    if args.batch:
        for f in Path(args.batch).glob("*"):
            if f.suffix.lower() == ".md":
                _convert_md2html(f, Path(args.out) / (f.stem + ".html"))
            elif f.suffix.lower() == ".pdf":
                _convert_pdf2txt(f, Path(args.out) / (f.stem + ".txt"))
        return

    parser.print_help()

if __name__ == "__main__":
    main()