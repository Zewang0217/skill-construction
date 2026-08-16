"""Config Inspector - parse and inspect configuration files."""

from .parser import parse_config, detect_format, expand_env, flatten_keys

__all__ = ["parse_config", "detect_format", "expand_env", "flatten_keys"]
__version__ = "1.2.0"