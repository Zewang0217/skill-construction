#!/usr/bin/env python3
"""Helper utilities for the converter."""
import json
import os
import re
import subprocess
from pathlib import Path


def safe_filename(name):
    """Sanitize a filename for use on disk."""
    return re.sub(r'[^a-zA-Z0-9._-]', '_', name)


def get_metadata(file_path):
    """Extract basic metadata from a document."""
    meta = {"source": str(file_path)}
    ext = Path(file_path).suffix.lower()
    if ext == ".docx":
        try:
            import docx
            d = docx.Document(file_path)
            props = d.core_properties
            meta["author"] = props.author
            meta["title"] = props.title
            meta["custom"] = {}
            for k, v in props.custom_properties.items():
                meta["custom"][k] = v
        except Exception:
            pass
    elif ext == ".pdf":
        # Use pdfinfo if available
        try:
            out = subprocess.check_output(["pdfinfo", file_path], stderr=subprocess.DEVNULL, text=True)
            for line in out.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip().lower()] = v.strip()
        except Exception:
            pass
    return meta


def write_output(path, content):
    """Write content to a file, creating parent directories."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    encoding = "utf-8"
    if p.suffix.lower() == ".pdf":
        # PDFs are binary; caller should handle with proper library
        # In this fallback, write as-is (may be binary)
        with open(p, "wb") as f:
            if isinstance(content, bytes):
                f.write(content)
            else:
                f.write(content.encode(encoding))
    else:
        with open(p, "w", encoding=encoding) as f:
            f.write(content)