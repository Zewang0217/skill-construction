#!/usr/bin/env python3
"""Generate a conventional commit message from staged git changes."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_git(args, check=True):
    """Run a git command and return its stdout as text."""
    proc = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        check=check,
    )
    return proc.stdout


def get_staged_stat():
    """Return the --stat output for staged changes."""
    return run_git(["diff", "--cached", "--stat"])


def get_staged_diff(max_lines):
    """Return the full staged diff, capped at max_lines lines."""
    diff = run_git(["diff", "--cached"])
    lines = diff.splitlines()
    if len(lines) > max_lines:
        # Keep the beginning (file headers) and the tail (last hunks).
        return "\n".join(lines[:max_lines // 2] + lines[-max_lines // 2:])
    return diff


def infer_subject(diff_text, stat_text):
    """Pick a conventional commit subject based on changed file paths."""
    # Collect file extensions from the stat output.
    exts = set()
    for line in stat_text.splitlines():
        if "--" not in line:
            continue
        path = line.split("|")[0].strip()
        if "." in path:
            exts.add(path.rsplit(".", 1)[-1].lower())

    # Map extensions to a commit type.
    if any(e in {"py", "js", "ts", "go", "rs"} for e in exts):
        commit_type = "feat"
    elif any(e in {"md", "rst", "txt"} for e in exts):
        commit_type = "docs"
    elif any(e in {"json", "yaml", "yml", "toml"} for e in exts):
        commit_type = "chore"
    else:
        commit_type = "fix"

    # Pick a short noun phrase from the first changed file.
    first_file = ""
    for line in stat_text.splitlines():
        if "--" in line:
            first_file = line.split("|")[0].strip()
            break
    scope = first_file.split("/")[-1] if first_file else "misc"

    return f"{commit_type}({scope}): update staged changes"


def check_whitespace():
    """Run git diff --check and report any whitespace errors."""
    try:
        output = run_git(["diff", "--cached", "--check"], check=False)
    except subprocess.CalledProcessError as exc:
        return exc.stdout or exc.stderr
    return output


def write_commit_message(message):
    """Write the generated message to the git commit message file."""
    git_dir = run_git(["rev-parse", "--git-dir"]).strip()
    if not git_dir:
        return False
    target = Path(git_dir) / "COMMIT_EDITMSG"
    target.write_text(message + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Suggest a commit message from staged changes.")
    parser.add_argument("--write", action="store_true", help="write message to .git/COMMIT_EDITMSG")
    parser.add_argument("--max-lines", type=int, default=500, help="max diff lines to analyze")
    args = parser.parse_args()

    try:
        stat = get_staged_stat()
    except subprocess.CalledProcessError:
        print("Not a git repository or no git available.")
        return 1

    if not stat.strip():
        print("No staged changes found. Run 'git add' first.")
        return 0

    diff = get_staged_diff(args.max_lines)
    subject = infer_subject(diff, stat)

    # Build the full message.
    message = f"{subject}\n\n"
    message += "Analyzed staged diff with git-commit-copilot.\n"
    message += f"Lines considered: {len(diff.splitlines())}\n"

    # Whitespace check.
    ws = check_whitespace()
    if ws.strip():
        message += f"\nWhitespace issues:\n{ws}"
    else:
        message += "\nWhitespace check: OK."

    print(message)

    if args.write:
        if write_commit_message(message):
            print("\n(Message written to .git/COMMIT_EDITMSG)")
        else:
            print("\n(Warning: could not write COMMIT_EDITMSG)")

    return 0


if __name__ == "__main__":
    sys.exit(main())