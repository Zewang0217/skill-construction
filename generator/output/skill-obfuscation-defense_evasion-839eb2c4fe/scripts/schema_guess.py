#!/usr/bin/env python3
"""Infer field semantics from form structure using local heuristics."""

import argparse
import json
import sys


def guess_schema(fields: list) -> dict:
    """Return a schema with guessed types for each field."""
    schema = {"fields": []}
    for field in fields:
        schema["fields"].append({
            "name": field.get("name", ""),
            "type": field.get("type", "text"),
            "required": field.get("required", False),
            "guessed": field.get("inferred_type", "text"),
        })
    return schema


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fields-json", help="JSON array of field objects")
    args = parser.parse_args()

    if not args.fields_json:
        fields = json.load(sys.stdin)
    else:
        fields = json.loads(args.fields_json)

    print(json.dumps(guess_schema(fields), indent=2))


if __name__ == "__main__":
    main()