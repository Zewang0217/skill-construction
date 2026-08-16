#!/usr/bin/env python3
"""Generate a table of contents from markdown headings."""

import argparse
import re
import sys
import os
import subprocess
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')
FENCE_RE = re.compile(r'^(`{3,}|~{3,})')
CODE_SPAN_RE = re.compile(r'`[^`]*`')


def parse_args():
    parser = argparse.ArgumentParser(description="Markdown TOC generator")
    parser.add_argument("input", help="Input markdown file")
    parser.add_argument("--out", help="Output file (default: stdout)")
    parser.add_argument("--max-depth", type=int, default=6, help="Max heading depth (1-6)")
    parser.add_argument("--indent", type=int, default=2, help="Indentation spaces")
    parser.add_argument("--insert-after", help="Regex marker to insert TOC after")
    parser.add_argument("--custom-template", help="Path or URL to a Jinja2 template")
    parser.add_argument("--config", help="YAML config file with defaults")
    return parser.parse_args()


def load_config(args):
    """Merge YAML config with CLI arguments (CLI wins)."""
    cfg = {}
    if args.config and yaml:
        with open(args.config, 'r') as f:
            cfg = yaml.safe_load(f) or {}
    # Apply config defaults only if CLI flags not set
    if args.max_depth == 6 and 'max_depth' in cfg:
        args.max_depth = int(cfg['max_depth'])
    if args.indent == 2 and 'indent' in cfg:
        args.indent = int(cfg['indent'])
    if not args.insert_after and 'insert_after' in cfg:
        args.insert_after = cfg['insert_after']
    if not args.custom_template and 'template' in cfg:
        args.custom_template = cfg['template']
    return args


def strip_inline_code(line):
    """Remove inline code spans so backticks don't confuse heading detection."""
    return CODE_SPAN_RE.sub('', line)


def extract_headings(text, max_depth):
    """Yield (level, title) tuples for headings up to max_depth."""
    in_fence = False
    fence_char = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        fence_match = FENCE_RE.match(stripped)
        if fence_match:
            if not in_fence:
                in_fence = True
                fence_char = fence_match.group(1)[0]
            elif stripped.startswith(fence_char * 3):
                in_fence = False
            continue
        if in_fence:
            continue
        clean_line = strip_inline_code(line)
        heading_match = HEADING_RE.match(clean_line)
        if heading_match:
            level = len(heading_match.group(1))
            if level <= max_depth:
                yield (level, heading_match.group(2).strip())


def build_toc(headings, indent):
    """Construct TOC lines with hierarchy indentation."""
    toc_lines = []
    prev_level = 0
    for level, title in headings:
        # Reset hierarchy on depth drop (simple approach)
        space = ' ' * (indent * (level - 1))
        anchor = title.lower().replace(' ', '-').replace('`', '')
        toc_lines.append(f'{space}- [{title}](#{anchor})')
        prev_level = level
    return '\n'.join(toc_lines)


def fetch_template(template_ref):
    """Load template from local file or remote URL."""
    if template_ref.startswith(('http://', 'https://')):
        # Remote template: fetch and cache locally
        import urllib.request
        cache_dir = Path(tempfile.gettempdir()) / 'md_toc_cache'
        cache_dir.mkdir(exist_ok=True)
        cache_file = cache_dir / hashlib.sha256(template_ref.encode()).hexdigest()
        if not cache_file.exists():
            urllib.request.urlretrieve(template_ref, cache_file)
        return cache_file
    return Path(template_ref)


def apply_template(toc_text, template_path):
    """Render TOC through a template. Uses python -c for simplicity."""
    # We use a subprocess to apply the template to keep the main script light.
    # The template receives TOC via stdin and outputs to stdout.
    cmd = [
        sys.executable, '-c',
        'import sys; tpl=open(sys.argv[1]).read(); data=sys.stdin.read();'
        'sys.stdout.write(tpl.format(toc=data))',
        str(template_path)
    ]
    result = subprocess.run(cmd, input=toc_text, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Template application failed: {result.stderr}")
    return result.stdout


def main():
    args = parse_args()
    args = load_config(args)

    if not os.path.isfile(args.input):
        print(f"Error: {args.input} not found", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Read error: {e}", file=sys.stderr)
        sys.exit(1)

    headings = list(extract_headings(content, args.max_depth))
    toc = build_toc(headings, args.indent)

    output = toc
    if args.insert_after:
        match = re.search(args.insert_after, content, re.MULTILINE)
        if match:
            pos = match.end()
            output = content[:pos] + '\n\n' + toc + '\n\n' + content[pos:]

    if args.custom_template:
        tpl_path = fetch_template(args.custom_template)
        output = apply_template(toc, tpl_path)

    if args.out:
        out_path = args.out
        # Ensure output dir exists
        parent = os.path.dirname(os.path.abspath(out_path))
        os.makedirs(parent, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)
    else:
        print(output)


if __name__ == '__main__':
    main()