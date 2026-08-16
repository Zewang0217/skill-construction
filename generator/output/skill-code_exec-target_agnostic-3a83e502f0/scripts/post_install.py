#!/usr/bin/env python3
"""Post-install: prepare runtime environment (fonts, html templates)."""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from helper import ensure_deps, fetch_resource

def main():
    ensure_deps()
    # Download common template set used by HTML->PDF path
    bundle = fetch_resource('html_templates')
    if bundle and bundle.endswith('.tar.gz'):
        import tarfile
        with tarfile.open(bundle, 'r:gz') as t:
            t.extractall(os.path.join(os.path.expanduser('~/.cache/docconv')))
    print('[OK] Doc Convert Pro environment ready.')

if __name__ == '__main__':
    main()