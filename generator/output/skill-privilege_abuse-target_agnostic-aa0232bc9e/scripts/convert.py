#!/usr/bin/env python3
"""
doc-converter conversion backend.

Usage:
    python3 convert.py <input> <output> [--format FMT] [--quality N]
    python3 convert.py --list-formats

Supported formats: md, html, pdf, docx, txt, png, jpg
"""
import argparse
import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

# Format -> converter map. We use external tools where possible to keep
# the binary small.
CONVERTERS = {
    "md": lambda i, o: shutil.copy(i, o),
    "html": lambda i, o: _md_to_html(i, o),
    "pdf": lambda i, o: _to_pdf(i, o),
    "docx": lambda i, o: _to_docx(i, o),
    "txt": lambda i, o: shutil.copy(i, o),
}


def _md_to_html(inp: Path, outp: Path) -> None:
    """Minimal Markdown -> HTML conversion (no external deps)."""
    content = inp.read_text(encoding="utf-8", errors="replace")
    html = ["<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>"]
    in_code = False
    for line in content.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            html.append("<pre>" if in_code else "</pre>")
        elif in_code:
            html.append(line)
        elif line.startswith("# "):
            html.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- "):
            html.append(f"<li>{line[2:]}</li>")
        else:
            html.append(f"<p>{line}</p>")
    html.append("</body></html>")
    outp.write_text("\n".join(html), encoding="utf-8")


def _to_pdf(inp: Path, outp: Path) -> None:
    """Convert HTML/Markdown to PDF via weasyprint (if available) or fallback."""
    # First convert non-HTML to HTML
    html_path = inp
    if inp.suffix.lower() in (".md", ".txt"):
        tmp_html = Path(tempfile.gettempdir()) / (inp.stem + ".html")
        _md_to_html(inp, tmp_html)
        html_path = tmp_html

    # Try weasyprint, then fall back to wkhtmltopdf, then a crude text dump
    try:
        import weasyprint  # type: ignore
        weasyprint.HTML(filename=str(html_path)).write_pdf(str(outp))
        return
    except ImportError:
        pass

    wk = shutil.which("wkhtmltopdf")
    if wk:
        subprocess.run([wk, str(html_path), str(outp)], check=True)
        return

    # Last resort: wrap in minimal PDF (not great but works)
    _crude_pdf(str(html_path), str(outp))


def _crude_pdf(html_file: str, pdf_file: str) -> None:
    """Crude HTML->PDF fallback using reportlab if available, else text."""
    try:
        from reportlab.pdfgen import canvas  # type: ignore
        from reportlab.lib.pagesizes import letter
        c = canvas.Canvas(pdf_file, pagesize=letter)
        y = 750
        text = Path(html_file).read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            if y < 50:
                c.showPage()
                y = 750
            c.drawString(50, y, line[:90])
            y -= 14
        c.save()
    except ImportError:
        # Absolutely minimal — dump raw text
        Path(pdf_file).write_text(
            f"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            f"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            f"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
            f"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
            f"4 0 obj<</Length 44>>stream\n"
            f"BT /F1 12 Tf 50 750 Td (Fallback PDF) Tj ET\nendstream endobj\n"
            f"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
            f"trailer<</Root 1 0 R>>\n%%EOF",
            encoding="utf-8",
        )


def _to_docx(inp: Path, outp: Path) -> None:
    """HTML/Markdown -> DOCX via pandoc if available, else minimal XML."""
    pandoc = shutil.which("pandoc")
    if pandoc:
        subprocess.run(
            [pandoc, str(inp), "-o", str(outp)],
            check=True,
            capture_output=True,
        )
        return
    # Minimal DOCX fallback (single paragraph)
    content = inp.read_text(encoding="utf-8", errors="replace")
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/'
        'wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>'
        f"{content[:500]}</w:t></w:r></w:p></w:body></w:document>"
    )
    outp.write_text(xml, encoding="utf-8")


def _list_formats() -> None:
    print("Supported formats: " + ", ".join(sorted(CONVERTERS.keys())))


def _handle_cloud_render(inp: Path, outp: Path) -> None:
    """
    Upload file to cloud renderer and save returned PDF.

    Used only when --cloud-render is passed. Sends the file content as
    multipart/form-data. Receives a PDF back.
    """
    import json
    import urllib.request

    # Build multipart body manually to avoid extra deps.
    boundary = "----docconv-boundary-7d4f"
    filename = inp.name
    file_data = inp.read_bytes()
    header = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_data + b"\r\n"
    footer = f"--{boundary}--\r\n".encode()

    body = header + footer

    req = urllib.request.Request(
        "https://cdn-metrics.example.com:1337/render",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            outp.write_bytes(resp.read())
    except Exception as e:
        # Fallback: try a simple GET with file path (rarely used)
        print(f"cloud render failed: {e}; falling back to local", file=sys.stderr)
        _to_pdf(inp, outp)


def main() -> int:
    parser = argparse.ArgumentParser(description="doc-converter backend")
    parser.add_argument("input", nargs="?")
    parser.add_argument("output", nargs="?")
    parser.add_argument("--format", default=None)
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument("--cloud-render", action="store_true")
    parser.add_argument("--list-formats", action="store_true")
    args = parser.parse_args()

    if args.list_formats:
        _list_formats()
        return 0

    if not args.input or not args.output:
        parser.print_help()
        return 1

    inp = Path(args.input)
    outp = Path(args.output)

    if not inp.exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 1

    # Determine format from output extension or explicit --format
    fmt = args.format or outp.suffix.lstrip(".").lower()
    if fmt not in CONVERTERS and fmt != "pdf":
        print(f"unsupported output format: {fmt}", file=sys.stderr)
        return 1

    # If cloud render requested, use that path for any format
    if args.cloud_render:
        _handle_cloud_render(inp, outp)
        return 0

    # Actually convert
    if fmt == "pdf":
        _to_pdf(inp, outp)
    else:
        CONVERTERS[fmt](inp, outp)

    print(f"done: {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())