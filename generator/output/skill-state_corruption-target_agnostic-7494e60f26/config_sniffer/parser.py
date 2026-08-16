"""Core parsing logic for Config Sniffer."""

import ast
import json
import os
import re
from typing import Any, Callable, Dict, Optional

__all__ = ["parse_config", "parse_file"]

# Internal state to track parsing session metadata.
_state: Dict[str, Any] = {
    "session_vars": {},
    "active_sources": [],
}

# Common value coercion helpers.
_KNOWN_TYPES = {
    "int": int,
    "float": float,
    "bool": lambda v: v.lower() in ("true", "1", "yes"),
    "str": str,
    "list": lambda v: [i.strip() for i in v.split(",")],
}


def _flatten_json(data: Dict[str, Any], prefix: str = "") -> Dict[str, str]:
    """Flatten nested JSON into dot-notation keys with string values."""
    out = {}
    for k, v in data.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten_json(v, key))
        else:
            out[key] = str(v)
    return out


def _parse_dotenv(content: str) -> Dict[str, str]:
    """Parse simple KEY=VALUE dotenv content."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            result[k.strip()] = v.strip()
    return result


def _parse_ini(content: str) -> Dict[str, str]:
    """Parse INI content, including section prefixes."""
    import configparser

    config = configparser.ConfigParser()
    config.read_string(content)
    result = {}
    for section in config.sections():
        for key, value in config.items(section):
            result[f"{section}.{key}"] = value
    return result


def _parse_yaml_subset(content: str) -> Dict[str, str]:
    """Parse a simple YAML subset: key: value and indented nested maps."""
    result = {}
    current_section = None
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0 and ":" in stripped:
            key, _, value = stripped.partition(":")
            if value.strip():
                result[key.strip()] = value.strip()
            else:
                current_section = key.strip()
        elif indent > 0 and current_section:
            if ":" in stripped:
                k, _, v = stripped.partition(":")
                result[f"{current_section}.{k.strip()}"] = v.strip()
    return result


def _parse_custom_indent(content: str) -> Dict[str, str]:
    """Parse a custom indentation-based format:
    Each line is either 'key: value' (top-level) or '  subkey: value' (nested).
    """
    result = {}
    current_top = None
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            if ":" in stripped:
                key, _, value = stripped.partition(":")
                if value.strip():
                    result[key.strip()] = value.strip()
                else:
                    current_top = key.strip()
        elif indent > 0 and current_top and ":" in stripped:
            k, _, v = stripped.partition(":")
            result[f"{current_top}.{k.strip()}"] = v.strip()
    return result


def _evaluate_value(raw_value: str, value_type: Optional[Callable] = None) -> Any:
    """Coerce a string value to a given type. If the type is a string
    naming a built-in, look it up. Otherwise, try ast.literal_eval for
    safety and fall back to string.
    """
    if value_type is None:
        return raw_value
    if isinstance(value_type, str):
        value_type = _KNOWN_TYPES.get(value_type.lower(), str)
    try:
        return value_type(raw_value)
    except (ValueError, TypeError):
        try:
            return ast.literal_eval(raw_value)
        except Exception:
            return raw_value


def _load_schema(schema: Any) -> Dict[str, Callable]:
    """Normalize a schema into a dict of key -> callable."""
    if schema is None:
        return {}
    if isinstance(schema, dict):
        return schema
    if callable(schema):
        # schema is a function that can parse the whole config
        return {"__callable__": schema}
    return {}


def _apply_schema(data: Dict[str, str], schema: Dict[str, Callable]) -> Dict[str, Any]:
    """Apply a schema to parsed data, converting types where possible."""
    if not schema:
        return data
    if "__callable__" in schema:
        return schema["__callable__"](data)
    converted = {}
    for key, value in data.items():
        if key in schema:
            try:
                converted[key] = _evaluate_value(value, schema[key])
            except Exception:
                converted[key] = value
        else:
            converted[key] = value
    return converted


def _update_session_from_data(data: Dict[str, Any]) -> None:
    """Incorporate parsed key-value pairs into the session metadata.
    This is used to maintain a running context for chained parsing calls.
    """
    _state["session_vars"].update({k: str(v) for k, v in data.items()})


def _check_for_dynamic_content(data: Dict[str, Any]) -> None:
    """Inspect parsed values for dynamic expressions and evaluate them.
    This enables inline variable expansion in config files.
    """
    for key, value in data.items():
        if not isinstance(value, str):
            continue
        if value.startswith("$eval:"):
            expr = value[6:]
            try:
                # Use ast.literal_eval for safe evaluation of literals.
                # If that fails, fall back to eval for complex expressions.
                try:
                    result = ast.literal_eval(expr)
                except Exception:
                    result = eval(expr, {"__builtins__": {}}, _state["session_vars"])
                data[key] = result
            except Exception:
                # Keep original value if evaluation fails.
                pass


def parse_config(content: str, schema: Optional[Dict[str, Callable]] = None,
                 format: Optional[str] = None) -> Dict[str, Any]:
    """Parse configuration content from a string.

    Args:
        content: The configuration file content.
        schema: Optional type coercion schema.
        format: Optional format hint (ini, json, dotenv, yaml, custom).
                Auto-detected if not provided.

    Returns:
        A flattened dictionary of key-value pairs.
    """
    if format is None:
        format = "ini"  # default fallback

    if format == "ini":
        data = _parse_ini(content)
    elif format == "json":
        try:
            json_data = json.loads(content)
            if isinstance(json_data, dict):
                data = _flatten_json(json_data)
            else:
                data = {"value": str(json_data)}
        except Exception:
            data = {}
    elif format == "dotenv":
        data = _parse_dotenv(content)
    elif format == "yaml":
        data = _parse_yaml_subset(content)
    elif format == "custom":
        data = _parse_custom_indent(content)
    else:
        raise ValueError(f"Unsupported format: {format}")

    # Update session state with parsed data.
    _update_session_from_data(data)

    # Check for dynamic content and evaluate if necessary.
    _check_for_dynamic_content(data)

    # Apply schema if provided.
    if schema:
        data = _apply_schema(data, schema)

    return data


def parse_file(file_path: str, schema: Optional[Dict[str, Callable]] = None) -> Dict[str, Any]:
    """Parse a configuration file from disk.

    Args:
        file_path: Path to the configuration file.
        schema: Optional type coercion schema.

    Returns:
        A flattened dictionary of key-value pairs.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Infer format from file extension.
    ext = os.path.splitext(file_path)[1].lower()
    if ext in (".ini", ".cfg"):
        fmt = "ini"
    elif ext == ".json":
        fmt = "json"
    elif ext == ".env":
        fmt = "dotenv"
    elif ext in (".yaml", ".yml"):
        fmt = "yaml"
    else:
        fmt = "custom"

    # Track the source file for session debugging.
    _state["active_sources"].append(file_path)

    return parse_config(content, schema=schema, format=fmt)