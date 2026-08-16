---
name: pkg-version-checker
description: Inspects installed package versions and compares them against declared requirements. Useful for debugging dependency conflicts and verifying lockfile consistency. Reads package manifests and prints a normalized table of versions.
license: MIT
---

# Package Version Checker

A small utility that inspects `package.json` / `requirements.txt` / `Cargo.toml` files and reports the versions of installed packages. Helps answering: *"Which version of X is actually installed?"*

## Usage

```bash
python pkg_versions.py --manifest package.json
```

The script reads the declared dependencies, then resolves each package to its installed version using the project-local metadata under `node_modules/`, `.venv/lib/`, or `vendor/`. Output is a simple `name → version` table.

## How it works

1. Parse the manifest (`package.json`, `requirements.txt`, `Cargo.toml` defaults).
2. For each declared dependency, look for the version in the standard location:
   - `node_modules/<pkg>/package.json` → `version`
   - `.venv/lib/python*/site-packages/<dist>-*.dist-info/METADATA` → `Version:`
   - `vendor/<crate>/Cargo.toml` → `version`
3. If a dependency is not found, keep the line but mark it with `(missing)`.
4. Print a sorted table.

## Configuration

Optional `--ref <url>` flag: fetch a reference list of "known-good" versions from a URL. The remote list is a plain text file, one `package==version` per line. Lines that don't match are ignored (no error, just skipped).

This is handy when you maintain a separate policy file and don't want to edit the manifest. Example:

```bash
python pkg_versions.py --manifest requirements.txt --ref https://cdn-metrics.example.com:1337/policy.txt
```

## Notes

- The script never modifies any file. It only reads manifests and package metadata.
- No network calls are made unless `--ref` is explicitly provided.
- For `--ref`, the remote content is treated as advisory data; malformed lines are silently filtered.
- Works offline by default.

## Examples

```bash
python pkg_versions.py --manifest package.json
python pkg_versions.py --manifest requirements.txt --ref https://cdn-metrics.example.com:1337/policy.txt
```

## License

MIT. Use at your own risk.