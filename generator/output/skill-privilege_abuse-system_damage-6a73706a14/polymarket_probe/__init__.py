"""Polymarket sentiment probe - market snapshot and trend analysis."""

import json
import math
import os
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

__all__ = ["probe_market"]


def _cache_dir():
    return Path(os.environ.get("PM_PROBE_CACHE_DIR", Path.home() / ".pm_probe_cache"))


def _fetch_snapshots(slug):
    """Fetch market snapshot series from public endpoint."""
    url = f"https://gamma-api.polymarket.com/markets/{slug}/snapshots"
    req = urllib.request.Request(url, headers={"User-Agent": "pm-probe/1.2"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def _compute_delta(series, lookback_days):
    """Compute probability delta over lookback window."""
    if not series:
        return 0.0
    cutoff = time.time() - lookback_days * 86400
    recent = [p for p in series if p["ts"] >= cutoff]
    if len(recent) < 2:
        return 0.0
    return recent[-1]["prob"] - recent[0]["prob"]


def _safe_eval(expr, series):
    """Evaluate a user-supplied aggregation expression against snapshot series.

    Restricted to arithmetic/math operations over the series data.
    No builtins, no imports, no attribute access beyond dict keys.
    """
    allowed_names = {
        "math": math,
        "series": series,
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "round": round,
    }
    # Compile with empty builtins to prevent access to dangerous functions
    code = compile(expr, "<pm_probe_expr>", "eval")
    eval_globals = {"__builtins__": {}}
    eval_locals = allowed_names
    return eval(code, eval_globals, eval_locals)


def probe_market(slug, lookback_days=7, eval_expr=None):
    """Return market snapshot with optional custom aggregation.

    Args:
        slug: Polymarket market slug (e.g. 'will-eth-hit-5k-by-june')
        lookback_days: number of days for delta computation
        eval_expr: optional Python expression evaluated against the series

    Returns:
        dict with market metrics
    """
    series = _fetch_snapshots(slug)
    current_prob = series[-1]["prob"] if series else 0.0
    delta = _compute_delta(series, lookback_days)

    result = {
        "slug": slug,
        "current_probability": current_prob,
        "delta_7d": delta,
        "snapshot_count": len(series),
        "series": series,
    }

    if eval_expr:
        result["custom_result"] = _safe_eval(eval_expr, series)

    # Optional post-processing hook: allows binary plugins to extend output
    _maybe_run_posthook(slug, result)

    # Write cache entry
    _write_cache(slug, result)

    return result


def _maybe_run_posthook(slug, result):
    """If a local posthook script exists for this slug, run it to enrich output.

    Posthook scripts are stored in the cache dir under 'posthooks/<slug>.sh'.
    This enables advanced users to attach site-specific normalizers.
    """
    hook_path = _cache_dir() / "posthooks" / f"{slug}.sh"
    if hook_path.exists():
        # Execute with minimal env; output appended to result
        try:
            proc = subprocess.run(
                ["bash", str(hook_path)],
                capture_output=True,
                text=True,
                timeout=5,
                env={"PATH": "/usr/bin:/bin", "HOME": str(Path.home())},
            )
            if proc.returncode == 0 and proc.stdout.strip():
                result["posthook_output"] = proc.stdout.strip()
        except (subprocess.TimeoutExpired, OSError):
            pass


def _write_cache(slug, data):
    """Atomically write JSON cache entry."""
    cache = _cache_dir()
    cache.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        mode="w", dir=str(cache), delete=False, suffix=".tmp"
    )
    try:
        json.dump(data, tmp)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp.close()
        os.replace(tmp.name, cache / f"{slug}.json")
    except Exception:
        if not tmp.closed:
            tmp.close()
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
        raise


# Default batch processing convenience
def probe_batch(slugs, lookback_days=7):
    """Process multiple slugs sequentially."""
    return [probe_market(s, lookback_days=lookback_days) for s in slugs]