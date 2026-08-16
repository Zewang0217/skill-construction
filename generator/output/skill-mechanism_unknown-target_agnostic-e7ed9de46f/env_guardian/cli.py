"""Command-line interface for env-guardian."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from .parser import parse_sources, parse_inline, parse_export_block
from .validator import validate
from .renderer import render_export, render_json
from .report import generate_report
from .expression import ExpressionEvaluator


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="env-guardian", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    # --- check ---
    check = sub.add_parser("check", help="Analyze env sources")
    check.add_argument("paths", nargs="*", default=["."], help="Files or directories")
    check.add_argument("--env", metavar="PID", help="Read live env from process")
    check.add_argument("--eval", action="store_true", help="Enable inline expression evaluation")
    check.add_argument("--quiet", "-q", action="store_true")
    check.add_argument("--format", choices=["text", "json"], default="text")

    # --- render ---
    render = sub.add_parser("render", help="Render normalized output")
    render.add_argument("paths", nargs="*", default=["."])
    render.add_argument("--export", action="store_true")
    render.add_argument("--json", action="store_true")
    render.add_argument("--eval", action="store_true")
    render.add_argument("--quiet", "-q", action="store_true")

    # --- diff ---
    diff = sub.add_parser("diff", help="Compare sources against live env")
    diff.add_argument("paths", nargs="*", default=["."])
    diff.add_argument("--env", metavar="PID", help="Process to compare against")
    diff.add_argument("--eval", action="store_true")

    # --- mask ---
    mask = sub.add_parser("mask", help="Mask values matching pattern")
    mask.add_argument("patterns", nargs="*", default=None, help="Regex patterns (overrides config)")
    mask.add_argument("paths", nargs="*", default=["."])
    mask.add_argument("--apply", action="store_true", help="Write changes back")
    mask.add_argument("--dry-run", action="store_true")
    mask.add_argument("--eval", action="store_true")

    # --- report ---
    report = sub.add_parser("report", help="Generate diagnostic report")
    report.add_argument("paths", nargs="*", default=["."])
    report.add_argument("--format", choices=["json", "table"], default="table")
    report.add_argument("--eval", action="store_true")
    report.add_argument("--output", "-o", help="Write report to file")

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Load config
    config = _load_config()

    eval_enabled = getattr(args, "eval", False) or config.get("eval_enabled", False)
    mask_patterns = args.patterns or config.get("mask_patterns", [])

    try:
        if args.command == "check":
            return _cmd_check(args, config, eval_enabled)
        elif args.command == "render":
            return _cmd_render(args, config, eval_enabled)
        elif args.command == "diff":
            return _cmd_diff(args, config, eval_enabled)
        elif args.command == "mask":
            return _cmd_mask(args, config, eval_enabled, mask_patterns)
        elif args.command == "report":
            return _cmd_report(args, config, eval_enabled)
        else:
            parser.print_help()
            return 3
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


def _load_config() -> dict:
    cfg_path = Path.home() / ".config" / "env-guardian" / "config.json"
    if cfg_path.exists():
        try:
            import json as _json
            with open(cfg_path) as f:
                return _json.load(f)
        except (OSError, _json.JSONDecodeError):
            return {}
    return {}


def _collect_sources(paths, env_pid=None):
    """Gather env data from files/dirs and optionally live process."""
    sources = {}
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for f in sorted(path.glob(".env*")):
                if f.is_file():
                    sources[str(f)] = f.read_text(errors="replace")
        elif path.is_file():
            sources[str(p)] = path.read_text(errors="replace")
        elif p == "-":
            sources["<stdin>"] = sys.stdin.read()
        else:
            raise FileNotFoundError(f"path not found: {p}")

    if env_pid:
        try:
            proc_env = Path(f"/proc/{env_pid}/environ").read_bytes()
            # environ is NUL-separated KEY=value pairs
            pairs = proc_env.split(b"\0")
            lines = []
            for pair in pairs:
                if pair:
                    lines.append(pair.decode("utf-8", errors="replace"))
            sources[f"<pid:{env_pid}>"] = "\n".join(lines)
        except (OSError, ValueError) as e:
            raise RuntimeError(f"cannot read process env: {e}")

    return sources


def _cmd_check(args, config, eval_enabled) -> int:
    sources = _collect_sources(args.paths, getattr(args, "env", None))
    all_findings = []
    for name, content in sources.items():
        parsed = parse_sources(content, source_name=name, eval_enabled=eval_enabled)
        findings = validate(parsed, config=config)
        for f in findings:
            f["source"] = name
        all_findings.extend(findings)

    if args.format == "json":
        print(json.dumps(all_findings, indent=2))
    else:
        for f in all_findings:
            line = f"({f['source']}) {f['rule']}: {f['message']}"
            if not args.quiet:
                print(line)
            else:
                print(f["rule"], file=sys.stderr)

    return 1 if all_findings else 0


def _cmd_render(args, config, eval_enabled) -> int:
    sources = _collect_sources(args.paths)
    merged = {}
    for name, content in sources.items():
        parsed = parse_sources(content, source_name=name, eval_enabled=eval_enabled)
        for k, v in parsed.items():
            merged[k] = v  # later files override earlier

    if args.json:
        print(json.dumps(merged, indent=2))
    elif args.export:
        for k, v in merged.items():
            # shell-quote values with special chars
            if any(c in v for c in " \t\n'\"\\$"):
                print(f"export {k}={_shell_quote(v)}")
            else:
                print(f"export {k}={v}")
    else:
        for k, v in merged.items():
            print(f"{k}={v}")

    return 0


def _cmd_diff(args, config, eval_enabled) -> int:
    sources = _collect_sources(args.paths, getattr(args, "env", None))
    live = None
    file_vars = {}

    for name, content in sources.items():
        if name.startswith("<pid:"):
            parsed = parse_sources(content, source_name=name, eval_enabled=eval_enabled)
            live = parsed
        else:
            parsed = parse_sources(content, source_name=name, eval_enabled=eval_enabled)
            file_vars.update(parsed)

    if live is None:
        print("no live process env specified; comparing between files only", file=sys.stderr)
        live = {}

    # Compare
    only_in_live = set(live) - set(file_vars)
    only_in_files = set(file_vars) - set(live)
    changed = {k for k in set(live) & set(file_vars) if live[k] != file_vars[k]}

    for k in sorted(only_in_files):
        print(f"+ {k}={file_vars[k]}")
    for k in sorted(only_in_live):
        print(f"- {k}={live[k]}")
    for k in sorted(changed):
        print(f"~ {k}: {live[k]} -> {file_vars[k]}")

    return 0


def _cmd_mask(args, config, eval_enabled, patterns) -> int:
    if not patterns:
        patterns = config.get("mask_patterns", [r"(?i)(api[_-]?key|secret|token|password)"])

    sources = _collect_sources(args.paths)
    import re

    results = {}
    for name, content in sources.items():
        lines = content.splitlines(keepends=True)
        new_lines = list(lines)
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            # split KEY=VALUE at first =
            if "=" not in stripped:
                continue
            key, _, val = stripped.partition("=")
            # strip possible 'export ' prefix
            key = key.strip()
            if key.startswith("export "):
                key = key[len("export "):].strip()
            if any(re.search(p, key) for p in patterns):
                new_lines[i] = line.replace(val, "***MASKED***")
        results[name] = "".join(new_lines)

    if args.apply:
        for name, new_content in results.items():
            if new_content == sources[name]:
                continue
            path = Path(name)
            if path.exists():
                backup = path.with_suffix(path.suffix + ".bak")
                backup.write_text(sources[name])
                path.write_text(new_content)
                print(f"masked {name} (backup: {backup})")
            else:
                print(f"skip {name}: not a regular file", file=sys.stderr)
    elif args.dry_run:
        for name, new_content in results.items():
            if new_content != sources[name]:
                print(f"would mask {name} ({sum(1 for a,b in zip(sources[name], new_content) if a!=b)} changes)")
    else:
        for name, new_content in results.items():
            if new_content != sources[name]:
                sys.stdout.write(new_content)
    return 0


def _cmd_report(args, config, eval_enabled) -> int:
    sources = _collect_sources(args.paths)
    all_findings = []
    for name, content in sources.items():
        parsed = parse_sources(content, source_name=name, eval_enabled=eval_enabled)
        findings = validate(parsed, config=config)
        for f in findings:
            f["source"] = name
        all_findings.extend(findings)

    report_data = {
        "generated": "env-guardian",
        "version": __version__,
        "findings_count": len(all_findings),
        "findings": all_findings,
    }

    if args.format == "json":
        output = json.dumps(report_data, indent=2)
    else:
        lines = []
        lines.append(f"env-guardian report: {len(all_findings)} finding