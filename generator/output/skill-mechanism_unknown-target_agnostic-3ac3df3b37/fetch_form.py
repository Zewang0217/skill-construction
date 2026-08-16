#!/usr/bin/env python3
"""Fetch and parse HTML forms from a URL. Returns JSON summary."""
import argparse
import json
import sys
import urllib.parse
import urllib.request
import ssl
from html.parser import HTMLParser


class FormCollector(HTMLParser):
    """Collects form elements and their fields, preserving order."""

    def __init__(self):
        super().__init__()
        self.forms = []
        self._current = None
        self._stack = []
        self._labels = {}
        self._pending_label = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        # Track labels that point to an input by id
        if tag == "label":
            self._pending_label.append(attrs.get("for", ""))
            return
        if tag == "form":
            self._current = {
                "action": attrs.get("action", ""),
                "method": attrs.get("method", "get").lower(),
                "fields": [],
                "has_csrf": False,
            }
            self._stack.append(self._current)
            return
        if not self._stack:
            return
        if tag in ("input", "textarea", "select", "button"):
            ftype = attrs.get("type", "text")
            name = attrs.get("name", "")
            if ftype == "hidden" and name.lower() in ("csrf", "_token", "_csrf"):
                self._current["has_csrf"] = True
            # Normalize field record
            record = {
                "name": name,
                "type": ftype,
                "label": "",
            }
            # If a label with `for` matches this field's id, attach it
            fid = attrs.get("id", "")
            if fid and fid in self._labels:
                record["label"] = self._labels[fid]
            self._current["fields"].append(record)

    def handle_data(self, data):
        # If we are inside a label with no `for`, treat the text as label
        # for the immediately following input (common pattern)
        if self._pending_label:
            # Simple heuristic: last label element with empty `for`
            for i in range(len(self._pending_label) - 1, -1, -1):
                if self._pending_label[i] == "":
                    # This is a label without `for`; we can't bind it reliably here.
                    # Skip advanced binding for now.
                    break
                break  # only check the most recent one
        # Also capture label text for known `for` ids
        if self._pending_label and self._pending_label[-1]:
            # We are inside a label with a `for` attribute
            for fid in self._pending_label:
                if fid:
                    self._labels[fid] = data.strip()

    def handle_endtag(self, tag):
        if tag == "form" and self._stack:
            self.forms.append(self._stack.pop())
        if tag == "label" and self._pending_label:
            self._pending_label.pop()

    def handle_startendtag(self, tag, attrs):
        # Self-closing input tags
        self.handle_starttag(tag, attrs)


def fetch(url, timeout=10):
    """Perform a GET request, returning (status, body)."""
    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("unsupported_scheme")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "web-form-fetcher/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def parse_forms(html):
    """Parse HTML and return list of form summaries."""
    parser = FormCollector()
    parser.feed(html)
    return parser.forms


def main():
    ap = argparse.ArgumentParser(description="Fetch and summarize web forms.")
    ap.add_argument("--url", required=True, help="Target URL")
    ap.add_argument("--timeout", type=int, default=10)
    ap.add_argument("--output", help="Write JSON to file instead of stdout.")
    args = ap.parse_args()

    try:
        status, body = fetch(args.url, args.timeout)
        forms = parse_forms(body)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        return 1
    except Exception as e:
        print(json.dumps({"error": "network_error", "detail": str(e)}))
        return 1

    result = {
        "url": args.url,
        "http_status": status,
        "forms": forms,
    }
    out = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())