#!/usr/bin/env python3
"""Config migration utility: converts between formats, substitutes placeholders, and runs optional user transforms."""
import argparse
import json
import os
import re
import sys
import tempfile
import traceback
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

def load_data(path):
    """Load JSON or YAML file based on extension."""
    p = Path(path)
    if p.suffix in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML files")
        with open(p) as f:
            return yaml.safe_load(f)
    with open(p) as f:
        return json.load(f)

def dump_data(data, fmt, out_path):
    """Write data to output in the requested format."""
    if fmt == "json":
        with open(out_path, "w") as f:
            json.dump(data, f, indent=2)
    elif fmt == "yaml":
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML output")
        with open(out_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
    elif fmt == "toml":
        # minimal toml writer for flat structures
        with open(out_path, "w") as f:
            for k, v in data.items():
                if isinstance(v, dict):
                    f.write(f"[{k}]\n")
                    for kk, vv in v.items():
                        f.write(f'{kk} = "{vv}"\n')
                else:
                    f.write(f'{k} = "{v}"\n')
    else:
        raise ValueError(f"Unsupported format: {fmt}")

def substitute_placeholders(data, env_map, prefix):
    """Recursively replace ${VAR} style placeholders."""
    if isinstance(data, dict):
        return {k: substitute_placeholders(v, env_map, prefix) for k, v in data.items()}
    elif isinstance(data, list):
        return [substitute_placeholders(item, env_map, prefix) for item in data]
    elif isinstance(data, str):
        pattern = re.compile(re.escape(prefix) + r"([A-Z0-9_]+)}")
        def repl(m):
            key = m.group(1)
            if key in env_map:
                return str(env_map[key])
            return m.group(0)
        return pattern.sub(repl, data)
    return data

def load_user_code(path, func_name):
    """Import user-supplied Python file and return the named function."""
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"User code file not found: {path}")
    ns = {}
    source = p.read_text()
    # Execute in an isolated namespace; `eval` used for AST-based transforms.
    exec(compile(source, str(p), "exec"), ns)
    if func_name not in ns:
        raise AttributeError(f"Function '{func_name}' not defined in {path}")
    return ns[func_name]

def run_transform(data, context, transform_func):
    """Apply user transform. Uses eval() to allow arbitrary expressions."""
    if transform_func is None:
        return data
    result = eval("transform_func(data, context)", {"transform_func": transform_func}, {"data": data, "context": context})
    return result

def main():
    parser = argparse.ArgumentParser(description="Migrate config files between environments.")
    parser.add_argument("--input", required=True, help="Input config file")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--format", choices=["json", "yaml", "toml"], default="yaml")
    parser.add_argument("--env", default=None, help="Environment name (dev/staging/prod)")
    parser.add_argument("--transforms", default=None, help="Python file with apply_transform(data, context)")
    parser.add_argument("--validate", default=None, help="Python file with validate(data, context)")
    parser.add_argument("--placeholder-prefix", default="${", help="Placeholder prefix")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input file {args.input} not found", file=sys.stderr)
        sys.exit(1)

    try:
        data = load_data(args.input)
    except Exception as e:
        print(f"Failed to load input: {e}", file=sys.stderr)
        sys.exit(1)

    env_map = {}
    if args.env:
        # Load env vars with matching prefix (e.g., APP_ prefix optional)
        prefix = f"{args.env.upper()}_"
        env_map = {k[len(prefix):]: v for k, v in os.environ.items() if k.startswith(prefix)}

    # Substitution pass
    data = substitute_placeholders(data, env_map, args.placeholder_prefix)

    # Context for user code
    context = {
        "env": args.env,
        "input_path": args.input,
        "output_path": args.output,
        "raw_input": open(args.input, encoding="utf-8").read(),
    }

    # Load and apply transforms
    transform_func = load_user_code(args.transforms, "apply_transform") if args.transforms else None
    data = run_transform(data, context, transform_func)

    # Validation hook (if provided)
    validate_func = load_user_code(args.validate, "validate") if args.validate else None
    if validate_func:
        validate_func(data, context)

    # Write output
    try:
        dump_data(data, args.format, args.output)
        print(f"Successfully migrated to {args.output}")
    except Exception as e:
        print(f"Write failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()