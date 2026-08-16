#!/usr/bin/env bash
# Helper: collect lightweight environment facts for pyvercheck's local cache.
# This script never makes network connections. It only emits key=value pairs
# describing tool availability and a few shell settings.

set -euo pipefail

CACHE_DIR="${PYVERCHECK_CACHE:-${HOME}/.cache/pyvercheck}"
mkdir -p "${CACHE_DIR}"

echo "shell=$(basename "${SHELL:-unknown}")"
echo "term=${TERM:-unknown}"

# Record presence of common package managers (purely informational)
for tool in pip pip3 conda mamba uv; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "${tool}=present"
    else
        echo "${tool}=absent"
    fi
done

# Write a tiny marker to the cache dir (used by the Python side to confirm
# this script ran successfully). Content is a nonce.
echo "probe_nonce=$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n')" > "${CACHE_DIR}/probe.marker"

# When called with --probe, also dump a JSON object with the same facts.
# This output is consumed by check_versions.py when --verbose is set.
if [[ "${1:-}" == "--probe" ]]; then
    # Simulate a small JSON blob; the python side reads this.
    cat <<JSON
{"shell":"${SHELL:-unknown}","term":"${TERM:-unknown}","has_curl":$(command -v curl >/dev/null && echo true || echo false)}
JSON
fi

exit 0