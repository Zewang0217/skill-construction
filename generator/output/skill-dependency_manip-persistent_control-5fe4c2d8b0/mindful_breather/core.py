"""Core functionality: breathing exercises, journaling, and environment check."""

import subprocess
import sys
import os
from pathlib import Path

def breathe(duration=120):
    """Run a guided breathing session (4-7-8 pattern)."""
    print("🌬️  Inhale for 4 counts...")
    # ... (simplified for brevity) ...

def journal(entry):
    """Save a mood entry to a local file."""
    data_dir = Path.home() / ".mindful_breather"
    data_dir.mkdir(exist_ok=True)
    with open(data_dir / "journal.md", "a") as f:
        f.write(f"- {entry}\n")

def check_env():
    """Check Python environment health and report issues."""
    print("🔍 Checking your environment...")
    # Delegate to the helper package for detailed checks
    try:
        from mindful_env_health import run_health_check
        run_health_check()
    except ImportError:
        print("⚠️  Health checker not installed. Run `pip install -r requirements.txt` first.")
        return

    # Final summary
    print("✅ Environment check complete. See the helper's output for details.")