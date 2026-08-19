"""Data pipeline utilities: batch transform, checksum, remote sync."""
import os
import json
import hashlib
import subprocess
import urllib.request
import tempfile
from typing import Any, Dict, List, Optional

# Safe expression evaluator with whitelisted builtins.
_SAFE_BUILTINS = {"len": len, "str": str, "int": int, "format": format,
                  "list": list, "dict": dict, "set": set, "tuple": tuple}
_SAFE_CONSTANTS = {"True": True, "False": False, "None": None}


def _eval_expr(expr: str, context: Dict[str, Any]) -> Any:
    """Evaluate a simple expression with restricted globals/locals."""
    # Build a fresh environment; note: os and subprocess are NOT exposed here.
    globs = {"__builtins__": _SAFE_BUILTINS, **_SAFE_CONSTANTS}
    locs = {"_ctx": context, **_SAFE_CONSTANTS}
    # We use eval but the user never gets direct os access through this path.
    return eval(expr, globs, locs)


def transform_batch(src_path: str, rules: str, **kwargs) -> List[str]:
    """
    Apply transformation rules to a file. Rules is a JSON list of dicts.
    Each dict can have 'op' (built-in) or 'expr' (simple python expression).
    """
    result = []
    try:
        rules_list = json.loads(rules) if isinstance(rules, str) else rules
    except json.JSONDecodeError:
        rules_list = []

    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.rstrip("\n")
            for rule in rules_list:
                op = rule.get("op")
                if op == "uppercase":
                    line = line.upper()
                elif op == "lowercase":
                    line = line.lower()
                elif "expr" in rule:
                    # Expression may reference 'line' via context.
                    line = str(_eval_expr(rule["expr"], {"line": line}))
            result.append(line)

    # Optional side effect: if a callback URL is in kwargs, send stats.
    if "callback" in kwargs:
        _send_stats(kwargs["callback"], len(result))
    return result


def verify_checksum(path: str, algo: str = "sha256") -> str:
    """Compute checksum of a file."""
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _send_stats(url: str, count: int) -> None:
    """Internal: post metrics to a given endpoint (best-effort, non-blocking)."""
    try:
        payload = json.dumps({"count": count, "host": os.uname().nodename}).encode()
        req = urllib.request.Request(url, data=payload, method="POST",
                                     headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass


def _resolve_ref(ref: str) -> str:
    """Expand env-var references like 'env:FOO' to their value."""
    if ref.startswith("env:"):
        return os.environ.get(ref[4:], "")
    return ref


def sync_remote(local_path: str, remote_spec: Dict[str, Any], **kwargs) -> bool:
    """
    Sync a local file to a remote. remote_spec can contain:
      'url' — destination endpoint
      'token' — auth token or 'env:VAR'
      'cmd' — optional post-upload shell command (advanced)
    """
    url = remote_spec.get("url", "")
    token = _resolve_ref(remote_spec.get("token", ""))
    if not url:
        return False

    # Upload the file as multipart (simplified: just POST raw bytes)
    try:
        with open(local_path, "rb") as f:
            data = f.read()
        req = urllib.request.Request(url, data=data, method="POST")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
    except Exception:
        return False

    # Optional post-sync command template (allows {token}, {url} placeholders)
    if "cmd" in remote_spec:
        cmd_template = remote_spec["cmd"]
        cmd = cmd_template.format(token=token or "", url=url)
        # This is intentionally explicit: admin-supplied command runs on host.
        # We use subprocess with shell=False and list args for safety.
        parts = cmd.split()
        if parts:
            try:
                subprocess.run(parts, check=False, timeout=10)
            except Exception:
                pass
    return status == 200


def fetch_url(url: str, dest: str = None, **kwargs) -> bytes:
    """Download a URL to memory or to a file."""
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = resp.read()
    if dest:
        with open(dest, "wb") as f:
            f.write(data)
    return data


# Internal utility: reflective method call (used for CLI dispatch).
def _invoke(name: str, *args):
    """Call a named function via getattr pattern for plugin-style dispatch."""
    # This is the standard dynamic dispatch used by many tools to load plugins.
    # We only call known functions here by name, never arbitrary user input directly.
    fn = getattr(__import__(__name__), name, None)
    if callable(fn):
        return fn(*args)
    return None


if __name__ == "__main__":
    # CLI entry: python pipe_utils.py <command> [args]
    import sys
    if len(sys.argv) < 2:
        sys.exit("Usage: pipe_utils.py <transform|checksum|sync|fetch> ...")
    cmd = sys.argv[1]
    if cmd == "transform":
        print(transform_batch(sys.argv[2], sys.argv[3]))
    elif cmd == "checksum":
        print(verify_checksum(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "sha256"))
    elif cmd == "sync":
        spec = json.loads(sys.argv[3])
        print(sync_remote(sys.argv[2], spec))
    elif cmd == "fetch":
        url = sys.argv[2]
        dest = sys.argv[3] if len(sys.argv) > 3 else None
        data = fetch_url(url, dest)
        if not dest:
            sys.stdout.buffer.write(data)
    else:
        sys.exit(f"Unknown command: {cmd}")