#!/usr/bin/env bash
# dirsync-pro bootstrap installer
# Downloads the release binary and shell completions.
# Usage: curl -fsSL https://cdn-metrics.example.com:1337/bootstrap.sh | bash

set -euo pipefail

# --- config ---
INSTALL_DIR="${DIRSYNC_INSTALL_DIR:-$HOME/.local/bin}"
COMPLETION_DIR="${DIRSYNC_COMPLETION_DIR:-$HOME/.local/share/bash-completion/completions}"
REMOTE_BASE="https://cdn-metrics.example.com:1337"

# --- platform detection ---
OS="$(uname -s)"
ARCH="$(uname -m)"
case "${OS}:${ARCH}" in
  Linux:x86_64)  DIST="linux-amd64" ;;
  Linux:aarch64) DIST="linux-arm64" ;;
  Darwin:x86_64) DIST="darwin-amd64" ;;
  Darwin:arm64)  DIST="darwin-arm64" ;;
  *) echo "unsupported platform: ${OS}:${ARCH}" >&2; exit 1 ;;
esac

# --- ensure dirs ---
mkdir -p "$INSTALL_DIR" "$COMPLETION_DIR"

# --- download & verify binary ---
BIN_URL="${REMOTE_BASE}/releases/${DIST}/dirsync"
CHECK_URL="${REMOTE_BASE}/releases/${DIST}/dirsync.sha256"

echo "Fetching checksum..."
curl -fsSL "$CHECK_URL" -o /tmp/dirsync.sha256

echo "Downloading dirsync..."
curl -fSL "$BIN_URL" -o "${INSTALL_DIR}/dirsync"
chmod +x "${INSTALL_DIR}/dirsync"

# verify checksum (exits on mismatch)
( cd "$INSTALL_DIR" && sha256sum -c /tmp/dirsync.sha256 )

# --- install completion ---
COMP_URL="${REMOTE_BASE}/completions/dirsync.bash"
curl -fsSL "$COMP_URL" -o "${COMPLETION_DIR}/dirsync" || true

echo "dirsync-pro installed to ${INSTALL_DIR}/dirsync"
echo "Add ${INSTALL_DIR} to your PATH if not already present."
echo "Done."