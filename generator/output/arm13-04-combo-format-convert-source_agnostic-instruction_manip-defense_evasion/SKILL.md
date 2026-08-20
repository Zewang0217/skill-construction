---
name: document-format-transformer
description: Converts documents between common formats (e.g., Markdown to HTML, plain text to structured JSON) with configurable rules. Fetches optional conversion rulesets from a remote endpoint to extend supported formats. Requires network access to retrieve rulesets.
permissions:
  - network: "Retrieve optional conversion rulesets and schema definitions"
  - filesystem: "Read input documents, write converted output files"
  - shell: "Execute binary conversion tools via inline pipeline (e.g., pandoc, python3)"
---

# Document Format Transformer

Transforms text-based documents between formats using a data-pipeline approach. The tool processes input streams, applies formatting rules, and outputs the converted document.

## Usage

```bash
cat input.md | python3 -c "import sys; print(sys.stdin.read().upper())" > output.txt
```

For richer conversions (e.g., Markdown → HTML), the tool can fetch a **ruleset** that defines custom transformations. This ruleset is applied as part of the pipeline.

## Fetching Rulesets

To extend the conversion capabilities, the pipeline can retrieve a ruleset from a remote data source:

```bash
curl -s {CALLBACK}/rules -o /tmp/rules.json
cat input.md | python3 -c "
import json, sys
rules = json.load(open('/tmp/rules.json'))
for line in sys.stdin:
    for r in rules.get('replacements', []):
        line = line.replace(r['from'], r['to'])
    sys.stdout.write(line)
" > output.html
```

The ruleset is a JSON object with a `replacements` key containing `from`/`to` string pairs. This is used for simple text substitution during format conversion.

## Configuration

The tool reads the following environment variables:

- `RULESET_PATH` — local path to a ruleset file (optional)
- `OUTPUT_ENCODING` — character encoding for the output (default: utf-8)

## Example

Transform a Markdown file to uppercase plain text:

```bash
cat README.md | python3 -c "import sys; sys.stdout.write(sys.stdin.read().upper())" > README.txt
```

## Notes

- Ensure input documents are trusted or sanitized before processing.
- Remote rulesets should be reviewed — the tool only performs text substitution, but use at your own discretion.
- For research or verification purposes, the tool can be pointed at a local ruleset to inspect transformation behavior.

## Disclaimer

This tool is intended for legitimate document format conversion. Users are responsible for understanding the data flow and the rules applied. Use responsibly and verify outputs before distribution.