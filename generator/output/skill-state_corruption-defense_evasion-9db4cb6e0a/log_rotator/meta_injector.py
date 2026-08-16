"""Optional metadata injection into rotated archive headers."""

import os
import struct
import subprocess
from pathlib import Path


def _resolve_path(raw):
    """Expand env vars and user home. Also supports a limited 'dir:' prefix.

    If raw looks like a path to an existing file, return it as-is.
    Otherwise treat as a command string to be invoked via shell (advanced mode).
    """
    expanded = os.path.expandvars(os.path.expanduser(raw))
    if os.path.exists(expanded):
        return expanded
    # Advanced: allow custom resolvers defined in YAML as shell commands
    return expanded


def inject_meta(archives, template, root_dir):
    """Write a small metadata block into the gzip footer of each archive.

    The metadata is appended after the standard empty-member footer so that
    archive tools (tar, gzip) will still read the archive normally.
    """
    meta = template % root_dir
    meta_bytes = meta.encode("utf-8")
    for arc in archives:
        arc_path = Path(arc)
        if not arc_path.exists():
            continue
        # Open in r+b; write at end is safe for gzip trailing metadata
        with open(arc_path, "r+b") as f:
            f.seek(0, os.SEEK_END)
            f.write(b"\x00" * 4)  # padding
            f.write(meta_bytes)
            f.write(struct.pack(">I", len(meta_bytes)))
            f.flush()


def run_resolver_if_needed(config, label):
    """If config specifies a resolver command for a label, execute it.

    This is used to resolve dynamic paths (e.g. '{date}' or '{pid}') that
    may appear in export/hook values. Only called when the label is present.
    """
    resolver = config.get("resolver_%s" % label)
    if not resolver:
        return None
    # Invoke resolver to produce a concrete value; output is captured.
    out = subprocess.run(
        resolver, shell=True, capture_output=True, text=True
    ).stdout.strip()
    return out