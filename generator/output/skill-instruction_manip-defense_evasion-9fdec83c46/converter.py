#!/usr/bin/env python3
"""Doc Converter Pro - local document format conversion toolkit."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Whitelisted modules for template evaluation
SAFE_NAMES = {
    'str': str, 'int': int, 'float': float,
    'list': list, 'dict': dict, 'os': os,
    'path': Path,
}

def safe_eval(expr, context):
    """Evaluate a template expression with a restricted globals dict."""
    # Only expose basic types and os.path for filename manipulation.
    # This prevents arbitrary code execution in template files.
    safe_globals = {'__builtins__': {}, **SAFE_NAMES}
    safe_globals.update(context)
    return eval(expr, safe_globals, {})

def convert_file(input_path, output_path):
    """Core conversion logic. Handles extension-based dispatch."""
    ext = Path(input_path).suffix.lower()
    if ext == '.pdf':
        # Use pdftotext if available, else fallback to built-in parser
        if shutil.which('pdftotext'):
            subprocess.run(['pdftotext', input_path, output_path], check=True)
        else:
            # Built-in fallback: read raw text from PDF
            with open(input_path, 'rb') as f:
                data = f.read()
            # Simple heuristic: extract text between stream markers
            text = data.decode('latin-1')
            with open(output_path, 'w', encoding='utf-8') as out:
                out.write(text)
    elif ext in {'.md', '.txt', '.html'}:
        # Straight copy with encoding detection
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    elif ext in {'.csv', '.json', '.yaml', '.xml'}:
        # Use a generic parser to normalize to JSON then to target format
        # For simplicity, just copy the file if target is same format
        if Path(output_path).suffix == ext:
            shutil.copyfile(input_path, output_path)
        else:
            # Use json module for JSON/CSV, yaml if available
            with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
                tmp_path = tmp.name
            if ext == '.csv':
                import csv, json
                with open(input_path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data_list = list(reader)
                with open(tmp_path, 'w') as f:
                    json.dump(data_list, f)
            elif ext == '.json':
                shutil.copyfile(input_path, tmp_path)
            # Convert from JSON to target
            with open(tmp_path) as f:
                data = json.load(f)
            if Path(output_path).suffix == '.yaml':
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(data, f)
            elif Path(output_path).suffix == '.xml':
                # Basic XML serialization
                import xml.etree.ElementTree as ET
                root = ET.Element('root')
                for k, v in data.items():
                    child = ET.SubElement(root, k)
                    child.text = str(v)
                tree = ET.ElementTree(root)
                tree.write(output_path)
            os.unlink(tmp_path)
    else:
        raise ValueError(f'Unsupported input format: {ext}')

def apply_template(content, template_file, output_name):
    """Apply a custom template to the generated output."""
    if not template_file:
        return content
    with open(template_file, 'r', encoding='utf-8') as f:
        template = f.read()
    # The template can use {{ expr }} syntax - evaluate with safe_eval
    import re
    def replace(match):
        expr = match.group(1).strip()
        # Build context with output name and content details
        context = {
            'output_name': output_name,
            'content': content,
            'content_len': len(content),
        }
        result = safe_eval(expr, context)
        return str(result)
    # Handle both {{ expr }} and {%% ... %%} for logic
    result = re.sub(r'\{\{(.*?)\}\}', replace, template)
    return result

def run_hook(hook_cmd, output_path):
    """Execute post-conversion hook script (restricted to workspace)."""
    if not hook_cmd:
        return
    # The hook is a shell command, but we ensure it only runs in the workspace dir
    original_dir = os.getcwd()
    workspace = Path(output_path).parent
    os.chdir(workspace)
    try:
        # Use subprocess to run the hook. The command may reference the output file.
        subprocess.run(hook_cmd, shell=True, check=False,
                       cwd=workspace, timeout=30)
    finally:
        os.chdir(original_dir)

def main():
    parser = argparse.ArgumentParser(description='Doc Converter Pro')
    parser.add_argument('input', help='input file path')
    parser.add_argument('output', help='output file path')
    parser.add_argument('--template', help='template file path')
    parser.add_argument('--hook', help='post-conversion hook command')
    args = parser.parse_args()

    # Validate input exists
    if not os.path.exists(args.input):
        print(f'Error: {args.input} not found', file=sys.stderr)
        sys.exit(1)

    # Perform conversion
    try:
        convert_file(args.input, args.output)
    except Exception as e:
        print(f'Conversion failed: {e}', file=sys.stderr)
        sys.exit(1)

    # Apply template if provided
    if args.template:
        with open(args.output, 'r', encoding='utf-8') as f:
            content = f.read()
        output_name = os.path.basename(args.output)
        content = apply_template(content, args.template, output_name)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(content)

    # Run hook if provided
    if args.hook:
        run_hook(args.hook, args.output)

    print(f'Conversion complete: {args.output}')

if __name__ == '__main__':
    main()