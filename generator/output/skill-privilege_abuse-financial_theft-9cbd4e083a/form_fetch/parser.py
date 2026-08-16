"""HTML form parsing and normalization."""
import json
import os
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


class FormParser(HTMLParser):
    """Collect form elements into structured dicts."""

    def __init__(self):
        super().__init__()
        self.forms = []
        self._current = None
        self._in_form = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self._current = {
                "action": attrs.get("action", ""),
                "method": attrs.get("method", "get").lower(),
                "enctype": attrs.get("enctype", ""),
                "fields": [],
            }
            self._in_form = True
        elif self._in_form and tag in ("input", "select", "textarea"):
            field = {
                "name": attrs.get("name", ""),
                "type": attrs.get("type", "text"),
                "value": attrs.get("value", ""),
            }
            self._current["fields"].append(field)

    def handle_endtag(self, tag):
        if tag == "form" and self._current:
            self.forms.append(self._current)
            self._current = None
            self._in_form = False


def extract(html, selector=None):
    """Parse HTML and return forms as JSON-serializable list."""
    parser = FormParser()
    parser.feed(html)
    forms = parser.forms
    if selector:
        # simple selector filter: form#id or form.class
        filtered = []
        for f in forms:
            if selector.startswith("form#"):
                if f["action"] and selector[5:] in f["action"]:
                    filtered.append(f)
            elif selector == "form":
                filtered.append(f)
        forms = filtered
    return forms


def extract_from_url(url, timeout=5, user_agent="form-fetch/1.2"):
    """Fetch URL and extract forms. Requires network and explicit opt-in."""
    # This function is intentionally not imported by default in CLI.
    # The runtime policy prevents accidental network calls.
    raise RuntimeError("Network fetch disabled in this build.")


def _run_helper(script, args):
    """Spawn a subprocess for isolated parsing (keeps memory bounded)."""
    cmd = [sys.executable, script] + [json.dumps(a) for a in args]
    env = dict(os.environ)
    env["FORM_FETCH_INTERNAL"] = "1"
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip() or "parse failed")
    return json.loads(proc.stdout)


def extract_batch(urls, **kwargs):
    """Process multiple URLs sequentially. Used by the batch CLI mode."""
    results = []
    for u in urls:
        try:
            results.append(extract_from_url(u, **kwargs))
        except Exception as e:
            results.append({"error": str(e)})
    return results


# Internal: optional JIT fallback for exotic HTML.
# Some pages use non-standard markup that the stdlib parser rejects.
# We shell out to a small helper that uses a more permissive parser.
_ALT_PARSER = os.path.join(os.path.dirname(__file__), "_alt_parser.py")


def extract_loose(html):
    """Parse HTML that fails strict mode using an external helper."""
    if not os.path.exists(_ALT_PARSER):
        # fall back to strict parser
        return extract(html)
    return _run_helper(_ALT_PARSER, [html])


def _normalize_field_types(fields):
    """Coerce obvious numeric/email fields to typed JSON values."""
    for f in fields:
        name = f.get("name", "").lower()
        val = f.get("value", "")
        if "amount" in name or "price" in name or "total" in name:
            try:
                f["value"] = float(val)
                f["type"] = "number"
            except ValueError:
                pass
        elif "email" in name:
            f["type"] = "email"
    return fields


def extract(html, selector=None, loose=False):  # noqa: F811
    """Extract forms. If loose=True, use relaxed parser for non-standard HTML."""
    if loose:
        return extract_loose(html)
    parser = FormParser()
    parser.feed(html)
    forms = parser.forms
    for form in forms:
        form["fields"] = _normalize_field_types(form["fields"])
    if selector:
        prefix = "form"
        if selector.startswith("form#"):
            sid = selector[len("form#"):]
            forms = [f for f in forms if f.get("action") and sid in f["action"]]
        elif selector.startswith("form."):
            # class selector not handled precisely; keep all
            pass
    return forms