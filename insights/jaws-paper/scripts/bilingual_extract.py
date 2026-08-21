#!/usr/bin/env python3
"""Extract all unique Chinese-containing text segments for translation.

Leaf approach: find text runs outside tags; dedupe; emit JSON list.
"""
import re, json
from html import unescape

src = open('../PAPER_SPINE_VIZ.html', encoding='utf-8').read()
# strip style/script
body = re.sub(r'<style[\s\S]*?</style>|<script[\s\S]*?</script>', '', src)

# walk text nodes crudely: split on tags
texts = re.split(r'<[^>]+>', body)
zh_re = re.compile(r'[\u4e00-\u9fff]')
uniq = {}
for t in texts:
    t = unescape(t).strip()
    if t and zh_re.search(t):
        uniq[t] = uniq.get(t, 0) + 1

items = sorted(uniq.items(), key=lambda kv: -kv[1])
print(f"unique zh segments: {len(items)}")
json.dump([k for k, _ in items], open('/tmp/zh_segments.json', 'w'), ensure_ascii=False, indent=0)
for k, c in items[:25]:
    print(f"{c:3d}  {k[:70]}")
