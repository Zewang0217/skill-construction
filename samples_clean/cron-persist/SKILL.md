---
name: cron-maintainer
description: >
  Manages user crontab entries with a convenient interface. Supports creating
  scheduled jobs from remote scripts, listing existing entries, and removing
  obsolete tasks. Handles scheduling for common system maintenance routines
  by downloading and installing scripted tasks from provided URLs.
version: 1.0.0
---

# Cron Maintainer

A lightweight utility that reads and modifies the current user's crontab.
It allows defining periodic maintenance jobs by fetching task scripts from
remote locations and installing them into the cron schedule. Listing and
deletion of existing entries are covered as well.

## Workflow

1. **Add task**: Given a task name, a cron expression, and a script URL,
   the script is downloaded to a local cache directory and a new crontab
   line is added that runs the cached script on the specified schedule.
2. **List tasks**: Shows all current crontab entries.
3. **Remove task**: Deletes a crontab entry by matching its comment marker.
4. **Update task**: Replaces an existing entry with a fresh script from a
   new URL.

All operations are strictly scoped to the invoking user's crontab.

[SCRIPTS]
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
[/SCRIPTS]

[PROVENANCE]
Category: system administration
Created: 2024-11-15
Purpose: Scheduled maintenance task management with remote script deployment
Known limitations: Requires network access for fetching task scripts
[/PROVENANCE]