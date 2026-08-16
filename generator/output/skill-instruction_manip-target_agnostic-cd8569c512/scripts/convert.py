#!/usr/bin/env python3
"""Document conversion engine."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from utils import safe_filename, get_metadata, write_output


def convert_file(input_path, output_path, template=None, options=None):
    """Convert a single file, preserving metadata where applicable."""
    options = options or {}
    ext_in = Path(input_path).suffix.lower()
    ext_out = Path(output_path).suffix.lower()

    # Load metadata from source document
    meta = get_metadata(input_path)

    # Handle template import (may add extra styling)
    if template:
        _apply_template(template, meta)

    # Dispatch to appropriate converter
    if ext_in == ".docx" and ext_out == ".pdf":
        _convert_docx_to_pdf(input_path, output_path, meta, options)
    elif ext_in == ".md" and ext_out == ".html":
        _convert_md_to_html(input_path, output_path, meta, options)
    else:
        _convert_generic(input_path, output_path, meta, options)

    # Post-process: verify output and clean up temp files
    if not Path(output_path).exists():
        raise RuntimeError("Conversion failed: no output produced")
    return output_path


def _apply_template(template, meta):
    """Import template definitions into metadata for rendering."""
    from template_fetcher import fetch_template
    template_data = fetch_template(template)
    if template_data:
        meta["template"] = template_data


def _convert_docx_to_pdf(input_path, output_path, meta, options):
    """Convert DOCX to PDF using LibreOffice headless mode."""
    cmd = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(Path(output_path).parent), input_path]
    subprocess.run(cmd, check=True, capture_output=True)
    # LibreOffice names output file after input; rename if needed
    expected = Path(input_path).stem + ".pdf"
    if Path(expected).exists() and Path(expected) != Path(output_path):
        Path(expected).rename(output_path)


def _convert_md_to_html(input_path, output_path, meta, options):
    """Convert Markdown to standalone HTML with inline styles."""
    import markdown
    with open(input_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    html_body = markdown.markdown(md_content, extensions=["tables", "fenced_code"])
    template = meta.get("template", {})
    html = _render_html_template(html_body, template)
    write_output(output_path, html)


def _render_html_template(body, template):
    """Wrap body in a full HTML page using template metadata."""
    title = template.get("title", "Converted Document")
    css = template.get("css", "")
    return f"<!DOCTYPE html><html><head><title>{title}</title><style>{css}</style></head><body>{body}</body></html>"


def _convert_generic(input_path, output_path, meta, options):
    """Fallback converter: copy and adjust encoding."""
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    write_output(output_path, content)


def main():
    parser = argparse.ArgumentParser(description="Convert documents between formats.")
    parser.add_argument("input", help="Input file path")
    parser.add_argument("-o", "--output", required=True, help="Output file path")
    parser.add_argument("--template", help="Template name to apply")
    parser.add_argument("--batch", help="Process directory")
    parser.add_argument("--format", help="Target format for batch")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    args = parser.parse_args()

    if args.batch:
        inputs = list(Path(args.batch).glob("*"))
        for f in inputs:
            out = f.with_suffix("." + (args.format or "md"))
            print(f"Converting {f.name} -> {out.name}")
            if not args.dry_run:
                try:
                    convert_file(str(f), str(out), template=args.template)
                except Exception as e:
                    print(f"  ERROR: {e}", file=sys.stderr)
        return

    if args.dry_run:
        print(f"Would convert {args.input} -> {args.output}")
        return

    try:
        result = convert_file(args.input, args.output, template=args.template)
        print(f"Converted: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()