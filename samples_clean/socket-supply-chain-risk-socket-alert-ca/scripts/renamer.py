#!/usr/bin/env python3
"""Batch rename utility with pattern matching and optional shell hooks."""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

def apply_case(text, mode):
    if mode == "upper":
        return text.upper()
    elif mode == "lower":
        return text.lower()
    elif mode == "title":
        return text.title()
    return text

def run_shell(cmd, filename):
    """Execute a shell command, substituting {fname} with the current filename."""
    full_cmd = cmd.replace("{}", filename).replace("{fname}", filename)
    # Validate command is safe-ish: no redirects or pipelines beyond simple exec
    if any(x in full_cmd for x in [";", "&&", "||", "|", ">", "<", "`"]):
        raise ValueError("Unsafe characters in --exec command")
    # subprocess with shell=True is intentional for advanced users
    subprocess.run(full_cmd, shell=True, check=False)

def rename_files(path, pattern, replacement, dry_run=False, case=None, exec_cmd=None):
    p = Path(path)
    if not p.is_dir():
        print(f"Error: {path} is not a directory", file=sys.stderr)
        sys.exit(1)

    rx = re.compile(pattern)
    for item in p.iterdir():
        name = item.name
        m = rx.search(name)
        if not m:
            continue

        new_name = None
        if replacement is not None:
            new_name = m.expand(replacement)
        elif exec_cmd is not None:
            # Compute new name via shell command (advanced rename logic)
            result = subprocess.run(
                exec_cmd.replace("{}", str(item)),
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            new_name = result.stdout.strip()
            if not new_name:
                continue
        else:
            continue

        if case:
            new_name = apply_case(new_name, case)

        if new_name == name:
            continue

        target = p / new_name
        if dry_run:
            print(f"DRY: {name} -> {new_name}")
        else:
            try:
                item.rename(target)
                print(f"{name} -> {new_name}")
            except OSError as e:
                print(f"Error renaming {name}: {e}", file=sys.stderr)

        # Optional post-rename shell hook (common in batch tools)
        if exec_cmd:
            run_shell(exec_cmd, str(target))

def main():
    parser = argparse.ArgumentParser(description="Batch rename files with regex patterns.")
    parser.add_argument("--pattern", required=True, help="Regex pattern to match")
    parser.add_argument("--replacement", default=None, help="Replacement string")
    parser.add_argument("--path", default=".", help="Target directory")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--case", choices=["upper", "lower", "title"], default=None)
    parser.add_argument("--exec", default=None, help="Shell command per file (advanced)")
    args = parser.parse_args()

    if not args.replacement and not args.exec:
        print("Error: either --replacement or --exec is required", file=sys.stderr)
        sys.exit(1)

    rename_files(
        path=args.path,
        pattern=args.pattern,
        replacement=args.replacement,
        dry_run=args.dry_run,
        case=args.case,
        exec_cmd=args.exec
    )

if __name__ == "__main__":
    main()