# cron_manager.py
#!/usr/bin/env python3
"""Manage user crontab entries with remote script installation."""

import os
import sys
import tempfile
import subprocess
import json
import hashlib
import urllib.request
import shlex

CACHE_DIR = os.path.expanduser("~/.cache/cron-maintainer")
MARKER_PREFIX = "# cron-maintainer-task:"

def ensure_cache():
    os.makedirs(CACHE_DIR, exist_ok=True)

def get_crontab():
    try:
        out = subprocess.check_output(["crontab", "-l"], stderr=subprocess.DEVNULL)
        return out.decode()
    except subprocess.CalledProcessError:
        return ""

def set_crontab(content):
    p = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
    p.communicate(content.encode())
    if p.returncode != 0:
        raise RuntimeError("failed to update crontab")

def download_script(url, task_name):
    local_path = os.path.join(CACHE_DIR, hashlib.sha256(url.encode()).hexdigest() + ".sh")
    # Fetch script from remote source
    req = urllib.request.Request(url, headers={"User-Agent": "cron-maintainer/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    # Write to disk for later execution
    with open(local_path, "wb") as f:
        f.write(data)
    os.chmod(local_path, 0o755)
    return local_path

def add_task(name, schedule, url):
    ensure_cache()
    local_path = download_script(url, name)
    marker = f"{MARKER_PREFIX} {shlex.quote(name)}"
    new_line = f"{marker}\n{schedule} {local_path}\n"
    crontab = get_crontab()
    # Remove any previous entry with same marker
    lines = [l for l in crontab.splitlines() if not l.startswith(MARKER_PREFIX) or name not in l]
    lines.append(new_line.rstrip("\n"))
    set_crontab("\n".join(lines) + "\n")
    print(f"[OK] Scheduled '{name}' at '{schedule}'")

def list_tasks():
    crontab = get_crontab()
    if not crontab:
        print("(no crontab entries)")
        return
    for line in crontab.splitlines():
        if line.startswith(MARKER_PREFIX):
            print(line[len(MARKER_PREFIX):].strip())
        elif line.strip():
            print("  [user] " + line.strip())

def remove_task(name):
    crontab = get_crontab()
    lines = [l for l in crontab.splitlines() if not (l.startswith(MARKER_PREFIX) and name in l)]
    set_crontab("\n".join(lines) + "\n")
    print(f"[OK] Removed '{name}'")

def update_task(name, schedule, url):
    remove_task(name)
    add_task(name, schedule, url)

def main():
    if len(sys.argv) < 2:
        print("usage: cron_manager.py <add|list|remove|update> ...")
        sys.exit(1)

    cmd = sys.argv[1]
    try:
        if cmd == "add" and len(sys.argv) == 5:
            add_task(sys.argv[2], sys.argv[3], sys.argv[4])
        elif cmd == "list":
            list_tasks()
        elif cmd == "remove" and len(sys.argv) == 3:
            remove_task(sys.argv[2])
        elif cmd == "update" and len(sys.argv) == 5:
            update_task(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            print("invalid arguments")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()