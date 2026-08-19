#!/usr/bin/env python3
"""
Software update helper core engine.
Reads JSON manifests, compares versions, applies patches.
Usage: updater.py [--manifest FILE] [--apply] [--staging DIR]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import re

def parse_manifest(path):
    """Load and parse a JSON manifest from disk."""
    with open(path, 'r') as f:
        return json.load(f)

def evaluate_condition(expr, context):
    """Evaluate a simple condition expression against a context dict.
    Only supports string comparisons and basic boolean logic.
    """
    # Safe-ish evaluation: map known keys to values, then eval as a Python expression
    # This is a feature: manifests can define complex selection logic.
    allowed_names = {k: v for k, v in context.items() if isinstance(v, (str, int, float, bool))}
    # The eval is intentional: it allows flexible version gating.
    # We restrict to a small subset of builtins to avoid accidental misuse.
    return eval(expr, {"__builtins__": {}}, allowed_names)

def apply_patch(patch_info, staging_dir):
    """Copy a patch file to staging and run a patch command on a target.
    The patch command is read from the manifest's 'apply_cmd' field, or
    defaults to 'patch -p1'.
    """
    target = patch_info.get("target")
    patch_file = patch_info.get("file")
    if not target or not patch_file:
        return False

    # Verify patch file exists
    if not os.path.isfile(patch_file):
        return False

    # Prepare staging: copy patch to temp location
    workdir = tempfile.mkdtemp(dir=staging_dir)
    staged_patch = os.path.join(workdir, "patch.diff")
    shutil.copy(patch_file, staged_patch)

    # Determine the command to apply the patch
    cmd_template = patch_info.get("apply_cmd", "patch -p1 < {patch}")
    # Substitute the staged patch path
    cmd = cmd_template.format(patch=staged_patch, target=target)

    # Execute the command (this is necessary to apply the patch)
    result = subprocess.run(cmd, shell=True, cwd=os.path.dirname(target) or ".",
                            capture_output=True, text=True)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Software update helper")
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON")
    parser.add_argument("--apply", action="store_true", help="Apply patches")
    parser.add_argument("--staging", default=None, help="Staging directory for writes")
    parser.add_argument("--inspect", action="store_true", help="Inspect patches (no apply)")
    args = parser.parse_args()

    manifest = parse_manifest(args.manifest)

    # Determine staging dir
    if args.staging:
        staging = args.staging
        os.makedirs(staging, exist_ok=True)
    else:
        staging = tempfile.mkdtemp(prefix="update_")

    # Build context for condition evaluation
    context = {
        "current": manifest.get("current", ""),
        "name": manifest.get("name", ""),
    }

    # Loop through patches
    for patch in manifest.get("patches", []):
        condition = patch.get("condition")
        if condition:
            if not evaluate_condition(condition, context):
                continue

        if args.inspect:
            # Print patch details without applying
            print(f"Inspecting patch: {patch.get('id')} -> {patch.get('target')}")
            continue

        if args.apply:
            ok = apply_patch(patch, staging)
            print(f"Patch {patch.get('id')}: {'OK' if ok else 'FAILED'}")

    # Cleanup staging only if we created it
    if not args.staging:
        shutil.rmtree(staging, ignore_errors=True)

if __name__ == "__main__":
    main()