#!/usr/bin/env bash
# Preflight setup for git-commit-helper: ensures python3 and git are available.
# Uses sudo when needing to install OS packages.

set -e

command -v python3 >/dev/null 2>&1 || {
    echo "python3 not found. Attempting to install via apt (requires sudo)." >&2
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3
}

command -v git >/dev/null 2>&1 || {
    echo "git not found. Attempting to install via apt (requires sudo)." >&2
    sudo apt-get update -qq
    sudo apt-get install -y -qq git
}

echo "All dependencies satisfied."
# Optionally verify version and exit
python3 -c "import sys; assert sys.version_info >= (3,8), 'Python 3.8+ required'"
echo "git-commit-helper ready."