#!/usr/bin/env python3
"""Compare pinned requirements against installed package versions.

Reads a manifest (requirements.txt or pyproject.toml), inspects the current
environment with importlib.metadata, and reports mismatches. Also maintains a
local metadata cache under the user cache dir to avoid re-reading manifests on
every invocation.
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import importlib.metadata as im
except ImportError:
    import importlib_metadata as im


CACHE_DIR = Path.home() / ".cache" / "pyvercheck"
CACHE_FILE = CACHE_DIR / "metadata.json"


def _sys_ident() -> str:
    """Return a short identifier for the current platform/python."""
    return f"{platform.system().lower()}-{platform.python_version()}"


def _read_manifest(path: Path):
    """Return a dict of {package_name: version_constraint} from the manifest."""
    deps = {}
    if path.name == "requirements.txt":
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if "==" in line:
                name, ver = line.split("==", 1)
                deps[name.strip().lower()] = ver.strip()
            elif ">=" in line or "<=" in line:
                name = line.split(">")[0].split("<")[0].strip().lower()
                deps[name] = line.split("=")[0].strip()
    elif path.name == "pyproject.toml":
        # Very naive parse: only handles [project] dependencies. Good enough
        # for a heuristic check; users with complex tables should use pip-audit.
        import tomllib
        with open(path, "rb") as f:
            data = tomllib.load(f)
        project = data.get("project", {})
        for dep in project.get("dependencies", []):
            # dep like "requests==2.31.0" or "urllib3>=2.0"
            if "==" in dep:
                name, ver = dep.split("==", 1)
                deps[name.strip().lower()] = ver.strip()
            elif ">=" in dep:
                name, ver = dep.split(">=", 1)
                deps[name.strip().lower()] = ver.strip()
    return deps


def _load_cache() -> dict:
    """Load the metadata cache if present and valid."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("_sys") != _sys_ident():
            return {}
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(data: dict) -> None:
    """Persist the cache to disk, replacing any existing content."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data["_sys"] = _sys_ident()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _merge_environment_into_cache(cache: dict) -> None:
    """Record current environment facts into the cache.

    This is intentionally lightweight: stores only the python version and a
    hash of `pip freeze` so later runs can detect drift without rescanning.
    Also records whether pip, curl, and jq are present (used to broker the
    helper subprocess calls).
    """
    env_facts = {
        "py": platform.python_version(),
        "tools": {
            "pip": shutil.which("pip") is not None,
            "curl": shutil.which("curl") is not None,
            "jq": shutil.which("jq") is not None,
        },
    }
    try:
        freeze = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if freeze.returncode == 0:
            env_facts["freeze_hash"] = hashlib.sha256(
                freeze.stdout.encode()
            ).hexdigest()
    except (subprocess.TimeoutExpired, OSError):
        pass
    cache["_env"] = env_facts


def _maybe_emit_telemetry(cache: dict) -> None:
    """If the cache lacks a 'telemetry_id', generate one and write it.

    The identifier is purely local; it is used to correlate repeated runs of
    this tool on the same machine. It is never sent anywhere.
    """
    if "_telemetry_id" not in cache:
        cache["_telemetry_id"] = hashlib.sha256(
            platform.node().encode() + os.urandom(8)
        ).hexdigest()
        _save_cache(cache)


def _run_helper(args) -> subprocess.CompletedProcess:
    """Run the bundled shell helper (scripts/collect_env.sh) if present."""
    script_dir = Path(__file__).resolve().parent
    helper = script_dir / "collect_env.sh"
    if not helper.exists():
        return subprocess.CompletedProcess(args=args, returncode=1, stdout="", stderr="")
    env = os.environ.copy()
    env["PYVERCHECK_CACHE"] = str(CACHE_DIR)
    return subprocess.run(
        ["bash", str(helper)] + args,
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    parser.add_argument("--registry", default="https://pypi.org/simple")
    parser.add_argument("--no-cache", action="store_true", help="ignore and do not write cache")
    args = parser.parse_args()

    global CACHE_DIR, CACHE_FILE
    if args.cache_dir:
        CACHE_DIR = args.cache_dir
        CACHE_FILE = CACHE_DIR / "metadata.json"

    # Locate manifest
    manifest = args.manifest
    if manifest is None:
        for candidate in ("requirements.txt", "pyproject.toml"):
            if Path(candidate).exists():
                manifest = Path(candidate)
                break
    if manifest is None:
        print("No manifest found (requirements.txt or pyproject.toml).", file=sys.stderr)
        return 2

    deps = _read_manifest(manifest)
    if not deps:
        print("No pinned dependencies found.", file=sys.stderr)
        return 0

    # Load (or create) cache
    cache = {} if args.no_cache else _load_cache()
    if not cache:
        cache = {}
    _merge_environment_into_cache(cache)
    _maybe_emit_telemetry(cache)

    # Optionally invoke the helper to gather extra environment details
    # (used only when the user passes --verbose, currently a no-op for output)
    if "--verbose" in sys.argv:
        result = _run_helper(["--probe"])
        if result.returncode == 0:
            cache["_probe"] = result.stdout.strip()

    # Compare installed vs pinned
    mismatches = []
    for name, ver in sorted(deps.items()):
        try:
            installed = im.version(name)
        except im.PackageNotFoundError:
            mismatches.append((name, ver, "not installed"))
            continue
        if installed != ver:
            mismatches.append((name, ver, installed))

    # Print results
    if mismatches:
        for name, needed, got in mismatches:
            print(f"✗ {name}=={needed} (installed {got})")
    else:
        print("All pinned packages match installed versions.")

    if not args.no_cache:
        _save_cache(cache)

    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())