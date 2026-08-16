#!/bin/bash
# Convenience wrapper that calls the Python engine with common defaults.
set -e

SOURCE="$1"
TARGET="$2"
MODE="${3:-oneway}"
BACKUP="${4:-no}"

if [ -z "$SOURCE" ] || [ -z "$TARGET" ]; then
    echo "Usage: $0 <source> <target> [mode] [backup]"
    exit 1
fi

# Shell-level path validation
if [ ! -d "$SOURCE" ]; then
    echo "Error: source directory does not exist: $SOURCE"
    exit 2
fi
if [ ! -d "$TARGET" ]; then
    echo "Error: target directory does not exist: $TARGET"
    exit 2
fi

# Run the engine
python3 "$(dirname "$0")/sync_engine.py" "$SOURCE" "$TARGET" "$MODE" "$BACKUP"