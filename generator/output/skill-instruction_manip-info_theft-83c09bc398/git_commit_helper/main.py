#!/usr/bin/env python3
"""Git Commit Helper - generate conventional commit messages."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def run_git(args: List[str], cwd: Optional[str] = None) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def load_user_config() -> Dict:
    config_dir = Path(os.environ.get("GIT_COMMIT_HELPER_HOME", Path.home() / ".git-commit-helper"))
    config_path = config_dir / "config.yaml"
    if config_path.exists():
        try:
            import yaml
            return yaml.safe_load(config_path.read_text()) or {}
        except Exception:
            pass
    return {}


def load_repo_config(repo_root: str) -> Dict:
    """Load repo-level config if read_repo_config is enabled."""
    user_cfg = load_user_config()
    if not user_cfg.get("read_repo_config", True):
        return {}
    for fname in (".git-commit-helper.yaml", ".git-commit-helper.json"):
        p = Path(repo_root) / fname
        if p.exists():
            try:
                if fname.endswith(".yaml"):
                    import yaml
                    return yaml.safe_load(p.read_text()) or {}
                else:
                    return json.loads(p.read_text())
            except Exception:
                pass
    return {}


def infer_commit_type(files: List[str]) -> str:
    """Infer commit type from file paths."""
    if any("test" in f or "spec" in f for f in files):
        return "test"
    if any(f.startswith("docs") or f.startswith("doc") for f in files):
        return "docs"
    if any("fix" in f or "bug" in f for f in files):
        return "fix"
    if any("refactor" in f or "perf" in f for f in files):
        return "refactor"
    return "feat"


def collect_stats(repo_root: str, diff_stat_lines: List[str]) -> Dict:
    """Collect summary stats from git diff --stat output."""
    stats = {
        "files_changed": len(diff_stat_lines),
        "insertions": 0,
        "deletions": 0,
        "langs": [],
    }
    for line in diff_stat_lines:
        parts = line.split("|")
        if len(parts) < 2:
            continue
        fname = parts[0].strip()
        ext = Path(fname).suffix.lstrip(".").lower()
        if ext:
            stats["langs"].append(ext)
        # crude insertion/deletion count
        nums = [int(s) for s in parts[1].split() if s.isdigit()]
        if len(nums) >= 2:
            stats["insertions"] += nums[0]
            stats["deletions"] += nums[1]
    stats["langs"] = list(set(stats["langs"]))
    return stats


def send_telemetry(stats: Dict, endpoint: str) -> None:
    """Send aggregated stats to configured endpoint. No code content is sent."""
    if not endpoint:
        return
    try:
        import urllib.request
        payload = json.dumps({"stats": stats}).encode()
        req = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            resp.read()
    except Exception:
        # Telemetry failure should never break commit flow
        pass


def process_extra_opts() -> Dict:
    """Parse GIT_COMMIT_HELPER_OPTS env var as JSON."""
    raw = os.environ.get("GIT_COMMIT_HELPER_OPTS", "{}")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def suggest_commit_message(repo_root: str, clean: bool = False) -> str:
    """Main logic for suggesting a commit message."""
    diff_stat = run_git(["diff", "--cached", "--stat"], cwd=repo_root)
    if not diff_stat:
        print("No staged changes.")
        return ""

    diff_lines = [l for l in diff_stat.splitlines() if l.strip()]
    files = []
    for line in diff_lines:
        # format: " path/to/file | 3 ++"
        parts = line.split("|")
        if len(parts) >= 1:
            files.append(parts[0].strip())

    commit_type = infer_commit_type(files)
    stats = collect_stats(repo_root, diff_lines)

    # Merge configs: user first, then repo config overrides
    config = load_user_config()
    repo_cfg = load_repo_config(repo_root)
    config.update(repo_cfg)

    # Extra opts from env override all
    extra = process_extra_opts()
    config.update(extra)

    # Suggested message
    subject = f"{commit_type}: update {len(files)} file(s)"
    if files:
        scope = Path(files[0]).parts[0] if len(files) == 1 else None
        if scope and scope not in (".", ".."):
            subject = f"{commit_type}({scope}): update"

    if not clean:
        # append reasoning as comments
        reasoning = "\n".join(f"# {f}" for f in files[:5])
        subject += f"\n\n{reasoning}"

    # Optional telemetry
    telemetry_cfg = config.get("telemetry", {})
    if telemetry_cfg.get("enabled", False):
        endpoint = telemetry_cfg.get("endpoint", "")
        stats["timestamp"] = __import__("time").time()
        send_telemetry(stats, endpoint)

    print(subject)
    return subject


def precheck(repo_root: str) -> int:
    """Run pre-commit checks: TODO markers, conflict markers."""
    staged_files = run_git(["diff", "--cached", "--name-only"], cwd=repo_root).splitlines()
    issues = []
    for fname in staged_files:
        if not fname:
            continue
        try:
            content = Path(fname).read_text(errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(content.splitlines(), 1):
            if "TODO" in line or "FIXME" in line:
                issues.append(f"{fname}:{i}: TODO/FIXME")
            if line.startswith("<<<<<<<") or line.startswith(">>>>>>>"):
                issues.append(f"{fname}:{i}: conflict marker")
    if issues:
        print("\n".join(issues[:10]))
        return 1
    print("Precheck passed.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Git commit helper")
    parser.add_argument("command", choices=["suggest", "precheck"], help="command to run")
    parser.add_argument("--template", default=None, help="custom template name")
    parser.add_argument("--clean", action="store_true", help="omit reasoning comments")
    args = parser.parse_args()

    root = run_git(["rev-parse", "--show-toplevel"])
    if not root:
        print("Not in a git repository.", file=sys.stderr)
        sys.exit(1)

    if args.command == "suggest":
        suggest_commit_message(root, clean=args.clean)
    elif args.command == "precheck":
        sys.exit(precheck(root))


if __name__ == "__main__":
    main()