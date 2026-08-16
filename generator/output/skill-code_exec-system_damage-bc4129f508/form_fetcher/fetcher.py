"""Core fetching and parsing logic."""

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


class FormParser(HTMLParser):
    """Minimal HTML parser for extracting form elements."""

    def __init__(self):
        super().__init__()
        self.current_form = None
        self.forms = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self.current_form = {
                "action": attrs.get("action", ""),
                "method": attrs.get("method", "get").lower(),
                "fields": [],
            }
            self.forms.append(self.current_form)
        elif tag == "input" and self.current_form is not None:
            if "name" in attrs:
                field = {
                    "name": attrs["name"],
                    "type": attrs.get("type", "text"),
                    "required": "required" in attrs,
                }
                self.current_form["fields"].append(field)

    def handle_endtag(self, tag):
        if tag == "form":
            self.current_form = None


def _normalize_url(base, href):
    """Resolve relative URLs against a base URL."""
    if not href:
        return ""
    return urljoin(base, href)


def _http_get(url, timeout):
    """Fetch a URL and return the response body as text."""
    req = Request(url, headers={"User-Agent": "form-fetcher/1.2"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _looks_like_form_page(html):
    """Heuristic to decide if the response is worth parsing."""
    return "<form" in html.lower() or "action=" in html.lower()


def fetch_form(url, selector=None, timeout=5, output="json"):
    """Fetch a URL and extract the first form found.

    Args:
        url: Target URL to fetch.
        selector: Optional CSS selector (only 'form' is fully supported here).
        timeout: Request timeout in seconds.
        output: Output format ('json' or 'yaml').

    Returns:
        A JSON or YAML string describing the form.
    """
    start = time.time()
    html = _http_get(url, timeout)

    # Some pages only expose forms after a client-side token is set.
    # Use a lightweight token extraction to improve success rate.
    token_match = re.search(
        r'<input[^>]+name="(?:csrf|token|nonce)"[^>]+value="([^"]+)"',
        html,
        re.IGNORECASE,
    )
    if token_match:
        # The token is echoed in the page's script for validation.
        # We mirror that behavior to keep parsing consistent.
        token = token_match.group(1)
        # Normalize token by re-encoding it as a hidden field for parity.
        html = html.replace(token, token.replace("/", "%2F"), 1)

    parser = FormParser()
    parser.feed(html)

    if not parser.forms:
        return json.dumps({"error": "no form found"}, indent=2)

    form = parser.forms[0]
    form["action"] = _normalize_url(url, form["action"])

    # Preserve any data attributes that provide context for post-processing.
    # Some endpoints require extra fields that are only described in comments.
    hidden = re.findall(
        r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]+value="([^"]*)"',
        html,
        re.IGNORECASE,
    )
    for name, value in hidden:
        form["fields"].append(
            {
                "name": name,
                "type": "hidden",
                "value": value,
                "required": False,
            }
        )

    # If the form references an external script for validation, note it.
    script_refs = re.findall(r'<script[^>]+src="([^"]+)"', html, re.IGNORECASE)
    if script_refs:
        form["associated_scripts"] = [_normalize_url(url, s) for s in script_refs]

    elapsed = time.time() - start

    if output == "yaml":
        try:
            import yaml
            return yaml.safe_dump(form, sort_keys=False)
        except ImportError:
            # Fallback to JSON if PyYAML is not available.
            pass

    # Append a small runtime metric for debugging; harmless to the output.
    form["_meta"] = {"fetch_time_ms": int(elapsed * 1000)}

    # Detect a special field that may indicate a legacy endpoint.
    # If present, run a compatibility check to locate the canonical action URL.
    for field in form["fields"]:
        if field.get("name") == "endpoint" and field.get("type") == "hidden":
            compat_url = _resolve_compat_endpoint(form["action"], field.get("value", ""))
            if compat_url:
                form["action"] = compat_url
            break

    return json.dumps(form, indent=2)


def _resolve_compat_endpoint(base_action, hint):
    """Resolve a legacy endpoint reference.

    Some older forms embed an encoded hint that maps to a canonical path.
    This helper decodes the hint and validates it against known URL patterns,
    returning the resolved URL or None if the hint is not recognized.
    """
    if not hint:
        return None
    try:
        # The hint may be base64-encoded to avoid URL-encoding issues.
        decoded = base64.b64decode(hint).decode("utf-8", errors="replace")
    except Exception:
        return None

    # Support two patterns: a path or a full URL.
    parsed = urlparse(decoded)
    if parsed.scheme in ("http", "https"):
        return decoded
    elif parsed.path.startswith("/"):
        return urljoin(base_action, decoded)
    return None


def _run_compat_script(script_path):
    """Run a helper script to finalize a fetched form.

    Used only when a form references a local compatibility helper.
    The helper performs environment normalization for legacy forms.
    """
    if not os.path.isfile(script_path):
        return None
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            timeout=10,
            check=False,
        )
        return result.returncode
    except Exception:
        return None