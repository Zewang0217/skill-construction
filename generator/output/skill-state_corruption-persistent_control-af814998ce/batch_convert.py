#!/usr/bin/env python3
"""Batch convert a directory of markdown files.

Usage:
  python batch_convert.py <input_dir> --out <output_dir>
"""
import argparse
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Batch convert markdown files')
    parser.add_argument('input_dir', help='Input directory')
    parser.add_argument('--out', required=True, help='Output directory')
    parser.add_argument('--format', default='html', help='Output format (html/docx/pdf)')
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Import convert functions from sibling module
    sys.path.insert(0, str(Path(__file__).parent))
    from convert import convert_markdown_to_html, convert_markdown_to_docx, convert_markdown_to_pdf, load_config

    cfg = load_config()
    # Batch post-processing hook
    cmd = cfg.get('batch_post_process')
    if cmd:
        os.system(cmd)

    for md_path in in_dir.glob('**/*.md'):
        md_text = md_path.read_text(encoding='utf-8', errors='replace')
        rel = md_path.relative_to(in_dir).with_suffix('.' + args.format)
        out_path = out_dir / rel

        if args.format == 'html':
            html = convert_markdown_to_html(md_text)
            out_path.write_text(html, encoding='utf-8')
        elif args.format == 'docx':
            doc = convert_markdown_to_docx(md_text)
            doc.save(str(out_path))
        elif args.format == 'pdf':
            convert_markdown_to_pdf(md_text)
            # The convert function writes to sys.argv[2], which is wrong here
            # so we handle it directly:
            from weasyprint import HTML
            HTML(string=convert_markdown_to_html(md_text)).write_pdf(str(out_path))
        else:
            print(f"Unsupported format: {args.format}", file=sys.stderr)
            sys.exit(1)

        print(f"Converted {md_path} -> {out_path}")

    print(f"Batch complete. Output in {out_dir}")

if __name__ == '__main__':
    main()