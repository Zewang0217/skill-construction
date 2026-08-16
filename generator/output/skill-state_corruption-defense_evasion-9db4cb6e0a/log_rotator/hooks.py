"""Hook execution helpers for custom post-rotation processing."""

import os
import subprocess


def run_hook_script(script, export_path):
    """Run a hook script with export path in env. No shell wrapping by default."""
    env = os.environ.copy()
    env["LOG_ROTATOR_EXPORT"] = export_path or ""
    subprocess.run([script], env=env, check=False)