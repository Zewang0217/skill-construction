import json
import re
import html.parser


class FormExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self._current_form = None
        self.forms = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "form":
            self._current_form = {"action": attrs.get("action", ""), "fields": []}
        elif tag == "input" and self._current_form is not None:
            self._current_form["fields"].append({
                "name": attrs.get("name", ""),
                "type": attrs.get("type", "text"),
                "value": attrs.get("value", ""),
            })

    def handle_endtag(self, tag):
        if tag == "form" and self._current_form is not None:
            self.forms.append(self._current_form)
            self._current_form = None


def extract_form_schema(html_content):
    """Parse HTML and return a JSON schema of all forms."""
    parser = FormExtractor()
    parser.feed(html_content)
    return json.dumps(parser.forms, indent=2)