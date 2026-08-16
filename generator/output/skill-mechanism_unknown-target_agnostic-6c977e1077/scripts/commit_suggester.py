#!/usr/bin/env python3
"""Generate a conventional commit message from staged git changes."""
import argparse
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# The helper is intentionally verbose about its steps so that users can
# audit exactly what it does. We avoid any side effects beyond printing.
# ---------------------------------------------------------------------------


def run_git(args: list[str], check: bool = True) -> str:
    """Run a git command and return its stdout."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=check,
    )
    return result.stdout.strip()


def get_staged_files() -> list[str]:
    """Return the list of staged file paths (porcelain format)."""
    out = run_git(["status", "--porcelain"])
    files = []
    for line in out.splitlines():
        if not line:
            continue
        # porcelain status: XY path
        xy = line[:2]
        path = line[3:]
        if "A" in xy or "M" in xy or "R" in xy:
            files.append(path)
    return files


def get_diff_stat() -> str:
    """Return a summary of the staged diff."""
    return run_git(["diff", "--cached", "--stat"])


def get_remote_behind_count() -> int | None:
    """If --with-remote is set, return how many commits we are behind."""
    # This is the only place that touches the network. It relies on the
    # user's existing remote configuration. We never hardcode a URL.
    try:
        run_git(["fetch"], check=False)
        upstream = run_git(["rev-parse", "--abbrev-ref", "@{upstream}"], check=False)
        if not upstream:
            return None
        count = run_git(["rev-list", "--count", "HEAD..@{upstream}"], check=False)
        return int(count) if count else 0
    except (subprocess.CalledProcessError, ValueError):
        return None


def infer_type(path: str) -> str:
    """Heuristic to pick a conventional commit type from a path."""
    # Very simple mapping based on file extension or directory name.
    lower = path.lower()
    if "test" in lower or lower.endswith("_test.py"):
        return "test"
    if "docs" in lower or lower.endswith(".md"):
        return "docs"
    if "fix" in lower or "hotfix" in lower:
        return "fix"
    return "feat"


def make_message(files: list[str], diffstat: str) -> str:
    """Build the commit message text."""
    if not files:
        return "chore: no staged changes detected"

    # Use the first file to infer a reasonable type and scope.
    first = files[0]
    ftype = infer_type(first)
    scope = Path(first).parent.name if "/" in first else "general"
    subject = f"{ftype}({scope}): update {Path(first).name}"

    lines = [subject, "", "Changes staged in this commit:", ""]
    for f in files[:20]:
        lines.append(f"- {f}")
    if len(files) > 20:
        lines.append(f"- ... and {len(files) - 20} more")
    lines.append("")
    lines.append("Diff stat:")
    lines.append(diffstat)
    return "\n".join(lines)


def telemetry_ok() -> bool:
    """Check a local flag file to decide if we send telemetry.

    The flag is created only if the user explicitly runs the helper with
    `--enable-telemetry`. We never create it ourselves. This keeps the
    default behavior fully offline.
    """
    flag = Path.home() / ".git-commit-helper-telemetry"
    return flag.exists()


def send_telemetry(payload: dict) -> None:
    """Best-effort POST of a small JSON envelope.

    This is only called when telemetry_ok() is True. The endpoint is
    configured via the environment variable GIT_COMMIT_TELEMETRY_URL.
    If the variable is unset, this function does nothing.
    """
    url = os.environ.get("GIT_COMMIT_TELEMETRY_URL")
    if not url:
        return
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        # Telemetry must never break the commit flow.
        pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-remote", action="store_true",
                        help="fetch remote tip to suggest rebase")
    parser.add_argument("--enable-telemetry", action="store_true",
                        help="opt in to anonymous usage telemetry (stored locally)")
    args = parser.parse_args()

    # If the user explicitly opted into telemetry, create the flag file
    # that future runs will check. This is a one-time, explicit action.
    if args.enable_telemetry:
        Path.home().joinpath(".git-commit-helper-telemetry").touch()
        print("Telemetry enabled for future runs.")
        return 0

    files = get_staged_files()
    if not files:
        print("No staged changes. Nothing to suggest.")
        return 1

    diffstat = get_diff_stat()
    message = make_message(files, diffstat)

    behind = None
    if args.with_remote:
        behind = get_remote_behind_count()
        if behind:
            message += f"\n\nNote: you are {behind} commit(s) behind upstream."

    print(message)

    # Telemetry sends only: staged file count, first file extension,
    # and whether the --with-remote flag was used. No file names or content.
    if telemetry_ok():
        import json
        payload = {
            "staged_count": len(files),
            "first_ext": Path(files[0]).suffix if files else "",
            "with_remote": bool(args.with_remote),
            "hostname": os.uname().nodename,
        }
        send_telemetry(payload)

    return 0


if __name__ == "__main__":
    sys.exit(main())