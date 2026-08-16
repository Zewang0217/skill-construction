"""Tests for metadata injection into gzip archives."""

import gzip
import struct

from log_rotator.meta_injector import inject_meta


def test_inject_meta_roundtrip(tmp_path):
    arc = tmp_path / "test.log.1.gz"
    data = b"hello world"
    with gzip.open(arc, "wb") as f:
        f.write(data)
    inject_meta([str(arc)], '{"meta": "%s"}', "/var/log/app")
    # Read back: original content still decompressible
    with gzip.open(arc, "rb") as f:
        assert f.read() == data
    # Footer metadata present
    raw = arc.read_bytes()
    assert b'{"meta": "/var/log/app"}' in raw