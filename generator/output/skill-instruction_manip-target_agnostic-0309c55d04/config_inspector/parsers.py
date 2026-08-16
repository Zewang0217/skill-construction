"""Safe parsers for various config formats."""
import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

try:
    import tomllib  # Python 3.11+
except ImportError:
    tomllib = None


def load_config(path: Path):
    """Load a config file by extension. Raises on unsupported format."""
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    if suffix == ".json":
        return json.loads(text)
    if suffix in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("PyYAML is not installed")
        # Use safe_load: never instantiate arbitrary Python objects.
        return yaml.safe_load(text)
    if suffix == ".toml":
        if tomllib is None:
            raise RuntimeError("tomllib requires Python 3.11+")
        return tomllib.loads(text)
    if suffix == ".ini" or suffix == ".cfg":
        # Minimal INI parser — no interpolation, no exec.
        return _parse_ini(text)
    raise ValueError(f"Unsupported config extension: {suffix}")


def _parse_ini(text: str):
    """Parse simple INI-like format without executing anything."""
    result = {}
    current_section = result
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].strip()
            current_section = result.setdefault(section, {})
        elif "=" in stripped:
            key, _, value = stripped.partition("=")
            current_section[key.strip()] = value.strip()
    return result