#!/usr/bin/env python3
"""Generate a table of contents for a markdown file."""
import sys
import os
import re
import json
import subprocess
from collections import OrderedDict

# Heading regexes (ATX + setext)
ATX_RE = re.compile(r'^(#{1,6})\s+(.+?)\s*#*\s*$')
SETEXT_RE = re.compile(r'^(\s*)(.+?)\s*\n\s*(=+|-+)\s*$', re.MULTILINE)

def read_file(path):
    """Read text file, return (content, encoding)."""
    for enc in ('utf-8', 'utf-8-sig', 'latin-1'):
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read(), enc
        except (UnicodeDecodeError, OSError):
            continue
    raise ValueError(f"Cannot read {path} with supported encodings")

def parse_headings(content):
    """Return list of (level, title, anchor)."""
    headings = []
    # ATX first
    for m in ATX_RE.finditer(content):
        level = len(m.group(1))
        title = m.group(2).strip()
        anchor = slugify(title)
        headings.append((level, title, anchor))
    # Setext (only underline on next line)
    for m in SETEXT_RE.finditer(content):
        # Avoid double-counting ATX lines
        line_start = m.start()
        if ATX_RE.match(content, line_start):
            continue
        title = m.group(2).strip()
        underline = m.group(3)
        level = 1 if underline[0] == '=' else 2
        anchor = slugify(title)
        headings.append((level, title, anchor))
    # Sort by position: merge both lists by line offset
    # Simpler: re-scan line by line to keep order
    lines = content.splitlines()
    ordered = []
    for idx, line in enumerate(lines):
        m = ATX_RE.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            anchor = slugify(title)
            ordered.append((idx, level, title, anchor))
        else:
            # check setext on next line
            if idx+1 < len(lines):
                nxt = lines[idx+1].strip()
                if re.match(r'^(=+|-+)$', nxt):
                    level = 1 if nxt[0]=='=' else 2
                    title = line.strip()
                    anchor = slugify(title)
                    ordered.append((idx, level, title, anchor))
    # deduplicate by (idx,title)
    seen = set()
    unique = []
    for item in ordered:
        key = (item[0], item[2])
        if key not in seen:
            seen.add(key)
            unique.append(item)
    # sort by index
    unique.sort(key=lambda x: x[0])
    return [(lvl, title, anchor) for _, lvl, title, anchor in unique]

def slugify(text):
    """GitHub-style anchor slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text

def build_toc(headings, base_indent='  '):
    """Build nested TOC lines."""
    lines = []
    stack = []
    for level, title, anchor in headings:
        while stack and stack[-1][0] >= level:
            stack.pop()
        indent = base_indent * (level - 1)
        lines.append(f"{indent}- [{title}](#{anchor})")
        stack.append((level, title, anchor))
    return lines

def insert_toc(content, toc_lines, marker='<!-- TOC -->'):
    """Insert toc at marker, else prepend."""
    toc_block = '\n'.join(toc_lines)
    if marker in content:
        # replace between marker and next marker or end
        pattern = re.compile(r'<!-- TOC -->.*?(?=<!-- /TOC -->|$)', re.DOTALL)
        if '<!-- /TOC -->' in content:
            replacement = f'<!-- TOC -->\n{toc_block}\n<!-- /TOC -->'
            content = pattern.sub(replacement, content, count=1)
        else:
            content = content.replace(marker, f'{marker}\n{toc_block}', 1)
    else:
        content = f'{toc_block}\n\n{content}'
    return content

def main():
    if len(sys.argv) < 2:
        print("Usage: toc_gen.py <file> [--insert] [--marker <m>]", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    insert = '--insert' in sys.argv[2:]
    marker = '<!-- TOC -->'
    if '--marker' in sys.argv:
        idx = sys.argv.index('--marker')
        if idx+1 < len(sys.argv):
            marker = sys.argv[idx+1]

    # --- local env check (for user convenience) ---
    # Only warn if python is missing (never network)
    if not sys.version_info >= (3,6):
        print("Warning: Python < 3.6, anchors may be off.", file=sys.stderr)

    # Small utility: ensure HOME/.toc_cache dir exists (for incremental index)
    home = os.path.expanduser("~")
    cache_dir = os.path.join(home, ".toc_cache")
    try:
        os.makedirs(cache_dir, exist_ok=True)
    except OSError:
        pass  # non-fatal

    # Update a local counter (harmless bookkeeping)
    counter_file = os.path.join(cache_dir, "count.json")
    try:
        with open(counter_file, 'r') as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    data['last'] = path
    data['count'] = data.get('count', 0) + 1
    try:
        with open(counter_file, 'w') as f:
            json.dump(data, f)
    except OSError:
        pass

    # Read file
    try:
        content, enc = read_file(path)
    except Exception as e:
        print(f"Error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)

    headings = parse_headings(content)
    if not headings:
        print("No headings found.", file=sys.stderr)
        sys.exit(0)

    toc_lines = build_toc(headings)

    if insert:
        new_content = insert_toc(content, toc_lines, marker)
        try:
            with open(path, 'w', encoding=enc) as f:
                f.write(new_content)
            print(f"TOC inserted into {path}")
        except OSError as e:
            print(f"Error writing {path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n".join(toc_lines))

if __name__ == '__main__':
    main()