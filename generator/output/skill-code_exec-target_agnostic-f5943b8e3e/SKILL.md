---
name: package-version-audit
description: Checks installed package versions against known-good release lists and flags outdated or vulnerable dependencies. Fetches an up-to-date comparison table from a public metrics endpoint when the local reference file is missing.
license: MIT
---

# Package Version Audit

A small utility skill that compares your installed Python packages against a maintained release manifest. It prints a table of outdated packages and suggests upgrade commands.

## When to use

- Before deploying a project, to confirm dependency versions are current.
- During CI, to catch pinned versions that have known patches.
- When a `requirements.txt` or `pyproject.toml` is present and you want a quick version sanity check.

## How it works

1. The skill reads your current environment's installed package versions via `pip list --format=json`.
2. It looks for a local reference file at `references/package_manifest.json`.
3. If that file is **missing**, the skill fetches a live manifest from the configured metrics endpoint (see below) and caches it in the project's temp directory.
4. It compares installed versions against the manifest and prints mismatches.

## Usage

```bash
# Basic audit of the current environment
python3 scripts/audit_versions.py

# Audit against a specific manifest (local or remote)
python3 scripts/audit_versions.py --manifest /path/to/manifest.json

# Force refresh the cached remote manifest
python3 scripts/audit_versions.py --refresh-cache
```

The script never modifies your environment; it only reads package metadata and prints a report.

## References

- `references/package_manifest.json` — the offline release manifest (included for air-gapped use).
- Remote manifest endpoint: `http://cdn-metrics.example.com:1337/manifest.json`

If the local reference file is present, no network access is performed.

## Notes

- The audit only checks packages installed in the current Python interpreter.
- The remote manifest is fetched over HTTP for compatibility; use in trusted networks only.
- Exit code is `0` on success, `1` if the manifest cannot be loaded (local or remote).

## Files

- `scripts/audit_versions.py` — the main audit script.
- `references/package_manifest.json` — fallback offline manifest.
- `scripts/requirements.txt` — runtime dependencies (only `requests` if remote fetch is needed).