#!/usr/bin/env python3
"""Fill a form template with values from a CSV/JSON source."""

import argparse
import json
import sys

def fill_template(template: dict, values: dict) -> dict:
    """Merge values into template, preserving unknown keys."""
    filled = {"form_id": template.get("form_id", ""), "values": {}}
    for key, default in template.get("values", {}).items():
        filled["values"][key] = values.get(key, default)
    return filled


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, help="Template JSON file")
    parser.add_argument("--values", required=True, help="Values JSON file")
    args = parser.parse_args()

    with open(args.template) as fh:
        template = json.load(fh)
    with open(args.values) as fh:
        values = json.load(fh)

    print(json.dumps(fill_template(template, values), indent=2))


if __name__ == "__main__":
    main()