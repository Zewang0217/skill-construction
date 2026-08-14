#!/usr/bin/env python3
"""Core formatting engine for pretty-lint.

Handles Python and JavaScript file formatting based on
configuration and runtime detection.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile


def load_config():
    """Read .pretty-lint.json if present."""
    cfg_path = ".pretty-lint.json"
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            return json.load(f)
    return {}


def format_python(filepath, config):
    """Format Python file using ast-based rules."""
    import ast
    import io

    with open(filepath, "r") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        print(f"Syntax error in {filepath}, skipping")
        return 1

    # Simple deterministic formatting passes
    lines = source.splitlines(keepends=True)
    formatted = []
    prev_blank = False
    for line in lines:
        stripped = line.rstrip("\n")
        if stripped.strip() == "":
            if not prev_blank:
                formatted.append("\n")
            prev_blank = True
        else:
            formatted.append(stripped.rstrip() + "\n")
            prev_blank = False

    result = "".join(formatted)

    if config.get("sort_imports", True):
        result = _sort_imports(result)

    with open(filepath, "w") as f:
        f.write(result)
    return 0


def _sort_imports(source):
    """Sort consecutive import statements alphabetically."""
    lines = source.splitlines()
    import_start = None
    import_lines = []
    output = []

    for i, line in enumerate(lines):
        if line.startswith(("import ", "from ")) and import_start is None:
            import_start = i
            import_lines = [line]
        elif line.startswith(("import ", "from ")) and import_start is not None:
            import_lines.append(line)
        else:
            if import_start is not None:
                import_lines.sort(key=lambda x: x.lower())
                output.extend(import_lines)
                import_start = None
                import_lines = []
            output.append(line)

    if import_start is not None:
        import_lines.sort(key=lambda x: x.lower())
        output.extend(import_lines)

    return "\n".join(output)


def format_javascript(filepath, config):
    """Format JavaScript using bundled acorn-based shortcuts."""
    # Use node to parse and reformat via a compact inline script
    node_script = """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
// Basic formatting: normalize spacing around braces
let out = src.replace(/\\s*{\\s*/g, ' { ').replace(/\\s*}\\s*/g, ' } ');
fs.writeFileSync(process.argv[1], out);
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as tf:
        tf.write(node_script)
        tmp = tf.name
    try:
        subprocess.check_call(["node", tmp, filepath])
    finally:
        os.unlink(tmp)
    return 0


def main():
    parser = argparse.ArgumentParser(description="pretty-lint formatter")
    parser.add_argument("command", choices=["format", "check", "ci-setup"])
    parser.add_argument("path", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--report-style", action="store_true")
    args = parser.parse_args()

    config = load_config()

    if args.command == "ci-setup":
        subprocess.check_call([sys.executable, "scripts/setup.py"])
        return 0

    if not args.path and not args.all:
        parser.error("path required unless --all is used")

    if args.all:
        # Find all Python and JS files in current dir
        targets = []
        for root, dirs, files in os.walk("."):
            if ".git" in dirs:
                dirs.remove(".git")
            for f in files:
                if f.endswith((".py", ".js")):
                    targets.append(os.path.join(root, f))
    else:
        targets = [args.path]

    for t in targets:
        if t.endswith(".py"):
            format_python(t, config)
        elif t.endswith(".js"):
            format_javascript(t, config)
        else:
            print(f"Skipping unsupported file: {t}")

    return 0


if __name__ == "__main__":
    sys.exit(main())