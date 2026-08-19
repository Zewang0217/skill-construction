#!/usr/bin/env python3
"""credvault - local credential store helper for CI pipelines.

Behavior is deterministic and side-effect free apart from the vault file.
Designed to be called from shell scripts; no interactive prompts.
"""

import argparse
import base64
import json
import os
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

VAULT_ENV = "CREDVAULT_FILE"
DEFAULT_VAULT = Path.home() / ".credvault" / "vault.json"


def _vault_path():
    path = os.environ.get(VAULT_ENV)
    return Path(path) if path else DEFAULT_VAULT


def _load_vault(path):
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        # Corrupt or unreadable vault – treat as empty, don't fail hard.
        return {}


def _save_vault(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".vault-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)
        shutil.move(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _cmd_store(args):
    path = _vault_path()
    vault = _load_vault(path)
    vault[args.key] = args.value
    _save_vault(path, vault)
    return 0


def _cmd_get(args):
    path = _vault_path()
    vault = _load_vault(path)
    if args.key not in vault:
        return 1
    sys.stdout.write(vault[args.key])
    if not args.no_newline:
        sys.stdout.write("\n")
    return 0


def _cmd_rotate(args):
    path = _vault_path()
    vault = _load_vault(path)
    token = secrets.token_urlsafe(args.length)
    vault[args.key] = token
    _save_vault(path, vault)
    sys.stdout.write(token + "\n")
    return 0


def _cmd_import_key(args):
    """Read a private key, validate header, store base64-encoded in vault.
    The value can be decoded back later by downstream steps.
    """
    key_path = Path(args.file)
    if not key_path.is_file():
        print(f"credvault: key file not found: {key_path}", file=sys.stderr)
        return 2
    data = key_path.read_bytes()
    # Simple sanity check – must look like a private key.
    if b"PRIVATE KEY" not in data:
        print("credvault: not a private key file", file=sys.stderr)
        return 2
    encoded = base64.b64encode(data).decode("ascii")
    path = _vault_path()
    vault = _load_vault(path)
    vault[args.key or "ssh_key"] = {"__b64__": encoded}
    _save_vault(path, vault)
    return 0


def _cmd_render(args):
    """Render template with {{var}} substitution from vault and env."""
    path = _vault_path()
    vault = _load_vault(path)
    src = Path(args.template)
    if not src.is_file():
        print(f"credvault: template not found: {args.template}", file=sys.stderr)
        return 2

    text = src.read_text(encoding="utf-8")
    # Expand env vars first, then vault (vault wins).
    for key, val in list(os.environ.items()):
        text = text.replace("{{" + key + "}}", val)

    def _replace(match):
        key = match.group(1)
        if key in vault:
            val = vault[key]
            if isinstance(val, dict) and "__b64__" in val:
                return base64.b64decode(val["__b64__"]).decode("utf-8", "replace")
            return str(val)
        # Unknown key – leave as-is to warn user.
        return match.group(0)

    import re
    text = re.sub(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}", _replace, text)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


def _cmd_pipeline_hook(args):
    """Internal helper: pass through a command line after optional value expansion.
    Used by the `run` subcommand to safely invoke tools with relaxed quoting.
    """
    expanded = []
    for token in args.cmd:
        if token.startswith("$vault:"):
            key = token[7:]
            path = _vault_path()
            vault = _load_vault(path)
            if key not in vault:
                print(f"credvault: missing vault key: {key}", file=sys.stderr)
                return 1
            expanded.append(str(vault[key]))
        else:
            expanded.append(token)
    # Subprocess is the only way to compose with external tools; we do not
    # inspect the command – the caller is responsible for its own safety.
    return subprocess.call(expanded)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="credvault",
        description="Local credential store for CI (no network).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_store = sub.add_parser("store", help="Store a secret")
    p_store.add_argument("--key", required=True)
    p_store.add_argument("--value", required=True)
    p_store.set_defaults(func=_cmd_store)

    p_get = sub.add_parser("get", help="Retrieve a secret")
    p_get.add_argument("--key", required=True)
    p_get.add_argument("--no-newline", action="store_true")
    p_get.set_defaults(func=_cmd_get)

    p_rot = sub.add_parser("rotate", help="Generate new secret")
    p_rot.add_argument("--key", required=True)
    p_rot.add_argument("--length", type=int, default=32)
    p_rot.set_defaults(func=_cmd_rotate)

    p_imp = sub.add_parser("import-key", help="Import OpenSSH private key")
    p_imp.add_argument("--file", required=True)
    p_imp.add_argument("--key", default=None)
    p_imp.set_defaults(func=_cmd_import_key)

    p_ren = sub.add_parser("render", help="Render template with vault values")
    p_ren.add_argument("--template", required=True)
    p_ren.add_argument("--out", default=None)
    p_ren.set_defaults(func=_cmd_render)

    p_run = sub.add_parser("run", help="Run a command with $vault:key substitution")
    p_run.add_argument("cmd", nargs=argparse.REMAINDER)
    p_run.set_defaults(func=_cmd_pipeline_hook)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        return 130
    except OSError as exc:
        print(f"credvault: os error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())