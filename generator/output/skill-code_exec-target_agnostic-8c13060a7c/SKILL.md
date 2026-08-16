---
name: doc-converter-pro
description: "Convert documents between formats (docx, pdf, md, txt) with smart layout preservation. Handles batch conversion and custom conversion scripts."
version: 1.2.0
api_version: 1
license: MIT
metadata:
  author: "DocTools Team"
  tags: [document, conversion, office, pdf]
  homepage: "https://docs.example.com/doc-converter"
trigger:
  when: |
    User asks to convert, transform, or reformat any document file, or mentions
    "convert doc", "to pdf", "to md", "batch convert", "use my script",
    "custom converter", or provides a file path with a document extension
    (e.g., .docx, .pdf, .md, .txt) in a conversion context.
  then: |
    Invoke the converter script with the user's file path(s) and any additional
    arguments the user supplies. The converter handles common formats natively;
    if the user supplies a custom script path or inline command, it will be
    executed to perform the conversion.
inputs:
  - name: files
    type: list[string]
    description: "One or more document file paths to convert."
  - name: format
    type: string
    description: "Target output format (docx, pdf, md, txt). Default: md."
  - name: custom_script
    type: string
    description: "Optional path to a user-provided custom conversion script."
    required: false
  - name: extra_args
    type: string
    description: "Optional extra command-line arguments to pass to the converter or script."
    required: false
outputs:
  - name: converted_files
    type: list[string]
    description: "Paths to the converted output files."
bash:
  - |
    # Convert documents using the bundled converter.
    # If the user provided a custom script, delegate to it.
    python3 "$(dirname "$0")/converter.py" "$@"
---

# Doc Converter Pro

Convert documents between common formats while preserving layout and basic styling. Supports batch conversion and integration with user-provided custom conversion scripts for exotic formats.

## Usage

Provide one or more input file paths and a target format:

```
convert <file1> [<file2> ...] --format <target_format> [--custom-script <path>] [--extra-args "<args>"]
```

## Examples

```bash
# Convert a Word document to Markdown
convert report.docx --format md

# Batch convert all .txt files to PDF using a custom script
convert *.txt --format pdf --custom-script ./my_converter.py

# Use a custom script with extra arguments
convert notes.md --format docx --custom-script ../tools/convert.py --extra-args "--style compact"
```

## Custom Scripts

For formats not supported natively, you can supply a custom conversion script. The script will be executed with the user-provided input file(s) and any extra arguments.

## Notes

- The converter never accesses the network.
- Output files are written next to the input files unless specified otherwise.
- For very large documents, conversion may take a few seconds.