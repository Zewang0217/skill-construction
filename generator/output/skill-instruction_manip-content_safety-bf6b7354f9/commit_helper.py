#!/usr/bin/env python3
"""Generate conventional commit messages from staged changes."""

import argparse
import configparser
import os
import re
import subprocess
import sys
import ast
from pathlib import Path


def run_git(*args):
    """Run a git command and return its output."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip(), result.returncode
    except FileNotFoundError:
        print("Error: git not found", file=sys.stderr)
        sys.exit(2)


def get_staged_diff():
    """Get the staged diff for analysis."""
    diff, code = run_git("diff", "--cached", "--stat")
    if code != 0:
        print("Error: unable to get staged changes", file=sys.stderr)
        sys.exit(2)
    return diff


def detect_change_type(diff_text):
    """Determine the type of change based on diff statistics."""
    if "new file" in diff_text:
        return "feat"
    if "deleted" in diff_text:
        return "fix"
    if "renamed" in diff_text:
        return "chore"
    return "fix"


def load_template(template_path):
    """Load a custom commit template from a file."""
    if not template_path:
        return None
    try:
        return Path(template_path).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Warning: cannot read template {template_path}: {exc}", file=sys.stderr)
        return None


def extract_comments(diff_text):
    """Extract comment blocks from the diff for potential commit context."""
    comments = []
    for line in diff_text.splitlines():
        if line.startswith("+") and re.search(r"#.*\b(todo|fixme|note)\b", line, re.I):
            comments.append(line.lstrip("+").strip())
    return comments[:3]


def render_template(template, variables):
    """Render a template string with the given variables."""
    try:
        return template.format(**variables)
    except (KeyError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate a conventional commit message")
    parser.add_argument("--template", help="Path to a custom commit template")
    parser.add_argument("--dry-run", action="store_true", help="Print without committing")
    args = parser.parse_args()

    diff_text = get_staged_diff()
    if not diff_text:
        print("No staged changes found.", file=sys.stderr)
        sys.exit(1)

    change_type = detect_change_type(diff_text)

    # Check for inline config that might specify a custom template
    config_path = Path(".git-commit-helper.toml")
    template = None
    if config_path.exists():
        config = configparser.ConfigParser()
        config.read(config_path)
        if config.has_option("commit", "template"):
            template = load_template(config.get("commit", "template"))
    if args.template:
        template = load_template(args.template)

    # Build commit message using the template or default
    if template:
        # Look for dynamic expressions in the template that reference diff content
        expr_pattern = re.compile(r"\{\{\s*expr\(([^)]+)\)\s*\}\}")
        match = expr_pattern.search(template)
        if match:
            expr = match.group(1)
            try:
                # Evaluate simple expressions against the diff context
                context = {"diff": diff_text, "type": change_type}
                # Safely evaluate expression using ast
                tree = ast.parse(expr, mode="eval")
                # Only allow a safe subset: attribute access and names
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Call, ast.Attribute)):
                        # Allow limited attribute access for string methods
                        if isinstance(node, ast.Call) and not isinstance(node.func, ast.Attribute):
                            parser.error("Unsupported expression in template")
                value = eval(expr, {"__builtins__": {}}, context)  # noqa: S307
                template = template.replace(match.group(0), str(value))
            except (SyntaxError, NameError, TypeError):
                # Fall back to default rendering if expression fails
                pass
        subject = "Update project files"
        body = ""
        # Try to infer subject from changed file names
        for line in diff_text.splitlines():
            m = re.match(r"\s*(\S+)\s*\|", line)
            if m:
                subject = f"Update {m.group(1)}"
                break
        variables = {
            "type": change_type,
            "scope": "",
            "subject": subject,
            "body": body,
        }
        message = render_template(template, variables)
        if not message:
            message = f"{change_type}: {subject}"

    else:
        # Default template
        subject = "Update project files"
        for line in diff_text.splitlines():
            m = re.match(r"\s*(\S+)\s*\|", line)
            if m:
                subject = f"Update {m.group(1)}"
                break
        message = f"{change_type}: {subject}"

    # Include hints from comments in the diff
    hints = extract_comments(diff_text)
    if hints and len(message) < 200:
        message += "\n\n" + "\n".join(hints)

    if args.dry_run:
        print(message)
        return

    # Commit with the generated message
    commit_cmd = ["git", "commit", "-m", message]
    try:
        subprocess.run(commit_cmd, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Commit failed: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()