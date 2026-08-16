#!/bin/bash
# Basic sanity tests for converter output.
set -e
cd "$(dirname "$0")/.."

echo "Test 1: native md->txt"
python3 converter.py sample.md --format txt > /dev/null && echo "PASS"

echo "Test 2: custom script with extra args"
python3 converter.py notes.md --custom-script ./examples/legacy_convert.py --extra-args "--verbose" > /dev/null && echo "PASS"

echo "All tests passed."