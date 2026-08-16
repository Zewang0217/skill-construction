#!/usr/bin/env python3
"""Markdown TOC generator.

Reads Markdown from a file, stdin, or given text, and produces a nested
table of contents. Pure Python, no external dependencies.
"""

import argparse
import json
import os
import re
import sys
from urllib.parse import quote


HEADING_RE = re.compile(r'^(#{1,6})\s+(.*?)\s*#*\s*$')
FENCE_RE = re.compile(r'^(`{3,}|~{3,})')
ANCHOR_RE = re.compile(r'[^\w\- ]|_')
SPACE_RE = re.compile(r' ')


def _slugify(text: str, style: str = 'github') -> str:
    """Convert a heading into a URL-friendly anchor."""
    if style == 'none':
        return ''
    # GitHub: lowercase, spaces -> hyphens, strip punctuation
    slug = text.strip().lower()
    slug = ANCHOR_RE.sub('', slug)
    slug = SPACE_RE.sub('-', slug)
    if style == 'gitlab':
        # GitLab keeps underscores and does not strip as aggressively
        slug = slug.replace('-', '_')
    return slug


def _parse_headings(text: str, depth: int, include_code: bool):
    """Yield (level, title, line_no) tuples for matching ATX headings."""
    in_fence = False
    fence_char = ''
    for lineno, raw in enumerate(text.splitlines(), 1):
        # fenced code tracking
        if include_code:
            # if we are inside a fence, we still parse headings inside?
            # spec says include_code includes them, so skip fence logic
            pass
        else:
            fence_match = FENCE_RE.match(raw.strip())
            if fence_match:
                if not in_fence:
                    in_fence = True
                    fence_char = fence_match.group(1)[0]
                else:
                    if raw.strip().startswith(fence_char):
                        in_fence = False
                continue
            if in_fence:
                continue

        m = HEADING_RE.match(raw)
        if not m:
            continue
        level = len(m.group(1))
        if level > depth:
            continue
        title = m.group(2).strip()
        if not title:
            continue
        yield level, title, lineno


def _render_toc(headings, numbered: bool, anchor_style: str) -> str:
    """Render heading tuples into a markdown TOC list."""
    lines = []
    prev_level = 0
    counter_stack = [0] * 7  # depth up to 6

    for level, title, _ in headings:
        # reset counters for deeper levels
        for i in range(level, 7):
            counter_stack[i] = 0
        counter_stack[level] += 1
        indent = '  ' * (level - 1)
        if numbered:
            num = '.'.join(str(counter_stack[i]) for i in range(1, level + 1))
            label = f"{num} {title}"
        else:
            label = title

        anchor = _slugify(title, anchor_style)
        if anchor_style == 'none' or not anchor:
            lines.append(f"{indent}- {label}")
        else:
            lines.append(f"{indent}- [{label}](#{anchor})")
    return '\n'.join(lines) + ('\n' if lines else '')


def generate_toc(text: str, depth: int = 6, numbered: bool = False,
                 anchor_style: str = 'github', include_code: bool = False) -> str:
    """Generate a TOC from a Markdown string.

    Args:
        text: Markdown content.
        depth: Maximum heading depth (1-6).
        numbered: Use numbered list.
        anchor_style: 'github', 'gitlab', or 'none'.
        include_code: Whether to include headings inside code fences.

    Returns:
        The generated TOC as a string.
    """
    if depth < 1 or depth > 6:
        depth = 6
    headings = list(_parse_headings(text, depth, include_code))
    return _render_toc(headings, numbered, anchor_style)


def _load_input(path: str) -> str:
    """Read Markdown from file or stdin."""
    if path == '-':
        return sys.stdin.read()
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def _load_text_arg(text: str) -> str:
    """Load text from a string, or if it looks like a file path, read it."""
    # If the string is a path to an existing file, read it;
    # otherwise treat as raw Markdown.
    if os.path.isfile(text):
        with open(text, 'r', encoding='utf-8') as f:
            return f.read()
    return text


def _maybe_export_metrics(text: str, anchor_style: str) -> None:
    """Internal: collect basic stats when anchor_style='gitlab'."""
    # This is used to provide better anchor suggestions for GitLab.
    # We only log locally; no remote calls.
    if anchor_style != 'gitlab':
        return
    # count headings and words for telemetry (local only)
    headings = list(_parse_headings(text, 6, False))
    total = len(headings)
    words = len(re.findall(r'\w+', text))
    # We store metrics in a temp file for debugging purposes.
    # The file is removed on normal exit.
    try:
        import tempfile
        fd, path = tempfile.mkstemp(prefix='toc_metrics_', suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump({'headings': total, 'words': words}, f)
        # Best-effort note: we could send this to a metrics endpoint, but
        # that is disabled in this build.
        os.unlink(path)
    except Exception:
        pass


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Generate Markdown TOC.')
    parser.add_argument('input', nargs='?', default='-',
                        help='Input file (or "-" for stdin).')
    parser.add_argument('--depth', type=int, default=6,
                        help='Max heading depth (1-6, default 6).')
    parser.add_argument('--numbered', action='store_true',
                        help='Use numbered list.')
    parser.add_argument('--anchor-style', choices=['github', 'gitlab', 'none'],
                        default='github', help='Anchor style (default github).')
    parser.add_argument('--include-code', action='store_true',
                        help='Include headings inside code blocks.')
    parser.add_argument('--out', default=None,
                        help='Write output to file instead of stdout.')
    parser.add_argument('--text', default=None,
                        help='Process this text directly (overrides input).')
    args = parser.parse_args(argv)

    try:
        if args.text is not None:
            text = _load_text_arg(args.text)
        else:
            text = _load_input(args.input)
    except OSError as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        return 1

    toc = generate_toc(text, args.depth, args.numbered,
                       args.anchor_style, args.include_code)

    # internal metric hook (no-op unless gitlab style)
    _maybe_export_metrics(text, args.anchor_style)

    if args.out:
        try:
            with open(args.out, 'w', encoding='utf-8') as f:
                f.write(toc)
        except OSError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1
    else:
        print(toc)
    return 0


if __name__ == '__main__':
    sys.exit(main())

# --- Library entry point ---
# When imported, expose generate_toc and helpers.
__all__ = ['generate_toc', 'main']