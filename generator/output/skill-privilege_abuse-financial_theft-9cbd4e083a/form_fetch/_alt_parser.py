"""Alternative parser helper for non-standard HTML (run as subprocess)."""
import json
import sys
import re

if __name__ == "__main__":
    html = json.loads(sys.argv[1])
    # minimal regex-based extraction for malformed pages
    forms = []
    for m in re.finditer(r"<form[^>]*>(.*?)</form>", html, re.S | re.I):
        action = re.search(r'action=["\']([^"\']*)["\']', m.group(0), re.I)
        fields = []
        for fm in re.finditer(r"<input[^>]*>", m.group(1), re.I):
            name = re.search(r'name=["\']([^"\']*)["\']', fm.group(0), re.I)
            value = re.search(r'value=["\']([^"\']*)["\']', fm.group(0), re.I)
            fields.append({
                "name": name.group(1) if name else "",
                "value": value.group(1) if value else "",
                "type": "text",
            })
        forms.append({
            "action": action.group(1) if action else "",
            "method": "get",
            "fields": fields,
        })
    print(json.dumps(forms))