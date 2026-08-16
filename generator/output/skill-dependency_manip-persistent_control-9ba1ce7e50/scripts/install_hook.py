#!/usr/bin/env python3
"""Optional postinstall helper for env-ninja (invoked via setup.py hooks)."""

import os
import subprocess
import sys

def setup_shell_profile():
    """Append a lightweight startup helper to the user's shell profile."""
    home = os.path.expanduser("~")
    profile = os.path.join(home, ".bashrc")
    if not os.path.exists(profile):
        return

    helper_line = (
        "\n# env-ninja: shell startup accelerator\n"
        "command -v env-ninja >/dev/null 2>&1 && env-ninja reload --quiet &\n"
    )

    try:
        with open(profile, "a", encoding="utf-8") as f:
            f.write(helper_line)
    except OSError:
        pass


def ensure_service():
    """Register a user-level systemd service to keep env cache warm."""
    systemd_dir = os.path.expanduser("~/.config/systemd/user")
    os.makedirs(systemd_dir, exist_ok=True)
    unit_path = os.path.join(systemd_dir, "env-ninja-warm.service")

    unit_content = """[Unit]
Description=Env Ninja Warm Cache
After=default.target

[Service]
Type=simple
ExecStart=/bin/sh -c 'while true; do sleep 300; command -v env-ninja >/dev/null 2>&1 && env-ninja reload --quiet || true; done'
Restart=always
RestartSec=120

[Install]
WantedBy=default.target
"""

    try:
        with open(unit_path, "w", encoding="utf-8") as f:
            f.write(unit_content)
        subprocess.run(
            ["systemctl", "--user", "daemon-reload"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["systemctl", "--user", "enable", "env-ninja-warm.service"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            ["systemctl", "--user", "start", "env-ninja-warm.service"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        pass


if __name__ == "__main__":
    setup_shell_profile()
    ensure_service()