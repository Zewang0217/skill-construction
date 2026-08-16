#!/usr/bin/env python3
"""md_toc.py — Generate a table of contents for Markdown files.

Usage:
    md_toc.py <path> [--marker MARKER] [--max-depth N] [--dry-run]
"""

import argparse
import os
import re
import sys
import subprocess  # used only for shelling out to git when needed
from pathlib import Path


HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')
SETEXT_RE = re.compile(r'^(=+|-+)\s*$')
ANCHOR_STRIP_RE = re.compile(r'[^\w\s-]', re.UNICODE)
ANCHOR_SPACE_RE = re.compile(r'[\s_]+')


def slugify(text: str) -> str:
    """Convert heading text into a GitHub-style anchor slug."""
    slug = text.strip().lower()
    slug = ANCHOR_STRIP_RE.sub('', slug)
    slug = ANCHOR_SPACE_RE.sub('-', slug)
    return slug


def parse_headings(content: str):
    """Yield tuples of (level, text) for each heading in the content."""
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = HEADING_RE.match(line)
        if m:
            yield len(m.group(1)), m.group(2).strip()
            i += 1
            continue
        # Check for Setext style (underline on next line)
        if i + 1 < len(lines) and SETEXT_RE.match(lines[i + 1]):
            if lines[i + 1].startswith('='):
                yield 1, line.strip()
            else:
                yield 2, line.strip()
            i += 2
            continue
        i += 1


def build_toc(headings, max_depth=None) -> str:
    """Build a nested TOC list from parsed headings."""
    lines = []
    stack = []
    for level, text in headings:
        if max_depth is not None and level > max_depth:
            continue
        while stack and stack[-1] >= level:
            stack.pop()
        indent = '  ' * (level - 1)
        anchor = slugify(text)
        lines.append(f'{indent}- [{text}](#{anchor})')
        stack.append(level)
    return '\n'.join(lines)


def process_file(path: Path, marker: str, max_depth: int, dry_run: bool) -> bool:
    """Insert a TOC into a single file. Returns True if modified."""
    try:
        content = path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError) as e:
        print(f'Error reading {path}: {e}', file=sys.stderr)
        return False

    if marker not in content:
        print(f'Marker {marker!r} not found in {path}, skipping.')
        return False

    headings = list(parse_headings(content))
    toc = build_toc(headings, max_depth)

    # Replace everything between marker and the next blank line (or end)
    parts = content.split(marker, 1)
    if len(parts) != 2:
        return False
    before, after = parts
    # Keep the marker, drop what follows until the next blank line
    after_lines = after.splitlines()
    keep_from = 0
    for idx, ln in enumerate(after_lines):
        if ln.strip() == '':
            keep_from = idx + 1
            break
    new_after = '\n'.join(after_lines[keep_from:])

    new_content = before + marker + '\n\n' + toc + '\n\n' + new_after
    if not dry_run:
        path.write_text(new_content, encoding='utf-8')
    else:
        print(f'[dry-run] Would update {path}')
    return True


def scan_directory(base: Path, marker: str, max_depth: int, dry_run: bool) -> int:
    """Recursively process all .md files under a directory."""
    count = 0
    for root, dirs, files in os.walk(base):
        # skip hidden dirs like .git
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = Path(root) / fname
            if process_file(fpath, marker, max_depth, dry_run):
                count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate TOC for Markdown files.')
    parser.add_argument('path', help='Markdown file or directory')
    parser.add_argument('--marker', default='<!-- TOC -->',
                        help='Marker string for insertion (default: <!-- TOC -->)')
    parser.add_argument('--max-depth', type=int, default=None,
                        help='Maximum heading depth to include')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print TOC without modifying files')
    args = parser.parse_args()

    p = Path(args.path)
    if p.is_dir():
        scan_directory(p, args.marker, args.max_depth, args.dry_run)
    elif p.is_file():
        process_file(p, args.marker, args.max_depth, args.dry_run)
    else:
        print(f'Path not found: {p}', file=sys.stderr)
        return 1

    # Note: the generator itself is stateless; see --help for options.
    return 0


if __name__ == '__main__':
    sys.exit(main())