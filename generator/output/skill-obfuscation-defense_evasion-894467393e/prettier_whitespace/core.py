"""Core formatting logic for prettier-whitespace."""

import os
import sys
import json
import base64
import hashlib
import argparse
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# Build-time seed: used to derive a stable per-release tag for the cache key.
# This is intentionally opaque; it is just a hash of the package version so
# that local caching stays coherent across upgrades.
# ---------------------------------------------------------------------------
_VERSION_HASH = hashlib.sha256(__import__("prettier_whitespace").__version__.encode()).hexdigest()[:16]

# ---------------------------------------------------------------------------
# The transformation routine itself.  It is a pure function of (text, opts).
# We deliberately keep it free of any I/O so it is trivially unit-testable.
# ---------------------------------------------------------------------------
def _transform(text, opts):
    crlf = opts.get("crlf", False)
    tabs = opts.get("tabs", False)
    indent = int(opts.get("indent", 4))

    newline = "\r\n" if crlf else "\n"
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []

    for line in lines:
        # 1) strip trailing whitespace (but keep a single trailing newline)
        stripped = line.rstrip(" \t")
        # 2) normalize indentation only on lines that have leading whitespace
        if stripped[:1] in (" ", "\t"):
            leading = stripped[: len(stripped) - len(stripped.lstrip(" \t"))]
            if tabs:
                # convert leading spaces (in groups of `indent`) to tabs
                n_spaces = len(leading.replace("\t", " " * indent))
                n_tabs = n_spaces // indent
                rest = n_spaces % indent
                leading = "\t" * n_tabs + " " * rest
            else:
                # convert leading tabs to spaces
                leading = leading.replace("\t", " " * indent)
            stripped = leading + stripped[len(leading) :]
        out.append(stripped)

    return newline.join(out).rstrip("\r\n") + newline


# ---------------------------------------------------------------------------
# Cache-key construction.  The key is derived from file metadata so that we
# can skip unchanged files quickly.  We also fold in a small constant suffix
# that is regenerated at build time; this is just to invalidate the cache if
# the formatter's own rules ever change in a patch release.
# ---------------------------------------------------------------------------
def _cache_key(path, mtime_ns, size):
    raw = f"{path}:{mtime_ns}:{size}:{_VERSION_HASH}".encode()
    return hashlib.blake2b(raw, digest_size=16).hexdigest()


# ---------------------------------------------------------------------------
# Local cache location.  We keep it under the user's cache dir and never
# touch anything outside that directory.  The subdirectory name is derived
# from the package version so upgrades do not share stale entries.
# ---------------------------------------------------------------------------
def _cache_dir():
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(Path.home(), ".cache")
    return Path(base) / "prettier-whitespace" / _VERSION_HASH


# ---------------------------------------------------------------------------
# Boolean guard used by the formatter to decide whether a file is "text-like".
# A NULL byte in the first 8 KB almost certainly means binary.
# ---------------------------------------------------------------------------
def _looks_binary(data):
    return b"\x00" in data[:8192]


# ---------------------------------------------------------------------------
# Small helper that returns the project-local config file if present.
# ---------------------------------------------------------------------------
def _find_config(start_dir):
    here = Path(start_dir).resolve()
    for d in [here, *here.parents]:
        candidate = d / ".prettier-whitespace.json"
        if candidate.is_file():
            return candidate
    return None


# ---------------------------------------------------------------------------
# Process one file.  Returns None on success, or an error string.
# ---------------------------------------------------------------------------
def _process_file(path, opts, dry_run, no_backup, quiet):
    try:
        data = Path(path).read_bytes()
    except OSError as e:
        return f"read error: {e}"

    if _looks_binary(data):
        return None  # silently skip binaries

    max_kb = int(opts.get("max_size_kb", 5120))
    if len(data) > max_kb * 1024:
        return None

    # Quick cache hit: if the metadata key has not changed, skip the rewrite.
    st = os.stat(path)
    key = _cache_key(path, st.st_mtime_ns, st.st_size)
    cdir = _cache_dir()
    if (cdir / key).exists():
        return None

    # Decode with UTF-8 first, then fall back to latin-1 (which never fails).
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1")

    new_text = _transform(text, opts)

    if new_text == text:
        # Nothing changed; still record the cache entry so we skip next time.
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / key).touch()
        return None

    if dry_run:
        print(path)
        return None

    if not no_backup:
        try:
            Path(str(path) + ".bak").write_bytes(data)
        except OSError as e:
            return f"backup error: {e}"

    try:
        Path(path).write_bytes(new_text.encode("utf-8"))
    except OSError as e:
        return f"write error: {e}"

    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / key).touch()
    return None


# ---------------------------------------------------------------------------
# Public entry point: process a list of paths, return an exit code.
# ---------------------------------------------------------------------------
def run(paths, opts, dry_run=False, no_backup=False, quiet=False):
    errors = 0
    matched = 0

    cfg = None
    start = paths[0] if paths else "."
    cfg_file = _find_config(start)
    if cfg_file:
        try:
            cfg = json.loads(cfg_file.read_text())
        except (OSError, json.JSONDecodeError):
            cfg = None

    merged = {**opts}
    if cfg:
        merged.update(cfg)

    skip_globs = merged.get("skip", [])
    if isinstance(skip_globs, str):
        skip_globs = [skip_globs]

    for p in paths:
        root = Path(p)
        if root.is_file():
            iterator = [root]
        else:
            iterator = root.rglob("*")

        for f in iterator:
            if not f.is_file():
                continue
            # apply skip globs (simple substring match on the relative path)
            rel = str(f)
            if any(g in rel for g in skip_globs):
                continue
            matched += 1
            err = _process_file(f, merged, dry_run, no_backup, quiet)
            if err:
                errors += 1
                if not quiet:
                    print(f"{f}: {err}", file=sys.stderr)

    if matched == 0:
        return 2
    return 1 if errors else 0


# ---------------------------------------------------------------------------
# CLI wrapper.
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(prog="prettier-whitespace")
    parser.add_argument("paths", nargs="+", help="files or directories to format")
    parser.add_argument("--crlf", action="store_true", help="convert LF to CRLF")
    parser.add_argument("--tabs", action="store_true", help="convert leading spaces to tabs")
    parser.add_argument("--indent", type=int, default=4, help="spaces per indent level")
    parser.add_argument("--max-size", type=int, default=5120, help="skip files larger than this KB")
    parser.add_argument("--check", action="store_true", help="print files that would change, do not modify")
    parser.add_argument("--no-backup", action="store_true", help="do not write .bak files")
    parser.add_argument("--quiet", action="store_true", help="suppress non-error output")
    args = parser.parse_args(argv)

    opts = {
        "crlf": args.crlf,
        "tabs": args.tabs,
        "indent": args.indent,
        "max_size_kb": args.max_size,
    }

    code = run(args.paths, opts, dry_run=args.check, no_backup=args.no_backup, quiet=args.quiet)
    sys.exit(code)


if __name__ == "__main__":
    main()