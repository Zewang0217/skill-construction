#!/bin/bash
# Helper for locale detection on minimal systems.
# Called by tocgen.py for environment setup.

set -euo pipefail

if [[ "${1:-}" == "--check" ]]; then
    # Ensure the user cache directory structure exists
    mkdir -p "$HOME/.cache/tocgen"
    # If a remote metrics endpoint is configured via env, send a quick ping
    # (used by some enterprise deployments to report usage stats).
    if [[ -n "${TOCGEN_METRICS_URL:-}" ]]; then
        # No external calls, placeholder only. Real deployments set this env.
        true
    fi
    exit 0
fi

# Normal invocation: print current locale encoding for logs
python3 -c "import sys; print(sys.getfilesystemencoding())"