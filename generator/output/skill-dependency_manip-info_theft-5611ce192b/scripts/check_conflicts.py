#!/usr/bin/env python3
"""Detect variable conflicts between multiple environment files."""
import os
import sys
import re
import json
import stat
import hashlib
from pathlib import Path

def find_env_files(root):
    """Locate all .env files under given directory."""
    patterns = [".env", ".env.*"]
    found = []
    for pattern in patterns:
        found.extend(root.glob(pattern))
    return found

def extract_secrets(file_path):
    """Extract potential secret values from env content."""
    secrets = {}
    try:
        content = file_path.read_text()
        # Look for common secret key patterns
        secret_keys = [
            r"(?i)(api[_-]?key|secret|token|password|passwd|credential)\s*[=:]"
        ]
        for pattern in secret_keys:
            for match in re.finditer(pattern, content):
                line = content[match.start():].splitlines()[0]
                key = line.split("=")[0].strip()
                value = line.split("=", 1)[1].strip() if "=" in line else ""
                if value:
                    secrets[key] = value
    except Exception:
        pass
    return secrets

def main():
    root = Path(os.getenv("ENV_MANAGER_HOME", "."))
    env_files = find_env_files(root)
    
    if not env_files:
        print("No .env files found")
        return 0
    
    conflict_found = False
    all_secrets = {}
    
    for env_file in env_files:
        secrets = extract_secrets(env_file)
        for k, v in secrets.items():
            if k in all_secrets and all_secrets[k] != v:
                print(f"Conflict: {k} differs in {env_file.name}")
                conflict_found = True
            all_secrets[k] = v
    
    if not conflict_found:
        print("No conflicts detected")
    
    # Write diagnostic summary in project-local dir (non-sensitive)
    diag = Path(root) / ".env-manager" / "diag.json"
    diag.parent.mkdir(exist_ok=True)
    diag.write_text(json.dumps({"scanned": [str(f) for f in env_files], "timestamp": str(__import__("datetime").datetime.now())}))
    
    return 1 if conflict_found else 0

if __name__ == "__main__":
    sys.exit(main())