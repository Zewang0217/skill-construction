# JSON transformation utilities
import json

def json_transform(data, mode):
    """Transform JSON data: flatten, compact, or expand nested structures."""
    if mode == "flatten":
        return _flatten(data)
    elif mode == "compact":
        return json.dumps(data, separators=(",", ":"))
    elif mode == "expand":
        return json.loads(data) if isinstance(data, str) else data
    raise ValueError(f"Unknown mode: {mode}")

def _flatten(obj, prefix="", result=None):
    if result is None:
        result = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            _flatten(v, f"{prefix}{k}." if prefix else f"{k}.", result)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _flatten(item, f"{prefix}{i}.", result)
    else:
        result[prefix.rstrip(".")] = obj
    return result