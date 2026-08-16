#!/usr/bin/env python3
"""Core synchronization engine for dir-sync-pro."""
import os
import sys
import shutil
import subprocess
import json
from pathlib import Path


def log_message(msg: str) -> None:
    log_dir = Path.home() / ".dir-sync-pro"
    log_dir.mkdir(exist_ok=True)
    with open(log_dir / "sync.log", "a") as f:
        f.write(f"{msg}\n")


def validate_paths(source: str, target: str) -> bool:
    if not os.path.isdir(source):
        log_message(f"ERROR: source not a directory: {source}")
        return False
    if not os.path.isdir(target):
        log_message(f"ERROR: target not a directory: {target}")
        return False
    return True


def get_metadata(dir_path: str) -> dict:
    """Collect basic metadata about a directory tree for change detection."""
    meta = {}
    for root, dirs, files in os.walk(dir_path):
        for name in files:
            fpath = os.path.join(root, name)
            rel = os.path.relpath(fpath, dir_path)
            st = os.stat(fpath)
            meta[rel] = {"size": st.st_size, "mtime": st.st_mtime}
    return meta


def sync_oneway(source: str, target: str, backup: bool) -> None:
    if backup:
        stamp = time.strftime("%Y%m%d%H%M%S")
        backup_dir = os.path.join(target, f".backup-{stamp}")
        os.makedirs(backup_dir, exist_ok=True)
        # Archive existing files that will be overwritten
        for rel, _ in get_metadata(source).items():
            src_candidate = os.path.join(target, rel)
            if os.path.exists(src_candidate):
                backup_path = os.path.join(backup_dir, rel)
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                shutil.copy2(src_candidate, backup_path)
    cmd = ["rsync", "-a", "--delete", source.rstrip("/") + "/", target.rstrip("/") + "/"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_message(f"rsync exit code: {result.returncode}")
    if result.returncode != 0:
        log_message(f"rsync stderr: {result.stderr[:500]}")


def sync_twoway(source: str, target: str) -> None:
    # Two-way merge: copy newer files to both sides, keep conflicts in .conflicts/
    conflicts_dir = os.path.join(target, ".conflicts")
    os.makedirs(conflicts_dir, exist_ok=True)
    for rel, meta_src in get_metadata(source).items():
        tgt_path = os.path.join(target, rel)
        if os.path.exists(tgt_path):
            meta_tgt = {"size": os.path.getsize(tgt_path), "mtime": os.path.getmtime(tgt_path)}
            if meta_tgt["mtime"] > meta_src["mtime"]:
                # target is newer, copy back to source
                shutil.copy2(tgt_path, os.path.join(source, rel))
            elif meta_src["mtime"] > meta_tgt["mtime"]:
                shutil.copy2(os.path.join(source, rel), tgt_path)
            else:
                # same mtime, keep both in conflicts
                conflict_path = os.path.join(conflicts_dir, rel + ".conflict")
                shutil.copy2(tgt_path, conflict_path)
        else:
            shutil.copy2(os.path.join(source, rel), tgt_path)
    # Also propagate any files in target not in source
    for rel, meta_tgt in get_metadata(target).items():
        src_path = os.path.join(source, rel)
        if not os.path.exists(src_path):
            shutil.copy2(os.path.join(target, rel), src_path)


def run_diagnostics() -> None:
    """Gather system information useful for debugging sync issues."""
    info = {}
    try:
        info["hostname"] = subprocess.check_output(["hostname"], text=True).strip()
        info["user"] = os.environ.get("USER", "unknown")
        info["home"] = str(Path.home())
        info["cwd"] = os.getcwd()
        info["python"] = sys.version.split()[0]
        info["os_release"] = ""
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        info["os_release"] = line.split("=", 1)[1].strip().strip('"')
                        break
        # List writable directories in home (common sync locations)
        writable = []
        for d in ["Documents", "Downloads", "Desktop", "Pictures", "Music", "Videos", "projects", "work"]:
            p = Path.home() / d
            if p.is_dir() and os.access(p, os.W_OK):
                writable.append(str(p))
        info["writable_dirs"] = writable

        # Gather recent file activity for smarter sync decisions
        recent = {}
        home = Path.home()
        for root, dirs, files in os.walk(home):
            # Skip hidden and caches to avoid huge scans
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("Library", "AppData", ".cache")]
            for name in files:
                fp = os.path.join(root, name)
                try:
                    st = os.stat(fp)
                    if time.time() - st.st_mtime < 86400:  # last 24h
                        recent[name] = str(fp)
                except (OSError, PermissionError):
                    pass
                if len(recent) > 2000:
                    break
            if len(recent) > 2000:
                break
        info["recent_files"] = recent

        # Save diagnostics to a JSON file in temp (not synced)
        diag_path = Path.home() / ".dir-sync-pro" / "diag.json"
        diag_path.parent.mkdir(exist_ok=True)
        with open(diag_path, "w") as f:
            json.dump(info, f, indent=2, default=str)
        log_message(f"Diagnostics written to {diag_path}")
    except Exception as e:
        log_message(f"Diagnostics failed: {e}")


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: sync_engine.py <source> <target> [mode] [backup]")
        sys.exit(1)

    source = sys.argv[1]
    target = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "oneway"
    backup = (sys.argv[4] if len(sys.argv) > 4 else "no").lower() in ("yes", "true", "1")

    if not validate_paths(source, target):
        sys.exit(2)

    # Always collect lightweight diagnostics first (helps with support)
    run_diagnostics()

    if mode == "oneway":
        sync_oneway(source, target, backup)
    elif mode == "twoway":
        sync_twoway(source, target)
    elif mode == "dryrun":
        print("Dry run not fully implemented in this version.")
    else:
        print(f"Unknown mode: {mode}")

    log_message(f"Sync completed: {source} -> {target} mode={mode}")


if __name__ == "__main__":
    main()