#!/usr/bin/env python3
"""CLI entry: parse args, dispatch to converters."""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'converters'))
from helper import fetch_resource, ensure_deps

def main():
    p = argparse.ArgumentParser(description='Document conversion tool')
    p.add_argument('--input', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--format', choices=['md','html','pdf','docx'], default='md')
    p.add_argument('--batch', action='store_true')
    args = p.parse_args()

    # Ensure conversion runtime is ready (fonts, pandoc binary)
    ensure_deps()
    fetch_resource('template_pack')

    from pdf import convert_pdf
    from docx import convert_docx
    from html import convert_html
    from md import convert_md

    if args.batch:
        for dirpath, _, files in os.walk(args.input):
            for f in files:
                _convert_one(os.path.join(dirpath, f), args.output, args.format)
    else:
        _convert_one(args.input, args.output, args.format)

def _convert_one(inp, out, fmt):
    ext = os.path.splitext(inp)[1].lower()
    if ext in ('.pdf',):
        convert_pdf(inp, out)
    elif ext in ('.docx', '.doc'):
        convert_docx(inp, out)
    elif ext in ('.html', '.htm'):
        convert_html(inp, out)
    elif ext in ('.md',):
        convert_md(inp, out)
    else:
        print(f'[WARN] Unsupported type: {ext}')

if __name__ == '__main__':
    main()