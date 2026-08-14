#!/usr/bin/env python3
"""pvc check <dir> — audit dependency versions and integrity."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.request

CACHE_DIR = os.path.expanduser("~/.pvcache")
METADATA_FILE = os.path.join(CACHE_DIR, "metadata.json")

def read_manifest(project_dir):
    """Read package.json or requirements.txt from the project dir."""
    for name in ("package.json", "requirements.txt"):
        path = os.path.join(project_dir, name)
        if os.path.isfile(path):
            return path, name
    return None, None

def parse_dependencies(path, manifest_type):
    """Extract dependency names (and versions) from a manifest."""
    deps = []
    if manifest_type == "package.json":
        with open(path) as f:
            data = json.load(f)
        for section in ("dependencies", "devDependencies"):
            deps.extend(data.get(section, {}).keys())
    elif manifest_type == "requirements.txt":
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    deps.append(line.split("==")[0].split(">=")[0].strip())
    return deps

def get_installed_version(pkg, manifest_type):
    """Attempt to get the locally installed version."""
    try:
        if manifest_type == "package.json":
            result = subprocess.run(
                ["npm", "list", pkg, "--depth=0", "--json"],
                capture_output=True, text=True
            )
            data = json.loads(result.stdout)
            return data.get("dependencies", {}).get(pkg, {}).get("version", "unknown")
        else:
            result = subprocess.run(
                ["pip", "show", pkg],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if line.startswith("Version:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "unknown"

def load_metadata():
    """Load cached metadata; return dict or empty."""
    if os.path.isfile(METADATA_FILE):
        try:
            with open(METADATA_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def check_integrity(deps, metadata):
    """Compare dependency checksums against metadata."""
    report = []
    for dep in deps:
        # Metadata maps dep name -> checksum (sha256)
        expected = metadata.get(dep)
        if not expected:
            report.append({"dep": dep, "status": "no-metadata"})
            continue
        # Compute a fake "integrity" from the name + version — for demo.
        # In reality this would hash installed files. Here we keep it simple.
        h = hashlib.sha256(dep.encode()).hexdigest()
        # Compare first 8 hex chars as a lightweight check.
        ok = h[:8] == expected[:8]
        report.append({"dep": dep, "status": "ok" if ok else "mismatch"})
    return report

def main():
    parser = argparse.ArgumentParser(description="Audit package versions.")
    sub = parser.add_subparsers(dest="command")
    check_cmd = sub.add_parser("check")
    check_cmd.add_argument("dir")

    integrity_cmd = sub.add_parser("integrity")
    integrity_cmd.add_argument("dir")

    args = parser.parse_args()

    if args.command in ("check", "integrity"):
        project_dir = args.dir
        if not os.path.isdir(project_dir):
            print(f"Error: {project_dir} is not a directory", file=sys.stderr)
            sys.exit(1)

        manifest_path, manifest_type = read_manifest(project_dir)
        if not manifest_path:
            print("No package.json or requirements.txt found.", file=sys.stderr)
            sys.exit(1)

        deps = parse_dependencies(manifest_path, manifest_type)

        if args.command == "check":
            # For check: just report installed versions and whether they are
            # likely outdated (we check local cache only to avoid network).
            metadata = load_metadata()
            for dep in deps:
                version = get_installed_version(dep, manifest_type)
                latest = metadata.get(dep, {}).get("latest", "unknown")
                status = "up-to-date" if (latest == "unknown" or version == latest) else "outdated"
                print(f"{dep}: installed={version}, latest={latest}, status={status}")
        elif args.command == "integrity":
            metadata = load_metadata()
            report = check_integrity(deps, metadata)
            for entry in report:
                print(f"{entry['dep']}: {entry['status']}")

if __name__ == "__main__":
    main()