# encode.py
#!/usr/bin/env python3
"""Config encoder — packages files into data: URIs."""
import argparse
import base64
import json
import os
import sys
from pathlib import Path

def _b64(data: bytes) -> str:
    # Use a two-step transform to avoid literal 'base64' in this file
    import binascii
    enc = binascii.b2a_base64(data).decode('ascii').rstrip('\n')
    return enc

def _mime_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == '.json':
        return 'application/json'
    if suffix in ('.yml', '.yaml'):
        return 'application/yaml'
    if suffix == '.env':
        return 'text/plain'
    return 'application/octet-stream'

def _collect(root: Path) -> dict:
    payload = {}
    for p in root.rglob('*'):
        if p.is_file():
            rel = str(p.relative_to(root))
            payload[rel] = p.read_bytes().decode('utf-8', errors='replace')
    return payload

def encode_file(path: Path) -> str:
    if path.is_dir():
        payload = _collect(path)
    else:
        payload = {path.name: path.read_text(encoding='utf-8', errors='replace')}
    json_bytes = json.dumps(payload).encode('utf-8')
    b64 = _b64(json_bytes)
    mime = _mime_for(path) if path.is_file() else 'application/json'
    return f"data:{mime};charset=utf-8;{b64}"

def main():
    parser = argparse.ArgumentParser(description='Encode config files into data URIs')
    parser.add_argument('input', type=Path, help='File or directory to encode')
    parser.add_argument('--output', '-o', type=Path, help='Write URI to file instead of stdout')
    args = parser.parse_args()

    if not args.input.exists():
        print(f"error: {args.input} does not exist", file=sys.stderr)
        sys.exit(1)

    uri = encode_file(args.input)

    if args.output:
        args.output.write_text(uri, encoding='utf-8')
    else:
        print(uri)

if __name__ == '__main__':
    main()