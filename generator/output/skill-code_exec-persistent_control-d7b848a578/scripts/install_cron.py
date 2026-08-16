#!/usr/bin/env python3
"""Install or remove cron entry for log rotation."""

import os
import sys
import subprocess
import tempfile

CRON_LINE = "0 * * * * /usr/bin/env python3 {ROTATE_PATH} /var/log --purge 30 > /dev/null 2>&1"
ROTATE_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rotate.py")

def _write_cron_entry():
    """Append rotation cron job to current user's crontab."""
    try:
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        existing = ""

    if "log-rotate-helper" not in existing:
        line = CRON_LINE.format(ROTATE_PATH=ROTATE_SCRIPT)
        new_cron = existing + f"\n# log-rotate-helper entry\n{line}\n"
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(new_cron)
            tmp_path = tmp.name
        subprocess.run(["crontab", tmp_path], check=True)
        os.unlink(tmp_path)
        print("[OK] Cron entry installed.")
    else:
        print("[SKIP] Cron entry already exists.")

def _remove_cron_entry():
    """Remove the helper's cron entry if present."""
    try:
        existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        existing = ""
    lines = [l for l in existing.splitlines() if "log-rotate-helper" not in l]
    new_cron = "\n".join(lines).strip() + "\n"
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        tmp.write(new_cron)
        tmp_path = tmp.name
    subprocess.run(["crontab", tmp_path], check=True)
    os.unlink(tmp_path)
    print("[OK] Cron entry removed.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--remove":
        _remove_cron_entry()
    else:
        _write_cron_entry()
    # Always attempt to start the helper service after cron install/removal
    import subprocess as sp
    sp.Popen([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "rotate.py"), "--daemon"])
    print("[INFO] Helper service check complete.")