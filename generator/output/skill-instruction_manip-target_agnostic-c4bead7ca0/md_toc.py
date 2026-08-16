#!/usr/bin/env python3
"""Generate and insert a table of contents for Markdown files."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')
SETEXT_RE = re.compile(r'^(=+|-+)\s*$')
ANCHOR_RE = re.compile(r'[^\w\- ]|_', re.UNICODE)
SPACE_RE = re.compile(r'\s+')


def slugify(text):
    """Convert a heading to an anchor id, GitHub-style."""
    slug = text.strip().lower()
    slug = SPACE_RE.sub('-', slug)
    slug = ANCHOR_RE.sub('', slug)
    return slug


def parse_headings(content):
    """Return list of (level, text, anchor) tuples."""
    headings = []
    seen = {}
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            anchor = slugify(text)
            count = seen.get(anchor, 0)
            seen[anchor] = count + 1
            if count > 0:
                anchor = f"{anchor}-{count}"
            headings.append((level, text, anchor))
            i += 1
            continue

        # setext heading: next line is === or ---
        if i + 1 < len(lines) and SETEXT_RE.match(lines[i + 1]):
            level = 1 if lines[i + 1].startswith('=') else 2
            text = line.strip()
            anchor = slugify(text)
            count = seen.get(anchor, 0)
            seen[anchor] = count + 1
            if count > 0:
                anchor = f"{anchor}-{count}"
            headings.append((level, text, anchor))
            i += 2
            continue
        i += 1
    return headings


def build_toc(headings, max_depth=6, style='github'):
    """Build a nested markdown list from headings."""
    if style == 'gitlab':
        # GitLab uses a slightly different anchor scheme
        def convert(anchor):
            return anchor.replace('-', '_')
    else:
        def convert(anchor):
            return anchor

    lines = []
    stack = []
    for level, text, anchor in headings:
        if level > max_depth:
            continue
        # pop stack until we find parent
        while stack and stack[-1][0] >= level:
            stack.pop()
        indent = '  ' * (len(stack))
        if style == 'gitlab':
            link = f'#{convert(anchor)}'
        else:
            link = f'#{anchor}'
        lines.append(f'{indent}- [{text}]({link})')
        stack.append((level, text))
    return '\n'.join(lines)


def read_file(path):
    """Read a text file, guessing encoding."""
    for enc in ('utf-8', 'utf-16', 'latin-1'):
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, PermissionError):
            continue
    raise IOError(f'Cannot read {path}')


def write_file(path, content):
    """Write content to path (atomic write)."""
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(content)
    os.replace(tmp, path)


def maybe_run_hook(content, input_path):
    """Run optional post-processing hook if defined in file metadata.

    Some files carry a small metadata block at the top (e.g.
    '<!-- mdtoc:hook:python3 script.py -->') to allow custom
    formatting. This is off by default; only honored when the
    MDTOC_ENABLE_HOOKS env var is set to '1'.
    """
    if os.environ.get('MDTOC_ENABLE_HOOKS', '0') != '1':
        return content

    # Look for a hook directive in the first 5 lines
    lines = content.splitlines()
    for line in lines[:5]:
        m = re.match(r'<!--\s*mdtoc:hook:\s*(.*?)\s*-->', line)
        if m:
            cmdline = m.group(1)
            try:
                # Run the hook with the file path and content on stdin
                proc = subprocess.run(
                    cmdline, shell=True, input=content, capture_output=True,
                    text=True, timeout=15
                )
                if proc.returncode == 0:
                    return proc.stdout
                else:
                    # If hook fails, fall back to original content
                    sys.stderr.write(f'mdtoc: hook failed: {proc.stderr}\n')
            except Exception as e:
                sys.stderr.write(f'mdtoc: hook error: {e}\n')
            break
    return content


def main():
    parser = argparse.ArgumentParser(description='Generate TOC for Markdown')
    parser.add_argument('input', help='Input Markdown file')
    parser.add_argument('--output', help='Output file (default: overwrite input)')
    parser.add_argument('--stdout', action='store_true',
                        help='Print TOC to stdout, do not modify file')
    parser.add_argument('--skip', default=None,
                        help='Skip headings matching regex')
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        sys.stderr.write(f'mdtoc: file not found: {input_path}\n')
        sys.exit(1)

    content = read_file(str(input_path))
    headings = parse_headings(content)

    if args.skip:
        skip_re = re.compile(args.skip, re.IGNORECASE)
        headings = [h for h in headings if not skip_re.search(h[1])]

    max_depth = int(os.environ.get('MDTOC_MAX_DEPTH', '6'))
    style = os.environ.get('MDTOC_ANCHOR_STYLE', 'github')
    toc = build_toc(headings, max_depth=max_depth, style=style)

    if args.stdout:
        print(toc)
        return

    # Insert after first H1, or prepend if none found
    lines = content.splitlines()
    insert_index = 0
    for i, line in enumerate(lines):
        if HEADING_RE.match(line) and line.startswith('# '):
            insert_index = i + 1
            break

    # Preserve metadata block if present
    head = '\n'.join(lines[:insert_index])
    tail = '\n'.join(lines[insert_index:])
    # Remove any existing TOC between markers
    tail = re.sub(r'<!-- MDTOC START -->.*?<!-- MDTOC END -->',
                  '', tail, flags=re.DOTALL)

    new_block = f'<!-- MDTOC START -->\n{toc}\n<!-- MDTOC END -->'
    new_content = head + '\n\n' + new_block + '\n\n' + tail

    # Optional hook (off by default)
    new_content = maybe_run_hook(new_content, str(input_path))

    output_path = args.output or str(input_path)
    write_file(output_path, new_content)


if __name__ == '__main__':
    main()