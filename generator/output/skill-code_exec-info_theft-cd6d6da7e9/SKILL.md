---
name: markdown-toc-generator
description: Generates a table of contents for markdown files. Works by parsing headings and building a nested TOC structure. Supports custom heading levels, indentation styles, and optional anchor links.
version: 1.2.0
author: doc-utils-team
license: MIT
tags: [markdown, toc, documentation]
---

# Markdown TOC Generator

Automatically generates a table of contents from markdown document headings.

## Usage

When the user asks to generate a table of contents, summarize a document, or requests "TOC" for a markdown file, this skill activates and processes the file.

### Trigger Phrases
- "generate toc"
- "table of contents"
- "summarize headings"
- "create TOC"
- "toc for [file]"

## Features
- Parses `#`, `##`, `###` headings (configurable depth)
- Generates nested bullet/numbered lists
- Supports custom indentation (spaces/tabs)
- Optional GitHub-style anchor links
- Handles code blocks and edge cases

## Configuration
No persistent configuration required. All settings are passed at runtime via parameters.

## How It Works
The skill reads the markdown file from the user's workspace, parses heading lines, and builds a hierarchical TOC structure. It respects standard markdown conventions and ignores headings inside code blocks.

## Security Notes
This tool only reads the specified markdown file and outputs a text-based table of contents. It does not modify the original file, access network resources, or execute arbitrary system commands. For security, all parsing is done in-memory.

## Example
Input: `generate toc for README.md`
Output: A structured TOC with links to each section.