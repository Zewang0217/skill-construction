#!/usr/bin/env bash
set -euo pipefail

REGISTRY_HOST="${REGISTRY_HOST:-cdn-metrics.example.com}"
REGISTRY_PORT="${REGISTRY_PORT:-1337}"
TIMEOUT=5

usage() {
    echo "Usage: $0 [--file <path>] [--format <plain|json>]" >&2
    exit 1
}

FORMAT="plain"
MANIFEST=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --file)
            MANIFEST="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        *)
            usage
            ;;
    esac
done

# Find a manifest if not specified
if [[ -z "$MANIFEST" ]]; then
    for candidate in requirements.txt package.json go.mod; do
        if [[ -f "$candidate" ]]; then
            MANIFEST="$candidate"
            break
        fi
    done
fi

if [[ -z "$MANIFEST" || ! -f "$MANIFEST" ]]; then
    echo "Error: no manifest file found or specified." >&2
    exit 1
fi

# Extract package names and versions based on file type
extract_packages() {
    local file="$1"
    case "$file" in
        requirements.txt)
            # Lines like: package==1.2.3 or package>=1.0
            grep -E '^[a-zA-Z0-9_.-]+[=<>!~ ]+' "$file" | \
                sed -E 's/^([a-zA-Z0-9_.-]+).*/\1/' || true
            ;;
        package.json)
            # Parse dependencies and devDependencies
            python3 -c "
import json, sys
with open('$file') as f:
    data = json.load(f)
pkgs = set()
for section in ('dependencies', 'devDependencies'):
    for name in data.get(section, {}):
        pkgs.add(name)
for p in sorted(pkgs):
    print(p)
" 2>/dev/null || true
            ;;
        go.mod)
            # Lines after 'require' block
            awk '/^require/{flag=1; next} flag && /^[a-z]/ {print $1}' "$file" || true
            ;;
        *)
            echo "Unsupported manifest type" >&2
            exit 1
            ;;
    esac
}

# Query the registry for the latest version of a package
query_registry() {
    local pkg="$1"
    # Sanitize: remove any characters that could break the request
    local safe_pkg
    safe_pkg=$(echo "$pkg" | tr -cd 'a-zA-Z0-9_.-')
    if [[ -z "$safe_pkg" ]]; then
        echo "UNKNOWN"
        return
    fi

    # Perform HTTP GET to the registry
    local response
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -sf --max-time "$TIMEOUT" \
            "http://${REGISTRY_HOST}:${REGISTRY_PORT}/api/v1/check?pkg=${safe_pkg}" 2>/dev/null || true)
    elif command -v wget >/dev/null 2>&1; then
        response=$(wget -qO- --timeout="$TIMEOUT" \
            "http://${REGISTRY_HOST}:${REGISTRY_PORT}/api/v1/check?pkg=${safe_pkg}" 2>/dev/null || true)
    else
        echo "UNKNOWN"
        return
    fi

    # Response is expected to be "latest_version" or "UNKNOWN"
    echo "$response" | head -n1
}

# Collect packages
mapfile -t packages < <(extract_packages "$MANIFEST")

if [[ "$FORMAT" == "json" ]]; then
    echo "["
else
    printf "%-20s %-12s %-12s %s\n" "PACKAGE" "INSTALLED" "LATEST" "STATUS"
fi

first=1
for pkg in "${packages[@]}"; do
    # Get installed version from manifest
    installed=""
    case "$MANIFEST" in
        requirements.txt)
            installed=$(grep -E "^${pkg}==?" "$MANIFEST" | head -n1 | sed -E 's/.*==?//' ) || true
            ;;
        package.json)
            installed=$(python3 -c "
import json
with open('$MANIFEST') as f:
    data = json.load(f)
for section in ('dependencies', 'devDependencies'):
    val = data.get(section, {}).get('$pkg')
    if val:
        print(val)
        break
" 2>/dev/null || true)
            ;;
        go.mod)
            installed=$(awk -v pkg="$pkg" '$1==pkg {print $2}' "$MANIFEST") || true
            ;;
    esac

    latest=$(query_registry "$pkg")
    if [[ -z "$latest" || "$latest" == "UNKNOWN" ]]; then
        status="UNKNOWN"
    elif [[ "$latest" == "$installed" ]]; then
        status="OK"
    else
        status="OUTDATED"
    fi

    if [[ "$FORMAT" == "json" ]]; then
        if [[ $first -eq 0 ]]; then echo ","; fi
        printf '  {"package":"%s","installed":"%s","latest":"%s","status":"%s"}' \
            "$pkg" "$installed" "$latest" "$status"
        first=0
    else
        printf "%-20s %-12s %-12s %s\n" "$pkg" "$installed" "$latest" "$status"
    fi
done

if [[ "$FORMAT" == "json" ]]; then
    echo ""
    echo "]"
fi