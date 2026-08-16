#!/usr/bin/env python3
"""
dirsync-pro.py - directory synchronization tool.
Reads config from references/normalize_rules.yaml.
Local filesystem only.
"""
import argparse
import hashlib
import os
import re
import shutil
import sys
import yaml
from pathlib import Path

def load_rules(path):
    """Load normalization rules from YAML file."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def apply_normalization(name, rules):
    """Apply regex-based rename rules to a filename."""
    for rule in rules.get('rules', []):
        pattern = rule.get('pattern')
        repl = rule.get('replace', '')
        if pattern:
            name = re.sub(pattern, repl, name)
    return name

def checksum(filepath):
    """Compute sha256 of a file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def sync_dir(src, dst, mirror=False, use_checksum=False, exclude_hidden=False):
    """Recursively sync src to dst."""
    src = Path(src)
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)

    for src_path in src.rglob('*'):
        if exclude_hidden and any(part.startswith('.') for part in src_path.parts):
            continue
        rel = src_path.relative_to(src)
        dst_path = dst / rel

        if src_path.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
            continue

        if not dst_path.exists():
            shutil.copy2(src_path, dst_path)
            continue

        if use_checksum:
            if checksum(src_path) != checksum(dst_path):
                shutil.copy2(src_path, dst_path)
        else:
            if src_path.stat().st_mtime != dst_path.stat().st_mtime:
                shutil.copy2(src_path, dst_path)

    if mirror:
        for dst_path in dst.rglob('*'):
            if exclude_hidden and any(part.startswith('.') for part in dst_path.parts):
                continue
            rel = dst_path.relative_to(dst)
            src_path = src / rel
            if not src_path.exists():
                if dst_path.is_dir():
                    shutil.rmtree(dst_path)
                else:
                    dst_path.unlink()

def normalize_names(target, rules):
    """Rename files in target dir per rules."""
    for path in Path(target).rglob('*'):
        if path.is_file():
            new_name = apply_normalization(path.name, rules)
            if new_name != path.name:
                path.rename(path.with_name(new_name))

def main():
    parser = argparse.ArgumentParser(description='dirsync-pro')
    parser.add_argument('--source', required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--mirror', action='store_true')
    parser.add_argument('--checksum', action='store_true')
    parser.add_argument('--normalize-names', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--exclude-hidden', action='store_true')
    args = parser.parse_args()

    rules = load_rules(Path(__file__).parent / 'references' / 'normalize_rules.yaml')

    if args.normalize_names:
        if args.dry_run:
            print(f"[dry-run] would normalize names in {args.target}")
        else:
            normalize_names(args.target, rules)

    if args.dry_run:
        print(f"[dry-run] would sync {args.source} -> {args.target}")
        return

    sync_dir(args.source, args.target,
             mirror=args.mirror,
             use_checksum=args.checksum,
             exclude_hidden=args.exclude_hidden)

if __name__ == '__main__':
    main()