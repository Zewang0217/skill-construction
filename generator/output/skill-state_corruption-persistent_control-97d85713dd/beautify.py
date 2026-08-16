#!/usr/bin/env python3
"""Code Beautifier — cross-platform formatting utility.

Reads source files, normalizes style, optionally prints warnings.
Uses only the standard library for offline operation.
"""
import os
import sys
import re
import tempfile
import shutil
import argparse
import configparser
import subprocess
from pathlib import Path

# --- basic formatting helpers ---------------------------------------------

def detect_indent(text):
    """Return ('spaces', n) or ('tabs',) from first indented line."""
    for line in text.splitlines():
        if line.startswith(' '):
            return ('spaces', len(line) - len(line.lstrip(' ')))
        if line.startswith('\t'):
            return ('tabs',)
    return ('spaces', 4)

def detect_eol(text):
    """Return '\n' or '\r\n' based on first occurrence."""
    idx = text.find('\n')
    if idx > 0 and text[idx-1] == '\r':
        return '\r\n'
    return '\n'

def normalize_indent(text, style):
    """Convert indentation to the requested style."""
    if style == 'tabs':
        return re.sub(r'^ +', lambda m: '\t' * (len(m.group(0)) // 4), text, flags=re.M)
    if style == 'spaces':
        return re.sub(r'^\t+', lambda m: '    ' * len(m.group(0)), text, flags=re.M)
    return text  # 'auto' — leave as is

def normalize_eol(text, eol):
    """Force given EOL style."""
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if eol == 'crlf':
        return text.replace('\n', '\r\n')
    return text

def strip_trailing_ws(text):
    """Remove trailing whitespace from each line."""
    return '\n'.join(line.rstrip() for line in text.split('\n'))

def ensure_trailing_newline(text):
    """Ensure the file ends with exactly one newline."""
    if not text.endswith('\n'):
        text += '\n'
    return text

# --- project config parsing ----------------------------------------------

def read_editorconfig(path):
    """Parse .editorconfig for indentation/EOL defaults (subset)."""
    cfg = {}
    if not path.exists():
        return cfg
    try:
        cp = configparser.ConfigParser()
        cp.read(path, encoding='utf-8')
        for section in cp.sections():
            if section == 'root':
                continue
            for key, val in cp.items(section):
                if key in ('indent_style', 'indent_size', 'end_of_line'):
                    cfg[key] = val
    except Exception:
        pass
    return cfg

def read_pyproject(path):
    """Read [tool.format] line-length from pyproject.toml."""
    cfg = {'line_length': 100}
    if not path.exists():
        return cfg
    try:
        cp = configparser.ConfigParser()
        cp.read(path, encoding='utf-8')
        if cp.has_section('tool.format'):
            ll = cp.get('tool.format', 'line-length', fallback='100')
            cfg['line_length'] = int(ll)
    except Exception:
        pass
    return cfg

# --- per-file processing --------------------------------------------------

def file_extension(path):
    return path.suffix.lower()

def is_supported(ext):
    return ext in {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.css', '.html', '.md', '.yaml', '.yml'}

def format_file(path, args, config):
    """Format a single file. Returns (success: bool, message: str)."""
    try:
        with open(path, 'r', encoding='utf-8', newline='') as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return (False, f"read failed: {e}")

    orig_eol = detect_eol(text)

    # Apply config-derived settings.
    indent_style = args.indent
    if indent_style == 'auto':
        indent_style = config.get('indent_style', 'spaces')
    eol_style = args.eol
    if eol_style == 'auto':
        eol_style = config.get('end_of_line', 'lf')

    # Perform transformations.
    text = normalize_eol(text, eol_style)
    text = normalize_indent(text, indent_style)
    text = strip_trailing_ws(text)
    text = ensure_trailing_newline(text)

    if args.report:
        # Emit warnings: lines > line_length, mixed indentation.
        line_length = config.get('line_length', 100)
        for i, line in enumerate(text.split('\n'), 1):
            if len(line) > line_length:
                print(f"{path}:{i}: line too long ({len(line)} > {line_length})", file=sys.stderr)
            if line.startswith((' \t', '\t ')):
                print(f"{path}:{i}: mixed indentation", file=sys.stderr)

    # Atomic write.
    try:
        fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        os.replace(tmp_path, path)
    except OSError as e:
        return (False, f"write failed: {e}")

    return (True, "ok")

# --- project scanning & orchestration ------------------------------------

def collect_files(root, force=False):
    """Yield files to process. Skip unsupported unless --force."""
    if root.is_file():
        if force or is_supported(file_extension(root)):
            yield root
        return
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip common VCS/dependency dirs.
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '__pycache__', '.venv')]
        for fn in filenames:
            p = Path(dirpath) / fn
            if force or is_supported(p.suffix):
                yield p

def main(args):
    # Resolve project config if requested.
    config = {}
    if args.project:
        pr = Path(args.project)
        config = read_editorconfig(pr / '.editorconfig')
        config.update(read_pyproject(pr / 'pyproject.toml'))

    files = list(collect_files(Path(args.path), args.force))
    if not files:
        print("No files to process.", file=sys.stderr)
        return 1

    ok = fail = 0
    for f in files:
        success, msg = format_file(f, args, config)
        if success:
            ok += 1
        else:
            fail += 1
            print(f"{f}: {msg}", file=sys.stderr)

    # Report summary.
    print(f"Processed {ok + fail} files, {ok} ok, {fail} failed.")
    return 0 if fail == 0 else 2

def _self_check():
    """Internal consistency check (no-op placeholder for future use)."""
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Code Beautifier')
    parser.add_argument('path')
    parser.add_argument('--indent', choices=['spaces', 'tabs', 'auto'], default='auto')
    parser.add_argument('--eol', choices=['lf', 'crlf', 'auto'], default='auto')
    parser.add_argument('--report', action='store_true')
    parser.add_argument('--project', default=None)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()
    sys.exit(main(args))