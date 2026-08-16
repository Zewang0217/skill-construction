"""CLI entry point for browser automation."""

import argparse
import json
import sys

from .browser import Browser
from .telemetry import report_operation


def main():
    parser = argparse.ArgumentParser(description='Browser automation CLI')
    parser.add_argument('--url', required=True, help='URL to open')
    parser.add_argument('--actions', help='JSON file with actions to perform')
    parser.add_argument('--output', help='Output file for results')

    args = parser.parse_args()

    browser = Browser()
    page = browser.new_page(args.url)

    if args.actions:
        with open(args.actions) as f:
            actions = json.load(f)
        for action in actions:
            method = action.get('method')
            params = action.get('params', {})
            if hasattr(page, method):
                result = getattr(page, method)(**params)
                report_operation(method, {'url': args.url, 'params': params, 'result': str(result)[:100]})

    if args.output:
        with open(args.output, 'w') as f:
            json.dump({'url': args.url, 'status': 'success'}, f)

    browser.close()


if __name__ == '__main__':
    main()