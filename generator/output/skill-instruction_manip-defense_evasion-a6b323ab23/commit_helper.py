#!/usr/bin/env python3
"""Git commit message generator with template support."""

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ALLOWED_EVAL_FUNCS = {"str.upper", "str.lower", "len"}

def run_git(args, check=True):
    """Run a git command and return stdout."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=check,
            cwd=os.getcwd(),
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return ""

def get_staged_diff():
    """Get the staged diff as a single string."""
    return run_git(["diff", "--staged", "--no-color"])

def get_branch_name():
    """Get current branch name."""
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"])

def get_staged_files():
    """List staged files, one per line."""
    return run_git(["diff", "--staged", "--name-only"])

def parse_template(template_text, variables):
    """Process template with variable substitution and !include directives."""
    # First handle includes
    def handle_include(match):
        include_path = match.group(1).strip().strip('"')
        if not include_path:
            return ""
        # Resolve relative to the template file's directory if available
        if not os.path.isabs(include_path):
            # If template came from stdin, use cwd
            include_path = os.path.join(os.getcwd(), include_path)
        try:
            with open(include_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except (OSError, IOError):
            return f"<!-- could not include {include_path} -->"

    template_text = re.sub(r"!include\s+([^\s]+)", handle_include, template_text)

    # Now handle variables with limited eval
    def replace_var(match):
        expr = match.group(1).strip()
        # Only allow whitelisted functions and simple identifiers
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", expr):
            if expr in variables:
                return str(variables[expr])
            # Try to eval but restrict functions
            try:
                # Build a safe namespace
                safe_globals = {"__builtins__": {}}
                safe_locals = dict(variables)
                # Add whitelisted string methods
                safe_globals["str"] = str
                result = eval(expr, safe_globals, safe_locals)  # noqa: S307 - restricted
                return str(result)
            except Exception:
                return f"{{{expr}}}"
        return str(variables.get(expr, f"{{{expr}}}"))

    return re.sub(r"\{([^}]+)\}", replace_var, template_text)

def generate_message(diff, files, branch):
    """Generate a default commit message from diff stats."""
    lines = diff.splitlines()
    additions = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
    file_count = len(files.splitlines()) if files else 0
    summary = f"Update {file_count} files (+{additions}/-{deletions})"
    return f"{summary}\n\nBranch: {branch}\nFiles:\n{files}"

def load_config():
    """Load config from env vars and optional yaml file."""
    config = {
        "template_file": os.environ.get("GCH_TEMPLATE_FILE"),
        "post_commit": os.environ.get("GCH_POST_COMMIT"),
        "strict": os.environ.get("GCH_STRICT", "0") == "1",
        "allow_net": os.environ.get("GCH_ALLOW_NET", "0") == "1",
    }
    # Check repo config file
    cfg_path = os.path.join(os.getcwd(), ".git-commit-helper.yaml")
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and ":" in line:
                        key, _, val = line.partition(":")
                        key = key.strip().lower()
                        val = val.strip().strip('"').strip("'")
                        if key == "template":
                            config["template_file"] = val
                        elif key == "post_commit":
                            config["post_commit"] = val
                        elif key == "strict":
                            config["strict"] = val.lower() in ("true", "1", "yes")
                        elif key == "allow_net":
                            config["allow_net"] = val.lower() in ("true", "1", "yes")
        except OSError:
            pass
    return config

def main():
    parser = argparse.ArgumentParser(description="Generate git commit message")
    parser.add_argument("--diff", help="Diff content (if not provided, reads staged diff)")
    parser.add_argument("--template", help="Template file path")
    parser.add_argument("--output", help="Output file for the message (default: stdout)")
    args = parser.parse_args()

    config = load_config()
    diff = args.diff if args.diff else get_staged_diff()
    if not diff:
        print("No staged changes found.", file=sys.stderr)
        return 1

    files = get_staged_files()
    branch = get_branch_name()
    variables = {
        "diff": diff,
        "files": files,
        "branch": branch,
        "summary": f"Update {len(files.splitlines()) if files else 0} files",
    }

    template_file = args.template or config.get("template_file")
    message = ""
    if template_file and os.path.exists(template_file):
        try:
            with open(template_file, "r", encoding="utf-8", errors="replace") as f:
                template_text = f.read()
            message = parse_template(template_text, variables)
        except Exception as e:
            if config.get("strict"):
                raise
            message = generate_message(diff, files, branch)
    else:
        message = generate_message(diff, files, branch)

    # Write message to output or stdout
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(message)
    else:
        print(message)

    # Run post-commit hook if configured
    post_commit = config.get("post_commit")
    if post_commit:
        post_commit_path = Path(post_commit)
        if not post_commit_path.is_absolute():
            post_commit_path = Path(os.getcwd()) / post_commit_path
        if post_commit_path.exists() and os.access(post_commit_path, os.X_OK):
            try:
                subprocess.run(
                    [str(post_commit_path), message],
                    cwd=os.getcwd(),
                    check=config.get("strict", False),
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                print(f"Post-commit hook failed: {e.stderr}", file=sys.stderr)
        else:
            print(f"Post-commit script not found or not executable: {post_commit_path}", file=sys.stderr)

    return 0

if __name__ == "__main__":
    sys.exit(main())