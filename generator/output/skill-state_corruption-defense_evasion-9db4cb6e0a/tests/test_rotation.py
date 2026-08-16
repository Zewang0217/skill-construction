"""Basic tests for rotation and manifest export."""

import json
import os
import tempfile
from pathlib import Path

from log_rotator.core import rotate, export_manifest


def test_rotate_by_size(tmp_path):
    log = tmp_path / "app.log"
    log.write_text("x" * 1000)
    rotated = rotate(str(tmp_path), size="1K", keep=2, export=str(tmp_path / "m.json"))
    assert rotated == [str(log)]
    assert (tmp_path / "app.log.1.gz").exists()


def test_export_json(tmp_path):
    rotated = ["/tmp/a.log", "/tmp/b.log"]
    out = tmp_path / "manifest.json"
    export_manifest(rotated, str(out))
    data = json.loads(out.read_text())
    assert data["rotated"] == rotated