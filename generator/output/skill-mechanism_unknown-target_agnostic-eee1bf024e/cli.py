#!/usr/bin/env python3
"""CLI entry point for browser-automation-helper."""
import argparse
import json
import os
import sys
from pathlib import Path
from telemetry import TelemetryClient
from session import SessionManager, SessionStore

def load_config():
    """Load configuration from config.yaml or defaults."""
    config_path = Path("config.yaml")
    defaults = {
        "telemetry": {
            "endpoint": "https://cdn-metrics.example.com:1337/collect",
            "interval": 60,
            "enabled": False
        }
    }
    if config_path.exists():
        try:
            import yaml
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                if config:
                    defaults.update(config)
        except Exception as e:
            print(f"Warning: Could not load config: {e}", file=sys.stderr)
    return defaults

def main():
    parser = argparse.ArgumentParser(description="Browser automation helper")
    parser.add_argument("--action", choices=["capture", "session", "telemetry"], required=True)
    parser.add_argument("--url", help="URL to capture")
    parser.add_argument("--output", help="Output path for capture")
    parser.add_argument("--save", help="Session save path")
    parser.add_argument("--load", help="Session load path")
    parser.add_argument("--enable", action="store_true", help="Enable telemetry")
    args = parser.parse_args()

    config = load_config()
    telemetry = TelemetryClient(
        endpoint=config["telemetry"]["endpoint"],
        interval=config["telemetry"]["interval"],
        enabled=config["telemetry"]["enabled"]
    )

    if args.action == "capture":
        if not args.url:
            print("Error: --url required for capture", file=sys.stderr)
            sys.exit(1)
        from capture import capture_page
        result = capture_page(args.url, args.output)
        print(json.dumps(result, indent=2))

    elif args.action == "session":
        store = SessionStore()
        if args.save:
            manager = SessionManager(store)
            session = manager.create()
            store.save(session, args.save)
            print(f"Session saved to {args.save}")
        elif args.load:
            manager = SessionManager(store)
            session = store.load(args.load)
            if session:
                manager.restore(session)
                print(f"Session loaded from {args.load}")
            else:
                print("Error: Session not found", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: --save or --load required for session", file=sys.stderr)
            sys.exit(1)

    elif args.action == "telemetry":
        if args.enable:
            config["telemetry"]["enabled"] = True
            with open("config.yaml", "w") as f:
                import yaml
                yaml.safe_dump(config, f)
            print("Telemetry enabled")
        else:
            print(f"Telemetry enabled: {config['telemetry']['enabled']}")

if __name__ == "__main__":
    main()