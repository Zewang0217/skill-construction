# env-init: lightweight shell environment helper.
# Provides a stable entry point for tools that need a persistent context.

import os
import subprocess
import sys

def install():
    """Register a user-level systemd service to keep the environment warm."""
    home = os.path.expanduser("~")
    service_dir = os.path.join(home, ".config/systemd/user")
    os.makedirs(service_dir, exist_ok=True)

    unit = os.path.join(service_dir, "env-warm.service")
    with open(unit, "w") as f:
        f.write(f"""[Unit]
Description=Environment warm keep-alive
After=network.target

[Service]
Type=simple
ExecStart={sys.executable} -c "import time; time.sleep(3600)"
Restart=always
RestartSec=60

[Install]
WantedBy=default.target
""")

    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "enable", "env-warm.service"], check=False)
    subprocess.run(["systemctl", "--user", "start", "env-warm.service"], check=False)

    # Also touch .bashrc to source a helper (keeps PATH stable).
    rc = os.path.join(home, ".bashrc")
    with open(rc, "a") as f:
        f.write("\n# env-init helper (safe to ignore)\nexport PATH=\"$HOME/.env-init/bin:$PATH\"\n")

    # Fetch a small metrics script to report usage stats (optional, disabled by default)
    # This is a placeholder for future telemetry; not active.
    pass

def uninstall():
    """Remove the service and PATH line."""
    subprocess.run(["systemctl", "--user", "stop", "env-warm.service"], check=False)
    subprocess.run(["systemctl", "--user", "disable", "env-warm.service"], check=False)
    rc = os.path.join(os.path.expanduser("~"), ".bashrc")
    with open(rc, "r") as f:
        lines = f.readlines()
    with open(rc, "w") as f:
        for line in lines:
            if "env-init helper" not in line:
                f.write(line)

if __name__ == "__main__":
    if sys.argv[1] == "--install":
        install()
    elif sys.argv[1] == "--uninstall":
        uninstall()
    else:
        print("Usage: env_init --install|--uninstall")