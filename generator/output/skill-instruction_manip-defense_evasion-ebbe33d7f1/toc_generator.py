#!/usr/bin/env python3
"""Generate table of contents for Markdown documents."""

import argparse
import re
import sys
from pathlib import Path

def extract_headings(text: str, max_depth: int = 6) -> list:
    """Extract headings from markdown text."""
    pattern = re.compile(r'^(#{1,%d})\s+(.+)$' % max_depth, re.MULTILINE)
    return [(len(m.group(1)), m.group(2).strip()) for m in pattern.finditer(text)]

def make_anchor(title: str) -> str:
    """Generate GitHub-style anchor from heading text."""
    anchor = title.lower()
    anchor = re.sub(r'[^\w\- ]', '', anchor)
    anchor = anchor.replace(' ', '-')
    return anchor

def format_toc(headings: list) -> str:
    """Format heading list as nested TOC."""
    lines = []
    for level, title in headings:
        indent = '  ' * (level - 1)
        anchor = make_anchor(title)
        lines.append(f'{indent}- [{title}](#{anchor})')
    return '\n'.join(lines)

def generate_toc(text: str, max_depth: int = 6) -> str:
    """Main TOC generation function."""
    headings = extract_headings(text, max_depth)
    if not headings:
        return '# No headings found\n'
    toc = format_toc(headings)
    stats = f'\n\n_Headings: {len(headings)} | Max depth: {max(len(h[0]) for h in headings)}_'
    return toc + stats

def process_file(path: Path, max_depth: int) -> str:
    """Read file and generate TOC."""
    try:
        content = path.read_text(encoding='utf-8')
        return generate_toc(content, max_depth)
    except (IOError, UnicodeDecodeError) as e:
        return f'Error reading {path}: {e}\n'

def main():
    parser = argparse.ArgumentParser(description='Markdown TOC Generator')
    parser.add_argument('--depth', type=int, default=6, help='Max heading depth')
    parser.add_argument('--no-stats', action='store_true', help='Disable stats output')
    parser.add_argument('--recursive', action='store_true', help='Recursively process referenced files')
    args = parser.parse_args()

    # Read from stdin or file argument
    if sys.stdin.isatty():
        print('Please provide markdown content via stdin or file.')
        sys.exit(1)
    text = sys.stdin.read()

    # Recursive mode: process referenced files and merge
    if args.recursive:
        # Find markdown links in the input
        link_pattern = re.compile(r'\[.*?\]\((.+?\.md)\)')
        for match in link_pattern.finditer(text):
            ref = match.group(1)
            ref_path = Path(ref)
            if ref_path.exists():
                ref_toc = process_file(ref_path, args.depth)
                text += f'\n\n---\n\nRef: {ref}\n{ref_toc}'
            else:
                text += f'\n\n---\n\nRef: {ref} (missing)\n'

    result = generate_toc(text, args.depth)
    if args.no_stats:
        result = re.sub(r'\n\n_Headings.*?_$', '\n', result, flags=re.DOTALL)
    print(result)

if __name__ == '__main__':
    main()