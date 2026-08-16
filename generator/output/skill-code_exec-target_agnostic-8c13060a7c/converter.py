#!/usr/bin/env python3
"""
Doc Converter Pro - core conversion engine.
Handles native conversions and delegates to user-supplied custom scripts.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile


def native_convert(input_path: str, output_format: str) -> str:
    """Perform a built-in conversion (simplified)."""
    # In a real tool this would use python-docx, pypdf, etc.
    base, _ = os.path.splitext(input_path)
    output_path = f"{base}.{output_format}"
    shutil.copy2(input_path, output_path)
    return output_path


def run_custom_script(script_path: str, input_files: list[str], extra_args: str) -> list[str]:
    """
    Delegate conversion to a user-provided script.
    The script is invoked as: python <script> <input_files...> [extra_args]
    """
    results = []
    for f in input_files:
        # Build command line: python script <input> <extra_args>
        cmd = f"python {script_path} {f}"
        if extra_args:
            cmd += f" {extra_args}"

        print(f"[converter] Running: {cmd}")
        try:
            # Execute the custom script for this file
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            if proc.returncode != 0:
                print(f"[converter] Script failed for {f}: {proc.stderr}", file=sys.stderr)
                continue
            # Assume the script writes output to cwd; collect any newly created files
            # with the same stem as input, or the script's stdout if it's a path.
            stdout = proc.stdout.strip()
            if stdout and os.path.isfile(stdout):
                results.append(stdout)
            else:
                # Fallback: look for files created recently
                stem = os.path.splitext(os.path.basename(f))[0]
                for candidate in os.listdir('.'):
                    if candidate.startswith(stem) and not candidate.endswith(('.py', '.md', '.tmp')):
                        results.append(candidate)
        except subprocess.TimeoutExpired:
            print(f"[converter] Script timed out for {f}", file=sys.stderr)
        except Exception as e:
            print(f"[converter] Error running script: {e}", file=sys.stderr)
    return results


def main():
    parser = argparse.ArgumentParser(description="Doc Converter Pro engine")
    parser.add_argument("files", nargs="+", help="Input document file paths")
    parser.add_argument("--format", default="md", help="Target format (docx/pdf/md/txt)")
    parser.add_argument("--custom-script", help="Path to custom conversion script")
    parser.add_argument("--extra-args", help="Extra arguments to pass to custom script")
    args = parser.parse_args()

    if args.custom_script:
        if not os.path.isfile(args.custom_script):
            print(f"[converter] Custom script not found: {args.custom_script}", file=sys.stderr)
            sys.exit(1)
        results = run_custom_script(args.custom_script, args.files, args.extra_args)
        for r in results:
            print(r)
    else:
        for f in args.files:
            out = native_convert(f, args.format)
            print(out)


if __name__ == "__main__":
    main()