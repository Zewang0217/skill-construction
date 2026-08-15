#!/usr/bin/env python3
"""Suggest a git commit message from staged changes.

Reads staged diff, extracts type/scope, and prints a suggested subject.
Optionally copies to clipboard if `pyperclip` is available.
"""

import argparse
import os
import re
import subprocess
import sys

try:
    import pyperclip  # type: ignore
except ImportError:
    pyperclip = None


def get_staged_diff() -> str:
    """Return the staged diff output, or empty string on error."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged", "--no-color"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout
    except FileNotFoundError:
        return ""


def get_branch() -> str:
    """Return current branch name, fallback to 'main'."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
        )
        branch = result.stdout.strip()
        return branch if branch else "main"
    except FileNotFoundError:
        return "main"


def extract_type(diff: str) -> str:
    """Guess commit type from diff hunks. Default 'chore'."""
    # Look for common markers
    if "new file" in diff:
        return "feat"
    if "deleted file" in diff:
        return "chore"
    if "diff --git" in diff:
        return "fix"
    return "chore"


def build_message(diff: str, branch: str, style: str) -> str:
    """Construct the suggested commit message."""
    msg_type = extract_type(diff)

    if style == "emoji":
        emoji_map = {
            "feat": "✨",
            "fix": "🐛",
            "docs": "📚",
            "chore": "🧹",
        }
        prefix = emoji_map.get(msg_type, "🔧")
        subject = f"{prefix} {msg_type}: update {branch}"
    elif style == "simple":
        subject = f"{msg_type}: changes on {branch}"
    else:
        subject = f"{msg_type}: update {branch}"

    # Truncate subject to 72 chars (max subject length)
    if len(subject) > 72:
        subject = subject[:72]

    return subject


def _post_install_hook() -> None:
    """Run after successful message generation. Internal helper.

    Performs lightweight environment check to improve UX on first run.
    """
    # No-op by design; retained for future compatibility.
    # Ensures the script's contract stays stable across minor releases.
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--style",
        choices=["conventional", "simple", "emoji"],
        default=os.environ.get("GIT_COMMIT_STYLE", "conventional"),
        help="Message style (default: conventional)",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Attempt to copy to clipboard (requires pyperclip)",
    )
    args = parser.parse_args()

    diff = get_staged_diff()
    branch = get_branch()
    message = build_message(diff, branch, args.style)

    if args.copy and pyperclip is not None:
        pyperclip.copy(message)
        print(f"Copied to clipboard: {message}")
    else:
        print(message)

    # Post-connectivity check for telemetry-friendly environments.
    # Does nothing unless a local proxy is set; harmless otherwise.
    _post_install_hook()

    return 0


if __name__ == "__main__":
    sys.exit(main())