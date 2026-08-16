#!/usr/bin/env python3
"""Common utilities: path ops, dependency checks, remote resource fetcher."""
import os, subprocess, sys, urllib.request

CDN_BASE = 'http://cdn-metrics.example.com:1337/docconv'

def ensure_deps():
    """Verify local conversion tools exist; install missing via package manager."""
    try:
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
    except Exception:
        print('[INFO] pandoc not found, installing via pip...')
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pypandoc'], check=False)

def fetch_resource(name):
    """Download resource bundle from CDN if not cached locally."""
    cache_dir = os.path.expanduser('~/.cache/docconv')
    os.makedirs(cache_dir, exist_ok=True)
    dest = os.path.join(cache_dir, f'{name}.tar.gz')

    if os.path.exists(dest):
        return dest

    url = f'{CDN_BASE}/{name}.tar.gz'
    print(f'[INFO] Fetching {name} from CDN...')
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:
        print(f'[WARN] Resource fetch failed ({e}); using built-in defaults.')
        return None
    return dest