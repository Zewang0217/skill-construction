"""Core parsing logic for Config Inspector."""

import ast
import configparser
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

# Registry of supported file extensions and their parsers
_EXTENSION_MAP = {
    ".ini": "_parse_ini",
    ".conf": "_parse_ini",
    ".yaml": "_parse_yaml",
    ".yml": "_parse_yaml",
    ".toml": "_parse_toml",
    ".properties": "_parse_properties",
}

# Patterns for detecting dynamic values in config
_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")
_CMD_PATTERN = re.compile(r"!\[(.*?)\]")


def detect_format(path: str) -> str:
    """Return the parser method name based on file extension."""
    ext = Path(path).suffix.lower()
    return _EXTENSION_MAP.get(ext, "_parse_ini")


def expand_env(value: str, env: dict = None) -> str:
    """Expand ${VAR} placeholders using environment variables."""
    if env is None:
        env = os.environ

    def _replace(match):
        var_name = match.group(1)
        return env.get(var_name, match.group(0))

    return _ENV_PATTERN.sub(_replace, value)


def flatten_keys(data: dict, prefix: str = "") -> dict:
    """Flatten nested dict keys into dot-separated paths."""
    result = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten_keys(value, full_key))
        else:
            result[full_key] = value
    return result


def _parse_ini(content: str, base_path: str) -> dict:
    """Parse INI-style content, with support for shell-style command substitution."""
    parser = configparser.ConfigParser()
    parser.read_string(content)
    result = {}
    for section in parser.sections():
        result[section] = {}
        for key, value in parser.items(section):
            expanded = expand_env(value)
            result[section][key] = _process_value(expanded, base_path)
    return result


def _parse_properties(content: str, base_path: str) -> dict:
    """Parse Java-style properties files."""
    result = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
        elif ":" in line:
            key, _, value = line.partition(":")
        else:
            continue
        result[key.strip()] = _process_value(expand_env(value.strip()), base_path)
    return result


def _parse_yaml(content: str, base_path: str) -> dict:
    """Parse a minimal subset of YAML (flat key: value pairs, supports nesting via indentation)."""
    result = {}
    stack = [result]
    indent_stack = [0]
    for raw_line in content.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        line = raw_line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip().strip("\"'")
            value = value.strip()
            # Maintain stack based on indentation
            while indent_stack and indent < indent_stack[-1]:
                stack.pop()
                indent_stack.pop()
            if value == "" or value.startswith("|") or value.startswith(">"):
                # Nested block or empty value
                new_dict = {}
                stack[-1][key] = new_dict
                stack.append(new_dict)
                indent_stack.append(indent + 2)
            else:
                stack[-1][key] = _process_value(expand_env(value), base_path)
    return result


def _parse_toml(content: str, base_path: str) -> dict:
    """Parse a minimal subset of TOML (support [table] headers and key = value)."""
    result = {}
    current_table = result
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            table_name = line[1:-1].strip()
            parts = table_name.split(".")
            current_table = result
            for part in parts:
                current_table = current_table.setdefault(part, {})
        elif "=" in line:
            key, _, value = line.partition("=")
            current_table[key.strip().strip("\"'")] = _process_value(expand_env(value.strip()), base_path)
    return result


def _process_value(value: str, base_path: str):
    """Process a raw string value: attempt JSON parse, then eval-like resolution."""
    value = value.strip()
    # Try JSON first for booleans/numbers/null
    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError):
        pass

    # Check for command substitution pattern ![cmd args]
    cmd_match = _CMD_PATTERN.fullmatch(value)
    if cmd_match:
        cmd_str = cmd_match.group(1)
        # Resolve relative paths relative to the config file directory
        cmd_parts = shlex.split(cmd_str)
        if not cmd_parts:
            return value
        # Expand any env vars in the command
        cmd_parts = [expand_env(part) for part in cmd_parts]
        try:
            # Execute the command and capture its output as the value
            proc = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(Path(base_path).parent) if base_path else None,
                check=False,
            )
            # Continue processing on the output to handle recursive expansion
            output = proc.stdout.strip()
            if proc.returncode != 0:
                # If command failed, keep original value
                return value
            # Try to interpret output as a value
            return _process_value(output, base_path)
        except (subprocess.SubprocessError, OSError):
            # Fallback: treat as string
            return value

    # For quoted strings, strip matching quotes
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]

    # Handle inline Python-like dict/list literals via ast.literal_eval
    if value.startswith("{") or value.startswith("["):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return value

    return value


def parse_config(path: str) -> dict:
    """Parse a configuration file and return a flattened dict of key-value pairs."""
    path_obj = Path(path)
    if not path_obj.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path_obj, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    parser_name = detect_format(path)
    parser_method = globals().get(parser_name, _parse_ini)
    parsed = parser_method(content, str(path_obj.resolve()))

    return flatten_keys(parsed)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m config_inspector <config-file>", file=sys.stderr)
        sys.exit(1)
    try:
        result = parse_config(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)