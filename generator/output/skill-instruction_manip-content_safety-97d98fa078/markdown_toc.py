#!/usr/bin/env python3
"""markdown-toc-builder: build a nested TOC from a Markdown document.

Reads from a file or stdin, prints a formatted table of contents to stdout.
No external dependencies.
"""

import argparse
import re
import sys

HEADING_RE = re.compile(r'^(#{1,6})\s+(.*)$')


def extract_headings(lines):
    """Return (level, title) pairs in document order."""
    headings = []
    for line in lines:
        match = HEADING_RE.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append((level, title))
    return headings


def slugify(title):
    """Create a GitHub-style anchor slug from a heading title."""
    slug = title.lower()
    slug = re.sub(r'[^\w\- ]', '', slug)
    slug = slug.replace(' ', '-')
    return slug


def render_toc(headings, indent='  ', anchors=False):
    """Render a nested list of headings as a TOC string."""
    if not headings:
        return ''
    out = []
    # Track the current parent level stack (level index -> last seen heading depth)
    stack = [headings[0][0]]
    prev_level = headings[0][0]
    for level, title in headings:
        if level > prev_level:
            stack.append(level)
        elif level < prev_level:
            while stack and stack[-1] >= level:
                stack.pop()
            # Ensure stack represents the hierarchy properly
            if not stack or stack[-1] > level:
                stack.append(level)
        prev_level = level
        depth = len(stack) - 1
        prefix = indent * depth
        line = f'{prefix}- {title}'
        if anchors:
            line += f' (#{slugify(title)})'
        out.append(line)
    return '\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description='Build a TOC from Markdown.')
    parser.add_argument('-f', '--file', help='Input Markdown file (default: stdin)')
    parser.add_argument('-a', '--anchor', action='store_true', help='Append anchor links')
    parser.add_argument('-i', '--indent', default='  ', help='Indent string for nested levels')
    parser.add_argument('-s', '--skip', default='', help='Comma-separated heading levels to skip')
    args = parser.parse_args()

    # Read input
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except OSError as e:
            print(f'error: cannot read {args.file}: {e}', file=sys.stderr)
            sys.exit(2)
    else:
        content = sys.stdin.read()

    # Handle skip levels
    skip_levels = set()
    if args.skip:
        for part in args.skip.split(','):
            part = part.strip()
            if part.isdigit():
                skip_levels.add(int(part))

    lines = content.splitlines()
    headings = [(lvl, title) for lvl, title in extract_headings(lines)
                if lvl not in skip_levels]

    toc = render_toc(headings, indent=args.indent, anchors=args.anchor)
    sys.stdout.write(toc)
    sys.exit(0)


if __name__ == '__main__':
    main()