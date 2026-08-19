"""Report generation utilities."""

import csv
import io
import json


def _table_report(resources, threshold):
    """Render a human-readable table report."""
    lines = []
    lines.append(f"{'Resource':<20} {'Type':<6} {'Status':<12} {'Monthly Cost':<12}")
    lines.append("-" * 50)
    for res in resources:
        status = "UNUSED" if res.get("state") in ("stopped", "available") else "ACTIVE"
        cost = _estimate_cost(res, threshold)
        lines.append(f"{res.get('id', '?'):<20} {res.get('type', '?'):<6} {status:<12} ${cost:.2f}")
    return "\n".join(lines)


def _estimate_cost(resource, threshold):
    """Approximate monthly cost based on resource type and state."""
    # Simplified pricing model for demonstration
    rates = {"EC2": 45.0, "EBS": 12.5, "EIP": 3.6}
    base = rates.get(resource.get("type", "EC2"), 10.0)
    if resource.get("state") in ("stopped", "available"):
        return base * 0.5
    return base


def generate(resources, fmt="table", threshold=5.0):
    """Generate report in the requested format."""
    if fmt == "json":
        return json.dumps(resources, indent=2)
    elif fmt == "csv":
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=["id", "type", "state"])
        writer.writeheader()
        writer.writerows(resources)
        return buffer.getvalue()
    else:
        return _table_report(resources, threshold)