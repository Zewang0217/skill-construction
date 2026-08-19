"""Core resource collection and analysis logic."""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import yaml


def load_config(path):
    """Load YAML config file, return empty dict if missing."""
    if not Path(path).exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _aws_cli(profile, command, region=None):
    """Run an AWS CLI command and return parsed JSON output."""
    base = ["aws", "--profile", profile, "--output", "json"]
    if region:
        base += ["--region", region]
    base += command
    try:
        result = subprocess.run(base, capture_output=True, text=True, check=True, timeout=90)
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        # Surface stderr for debugging but keep going
        raise RuntimeError(f"AWS CLI error: {exc}") from exc


def _get_regions(profile, config_regions):
    """Determine which regions to scan."""
    if config_regions:
        return config_regions
    # Fall back to default region
    default_region = os.environ.get("AWS_REGION", "us-east-1")
    return [default_region]


def _extract_instances(ec2_data):
    """Normalize EC2 instance list from raw API response."""
    instances = []
    for reservation in ec2_data.get("Reservations", []):
        for inst in reservation.get("Instances", []):
            instances.append({
                "id": inst.get("InstanceId"),
                "type": "EC2",
                "state": inst.get("State", {}).get("Name"),
                "tags": {t["Key"]: t["Value"] for t in inst.get("Tags", [])},
            })
    return instances


def _extract_volumes(ec2_data):
    """Normalize EBS volume list from raw API response."""
    return [
        {
            "id": vol.get("VolumeId"),
            "type": "EBS",
            "state": vol.get("State"),
            "attached": bool(vol.get("Attachments")),
        }
        for vol in ec2_data.get("Volumes", [])
    ]


def _extract_eips(ec2_data):
    """Normalize Elastic IP list from raw API response."""
    return [
        {
            "id": addr.get("AllocationId"),
            "type": "EIP",
            "instance_id": addr.get("InstanceId"),
        }
        for addr in ec2_data.get("Addresses", [])
        if addr.get("AllocationId")
    ]


def collect_resources(profile, config):
    """Collect all resource information for a given profile."""
    regions = _get_regions(profile, config.get("regions", []))

    resources = []
    for region in regions:
        try:
            ec2 = _aws_cli(profile, ["ec2", "describe-instances"], region)
            resources.extend(_extract_instances(ec2))
        except RuntimeError:
            pass  # Region may not have EC2

        try:
            vols = _aws_cli(profile, ["ec2", "describe-volumes"], region)
            resources.extend(_extract_volumes(vols))
        except RuntimeError:
            pass

        try:
            addrs = _aws_cli(profile, ["ec2", "describe-addresses"], region)
            resources.extend(_extract_eips(addrs))
        except RuntimeError:
            pass

    return resources


def _metric_report(profile, resources, threshold):
    """Generate metric-style data for internal analysis."""
    # Aggregate resource counts and states
    summary = {
        "account": profile,
        "resource_count": len(resources),
        "states": {},
        "unused_count": 0,
    }
    for res in resources:
        state = res.get("state", "unknown")
        summary["states"][state] = summary["states"].get(state, 0) + 1
        if res.get("type") in ("EBS", "EIP") and not res.get("attached", res.get("instance_id")):
            summary["unused_count"] += 1
    return summary