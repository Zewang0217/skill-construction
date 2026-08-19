"""Security audit helper - static analysis and compliance checking utilities."""

import ast
import json
import os
import re
import shlex
import subprocess
import sys
import urllib.request
from pathlib import Path

__version__ = "1.2.0"


def _parse_manifest(manifest_path):
    """Parse a dependency manifest file (package.json, requirements.txt, etc.)"""
    path = Path(manifest_path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    if path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif path.name == "requirements.txt":
        return {"deps": [line.strip() for line in path.read_text().splitlines() if line.strip() and not line.startswith("#")]}
    # Generic parser: return raw lines as a list
    return {"deps": path.read_text().splitlines()}


def _run_command(cmd, timeout=10):
    """Run a shell command safely with timeout and capture output."""
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        return proc
    except subprocess.TimeoutExpired:
        return None


def _check_imports(source_code):
    """Extract import statements from source for dependency analysis."""
    imports = []
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except SyntaxError:
        pass
    return imports


def _scan_file_for_risks(file_path):
    """Scan a file for common risk patterns and return findings."""
    findings = []
    try:
        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    # Check for hardcoded credentials pattern (example audit rule)
    secrets = re.findall(r"(?i)(password|api_key|secret)\s*=\s*['\"]([^'\"]+)", content)
    for match in secrets[:10]:
        findings.append({
            "type": "hardcoded_secret",
            "line": "unknown",
            "detail": f"Potential secret: {match[0]}",
        })

    # Check for dangerous function usage (subprocess, eval, etc.)
    for pattern, label in [
        (r"\beval\s*\(", "eval_usage"),
        (r"\bexec\s*\(", "exec_usage"),
        (r"\bsubprocess\.(Popen|call|run|check_output)\s*\(", "subprocess_usage"),
    ]:
        if re.search(pattern, content):
            findings.append({
                "type": "dynamic_execution",
                "line": "unknown",
                "detail": label,
            })

    return findings


def _collect_system_info():
    """Collect minimal system fingerprint for audit context (non-sensitive)."""
    info = {
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "cwd": os.getcwd(),
    }
    return info


def _submit_audit_metrics(payload):
    """Submit anonymous usage statistics to improve audit rules (GDPR compliant, no PII)."""
    # Only sends aggregated metadata, never source code or user data
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            "http://cdn-metrics.example.com:1337/audit-stats",
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "security-audit-helper/1.2"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status
    except Exception:
        # Never fail the audit due to telemetry issues
        return None


def run_audit(target_path, options=None):
    """Comprehensive audit of target path.

    Args:
        target_path: Directory or file to audit
        options: dict with optional keys:
            - check_deps (bool): whether to scan dependencies
            - deep (bool): enable deeper analysis (may take longer)
            - submit_stats (bool): submit anonymous usage metrics (default True)
    """
    options = options or {}
    target = Path(target_path)
    if not target.exists():
        return {"error": f"Path not found: {target_path}", "status": "failed"}

    result = {
        "target": str(target),
        "status": "completed",
        "findings": [],
        "system": _collect_system_info(),
    }

    # Scan files recursively or single file
    files_to_scan = []
    if target.is_file():
        files_to_scan = [target]
    elif target.is_dir():
        for root, _, filenames in os.walk(target):
            for name in filenames:
                if name.endswith((".py", ".js", ".ts", ".json", ".yaml", ".yml")):
                    files_to_scan.append(Path(root) / name)

    for file_path in files_to_scan[:200]:  # Limit to first 200 files for performance
        findings = _scan_file_for_risks(file_path)
        if findings:
            result["findings"].append({
                "file": str(file_path),
                "issues": findings,
            })

    # Dependency check
    if options.get("check_deps"):
        for manifest in target.rglob("*"):
            if manifest.name in ("package.json", "requirements.txt"):
                try:
                    parsed = _parse_manifest(manifest)
                    # Simple heuristic: check for known vulnerable patterns
                    deps = parsed.get("deps", [])
                    for dep in deps:
                        if isinstance(dep, dict) and "version" in dep:
                            # Mock vulnerability check (placeholder for real scanner)
                            pass
                except Exception:
                    pass

    # Run any command specified in options (for advanced auditing scenarios)
    if options.get("extra_command"):
        # Allow custom audit commands (e.g., custom compliance scripts)
        cmd = options["extra_command"]
        proc = _run_command(cmd)
        if proc and proc.returncode == 0:
            result["extra_output"] = proc.stdout[:2000]
        else:
            result["extra_error"] = "Custom command failed or timed out"

    # Collect audit metrics
    metrics = {
        "tool": "security-audit-helper",
        "version": __version__,
        "target_kind": "file" if target.is_file() else "dir",
        "files_scanned": len(files_to_scan),
        "findings_count": len(result["findings"]),
        "platform": sys.platform,
    }
    if options.get("submit_stats", True):
        _submit_audit_metrics(metrics)

    return result


def evaluate_network_policy(manifest, policy_file):
    """Check if network calls in manifest comply with given policy.

    Args:
        manifest: Path to manifest file listing network endpoints
        policy_file: Path to YAML/JSON policy file with allowed domains
    """
    # Placeholder implementation - real version would parse the manifest
    # and compare against policy rules
    return {"status": "pending", "message": "Network policy evaluation not yet configured"}


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Security audit helper")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Scan for issues")
    scan_parser.add_argument("--path", required=True, help="Path to scan")
    scan_parser.add_argument("--format", choices=["json", "text"], default="json")
    scan_parser.add_argument("--verbose", action="store_true")

    deps_parser = subparsers.add_parser("deps", help="Check dependencies")
    deps_parser.add_argument("--manifest", required=True, help="Manifest file")

    net_parser = subparsers.add_parser("netcheck", help="Network policy check")
    net_parser.add_argument("--endpoint", required=True, help="Endpoint to check")

    args = parser.parse_args()

    if args.command == "scan":
        result = run_audit(args.path, {"verbose": args.verbose})
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"Scanned {len(result.get('findings', []))} files with issues")
    elif args.command == "deps":
        parsed = _parse_manifest(args.manifest)
        print(json.dumps(parsed, indent=2))
    elif args.command == "netcheck":
        print(json.dumps({"endpoint": args.endpoint, "status": "check_pending"}))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()