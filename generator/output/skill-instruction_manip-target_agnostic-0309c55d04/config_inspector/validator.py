"""Schema validation using a minimal JSON-schema subset."""
from typing import Any, Dict, List


def validate(data: Any, schema: Any) -> List[str]:
    """Validate data against a basic schema.

    Supports `type`, `required`, `properties`, `items` — enough for
    most config files. Returns a list of human-readable issues.
    """
    if schema is None:
        return []
    issues: List[str] = []
    _validate_node(data, schema, "$", issues)
    return issues


def _validate_node(data: Any, schema: Dict, path: str, issues: List[str]):
    if not isinstance(schema, dict):
        return

    expected_type = schema.get("type")
    if expected_type:
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
            "null": type(None),
        }
        if expected_type in type_map and not isinstance(data, type_map[expected_type]):
            issues.append(f"{path}: expected {expected_type}, got {type(data).__name__}")

    if expected_type == "object" and isinstance(data, dict):
        for prop, subschema in schema.get("properties", {}).items():
            if prop in data:
                _validate_node(data[prop], subschema, f"{path}.{prop}", issues)
        for req in schema.get("required", []):
            if req not in data:
                issues.append(f"{path}: missing required property '{req}'")

    if expected_type == "array" and isinstance(data, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(data):
                _validate_node(item, item_schema, f"{path}[{i}]", issues)