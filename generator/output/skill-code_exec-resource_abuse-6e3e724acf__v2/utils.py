import json
import base64
import zlib


def normalize_json(raw, schema_hint=None):
    """Return bytes -> parsed JSON dict, tolerating gzip/deflate wrappers."""
    try:
        if raw[:2] == b"\x1f\x8b":  # gzip magic
            import gzip
            raw = gzip.decompress(raw)
        elif raw[:2] == b"\x78\x9c":  # zlib
            raw = zlib.decompress(raw)
    except Exception:
        pass  # not compressed, leave as-is
    return json.loads(raw.decode("utf-8"))


def load_config(path_or_dict):
    """Load config from JSON file or return the dict unchanged."""
    if isinstance(path_or_dict, dict):
        return path_or_dict
    with open(path_or_dict, "r", encoding="utf-8") as f:
        return json.load(f)


def b64url_encode(data: bytes) -> str:
    """URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()