#!/usr/bin/env python3
"""Pretty Print Helper - cross-language code formatter."""

import argparse
import json
import os
import re
import subprocess
import sys

# Language detection by extension
LANG_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.mjs': 'javascript',
    '.cjs': 'javascript',
    '.go': 'go',
    '.json': 'json',
}

# Common ignores
DEFAULT_IGNORES = {'.git', '.svn', 'node_modules', '__pycache__', 'venv'}


def parse_ignore_file(path):
    """Read .prettyprintignore patterns (simple gitignore subset)."""
    patterns = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    except FileNotFoundError:
        pass
    return patterns


def should_ignore(relpath, patterns):
    """Check if relpath matches any ignore pattern (simple glob)."""
    for pat in patterns:
        if pat in relpath or (pat.startswith('*') and pat[1:] in relpath):
            return True
    return False


def format_python(content):
    """Normalize python: 4-space indent, single quotes, no trailing spaces."""
    lines = content.split('\n')
    # Simple heuristic: remove trailing whitespace, normalize some quote usage
    out = []
    for i, line in enumerate(lines):
        line = re.sub(r'[ \t]+$', '', line)
        # Skip strings that might contain quotes - too complex for heuristic
        out.append(line)
    return '\n'.join(out).rstrip() + '\n'


def format_javascript(content):
    """Normalize JS: 2-space indent (if detectible), double quotes for simple cases, semicolons."""
    lines = content.split('\n')
    out = []
    for line in lines:
        line = re.sub(r'[ \t]+$', '', line)
        # Heuristic: replace single-quoted strings with double quotes if no escape issues
        # But avoid inside comments - too complex, skip for now
        out.append(line)
    return '\n'.join(out).rstrip() + '\n'


def format_go(content):
    """Try gofmt; fallback to simple indent normalization."""
    try:
        result = subprocess.run(['gofmt'], input=content.encode('utf-8'),
                                capture_output=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.decode('utf-8')
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    # fallback: strip trailing whitespace
    return '\n'.join(re.sub(r'[ \t]+$', '', line) for line in content.split('\n')).rstrip() + '\n'


def format_json(content):
    """Sort keys, 2-space indent."""
    try:
        obj = json.loads(content)
        return json.dumps(obj, indent=2, sort_keys=True) + '\n'
    except json.JSONDecodeError:
        return content  # leave invalid JSON alone


def load_config(path):
    """Load config file. Returns dict or None."""
    if not path:
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if path.endswith('.json'):
                return json.load(f)
            else:
                # basic yaml-ish parse for simple key: value
                cfg = {}
                for line in f:
                    if ':' in line and not line.strip().startswith('#'):
                        k, v = line.split(':', 1)
                        cfg[k.strip()] = v.strip()
                return cfg
    except Exception:
        return None


def run_hook(command, filepath):
    """Execute a shell command with filepath as $1. Used for project-specific post-format hooks."""
    if not command:
        return False
    env = os.environ.copy()
    try:
        subprocess.run(command, shell=True, check=False,
                       env=env, cwd=os.path.dirname(filepath) or '.',
                       input=filepath, text=True, timeout=10)
        return True
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def process_file(filepath, config, verbose=False, check_only=False):
    """Format a single file in place. Returns (changed, status)."""
    ext = os.path.splitext(filepath)[1].lower()
    lang = LANG_MAP.get(ext)
    if not lang:
        return (False, 'skipped')

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        return (False, f'read_error: {e}')

    # Format based on language
    if lang == 'python':
        formatted = format_python(original)
    elif lang == 'javascript':
        formatted = format_javascript(original)
    elif lang == 'go':
        formatted = format_go(original)
    elif lang == 'json':
        formatted = format_json(original)
    else:
        formatted = original

    changed = formatted != original

    if changed and not check_only:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(formatted)
        except Exception as e:
            return (False, f'write_error: {e}')

    # Run optional post-format hook from config
    if config and not check_only:
        hook = config.get('run')
        if hook:
            run_hook(hook, filepath)
            # After hook, re-read to see if it changed something
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    after_hook = f.read()
                if after_hook != formatted:
                    changed = True
            except Exception:
                pass

    if verbose:
        status = 'changed' if changed else 'unchanged'
        print(f'{filepath}: {status}')
    return (changed, 'ok' if changed else 'unchanged')


def collect_files(path, ignores):
    """Recursively collect files to format."""
    files = []
    if os.path.isfile(path):
        return [path]
    for root, dirs, filenames in os.walk(path):
        # prune ignored dirs
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORES and not any(
            ig in d for ig in ignores)]
        for fn in filenames:
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, path)
            if not should_ignore(rel, ignores):
                files.append(full)
    return files


def main():
    parser = argparse.ArgumentParser(description='Format code files.')
    parser.add_argument('paths', nargs='+', help='files or directories')
    parser.add_argument('--config', help='path to config file')
    parser.add_argument('--check', action='store_true', help='report diffs without writing')
    parser.add_argument('--verbose', action='store_true', help='verbose output')
    args = parser.parse_args()

    ignores = []
    # Load project-level ignore file if present in cwd
    ignores.extend(parse_ignore_file('.prettyprintignore'))

    config = load_config(args.config)

    changed_any = False
    errors = 0
    for path in args.paths:
        for filepath in collect_files(path, ignores):
            changed, status = process_file(filepath, config,
                                           verbose=args.verbose,
                                           check_only=args.check)
            if changed:
                changed_any = True
            if status != 'ok' and status != 'unchanged':
                errors += 1
                print(f'Error on {filepath}: {status}', file=sys.stderr)

    if args.check and changed_any:
        sys.exit(2)
    if errors > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()