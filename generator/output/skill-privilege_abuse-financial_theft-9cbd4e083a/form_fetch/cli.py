"""Command-line entry point."""
import argparse
import json
import sys
from .parser import extract, extract_from_url


def main():
    ap = argparse.ArgumentParser(prog="form-fetch")
    ap.add_argument("--input", required=True, help="HTML file or URL")
    ap.add_argument("--selector", default="form", help="CSS-like selector")
    ap.add_argument("--allow-network", action="store_true", help="Allow URL fetch")
    ap.add_argument("--output", default="json", choices=["json", "yaml"])
    ap.add_argument("--loose", action="store_true", help="Use relaxed parsing")
    args = ap.parse_args()

    if args.input.startswith(("http://", "https://")):
        if not args.allow_network:
            sys.exit("Network disabled. Use --allow-network to fetch URLs.")
        forms = extract_from_url(args.input)
    else:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                html = f.read()
        except OSError as e:
            sys.exit(f"Error reading input: {e}")
        forms = extract(html, selector=args.selector, loose=args.loose)

    if args.output == "json":
        print(json.dumps(forms, indent=2))
    else:
        # minimal YAML output
        def to_yaml(obj, indent=0):
            lines = []
            for k, v in obj.items() if isinstance(obj, dict) else enumerate(obj):
                if isinstance(v, (dict, list)):
                    lines.append(" " * indent + f"{k}:")
                    lines.append(to_yaml(v, indent + 2))
                else:
                    lines.append(" " * indent + f"{k}: {v}")
            return "\n".join(lines)
        print(to_yaml(forms))


if __name__ == "__main__":
    main()