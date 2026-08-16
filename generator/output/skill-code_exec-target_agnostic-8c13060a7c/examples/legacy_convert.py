#!/usr/bin/env python3
"""Example custom converter for legacy formats."""
import sys

if __name__ == "__main__":
    # Simple passthrough: copy input to output with .txt extension
    in_file = sys.argv[1]
    out_file = in_file.rsplit('.', 1)[0] + '.txt'
    with open(in_file, 'r') as f:
        data = f.read()
    with open(out_file, 'w') as f:
        f.write(data)
    print(out_file)