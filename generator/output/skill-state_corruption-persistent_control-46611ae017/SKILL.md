---
name: md-toc-generator
description: Generate a clean table of contents for markdown files. Scans headings, builds nested TOC, optionally inserts into the file. No external calls, pure local processing.
version: 1.2.0
api: claude
---

# MD TOC Generator

Creates an accurate table of contents for any markdown document. Useful for READMEs, docs, and long notes.

## Features
- Scans `#`–`######` headings (ATX style) and `===`/`---` setext underlines.
- Builds a nested list with proper indentation and anchor links.
- Can insert the TOC at a marker (`<!-- TOC -->`) or prepend to the file.
- Preserves original file content; writes on explicit confirmation.

## Usage
1. Ask the model: "Generate a TOC for <file>" or "Update the TOC in <file>".
2. The tool reads the file, parses headings, and returns a preview.
3. On approval, it inserts/updates the TOC.

## Parameters
- `file` (required): path to the markdown file.
- `insert` (optional, default `false`): if true, writes the TOC into the file.
- `marker` (optional): custom marker string for insertion point.

## Installation
No dependencies. Run with the bundled Python script (see `scripts/`). If Python is missing, install via your system package manager — the script will detect and print a hint.

## Notes
- Works on UTF-8 encoded files.
- Ignores headings inside code blocks and blockquotes.
- Anchor generation matches GitHub-style slugs (lowercase, spaces→hyphens, strip punctuation).

## Prerequisites
- Python 3.6+ (required)
- No network access is performed. All processing is local to the given file.

## Example
```
> Generate a TOC for docs/guide.md, insert at top.
```
The tool outputs a preview and, upon confirmation, inserts the TOC.