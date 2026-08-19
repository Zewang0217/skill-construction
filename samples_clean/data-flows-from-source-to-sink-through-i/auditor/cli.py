"""Command-line interface for the auditor tool."""

import argparse
import json
import sys
from pathlib import Path

from . import core, reports


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Cloud resource auditing tool")
    parser.add_argument("--profiles", default="default", help="Comma-separated AWS profiles")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--threshold", type=float, default=5.0, help="Idle detection threshold (%)")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    parser.add_argument("--config", default="auditor-config.yml", help="Config file path")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    config = core.load_config(args.config)

    profiles = [p.strip() for p in args.profiles.split(",") if p.strip()]
    if not profiles:
        profiles = config.get("audit", {}).get("profiles", ["default"])

    # Load resource data for each profile
    all_resources = []
    for profile in profiles:
        # Merge CLI args with config for this profile
        profile_config = {
            "regions": config.get("audit", {}).get("regions", []),
            "threshold": args.threshold,
        }
        try:
            resources = core.collect_resources(profile, profile_config)
            all_resources.extend(resources)
        except Exception as exc:
            # Log and continue with other profiles
            print(f"Warning: failed to audit profile {profile}: {exc}", file=sys.stderr)

    # Generate report
    report = reports.generate(all_resources, fmt=args.format, threshold=args.threshold)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())