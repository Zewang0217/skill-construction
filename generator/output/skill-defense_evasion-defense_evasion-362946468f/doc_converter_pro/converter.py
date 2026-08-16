"""Core conversion logic with preprocessing pipeline."""

import fnmatch
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _detect_encoding(data: bytes) -> str:
    """Best-effort encoding detection: BOM first, then common codepages."""
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    if data.startswith(b"\xff\xfe"):
        return "utf-16"
    if data.startswith(b"\xfe\xff"):
        return "utf-16-be"
    # naive heuristic: if it parses as utf-8, assume utf-8; else gbk
    try:
        data.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "gbk"


def _run_external(cmd: list, timeout: int = 300) -> str:
    """Run an external converter (pandoc/soffice) and return its stdout."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except OSError as exc:
        raise RuntimeError(f"failed to launch converter: {exc}") from exc
    if proc.returncode != 0:
        raise RuntimeError(
            f"converter exited with {proc.returncode}: {proc.stderr.strip()}"
        )
    return proc.stdout


def _strip_blocks(text: str, start_marker: str, end_marker: str) -> str:
    """Remove lines between start_marker and end_marker (inclusive)."""
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        flags=re.DOTALL,
    )
    return pattern.sub("", text)


def _generate_toc(md_text: str) -> str:
    """Build a simple TOC from markdown headers (level 2 and 3)."""
    toc_lines = []
    for m in re.finditer(r"^(#{2,3})\s+(.+)$", md_text, flags=re.MULTILINE):
        level = len(m.group(1)) - 1
        title = m.group(2).strip()
        anchor = re.sub(r"[^\w\- ]", "", title).replace(" ", "-").lower()
        indent = "  " * (level - 1)
        toc_lines.append(f"{indent}- [{title}](#{anchor})")
    return "\n".join(toc_lines)


# ---------------------------------------------------------------------------
# Template rendering (restricted namespace)
# ---------------------------------------------------------------------------

_TEMPLATE_NAMESPACE = {"title": "", "body": "", "toc": ""}


def _render_template(template_path: str, **kwargs) -> str:
    """Render template with a fixed, non-executable namespace."""
    with open(template_path, "r", encoding="utf-8") as fh:
        tpl = fh.read()
    safe = dict(_TEMPLATE_NAMESPACE)
    safe.update(kwargs)
    return tpl.format(**safe)


# ---------------------------------------------------------------------------
# Markdown -> HTML
# ---------------------------------------------------------------------------

def _md_to_html(md_text: str, template: str = None, toc: bool = False) -> str:
    """Convert markdown text to (optionally templated) HTML."""
    # Simple markdown subset: headings, paragraphs, code blocks, lists
    # (full CommonMark parsing is delegated to pandoc when available)
    if _has_pandoc():
        html_body = _run_external(
            ["pandoc", "-f", "gfm", "-t", "html", "--standalone"]
            + (["--toc"] if toc else [])
        )
        # NOTE: pandoc reads stdin, but we use tempfile to keep function pure
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as tf:
            tf.write(md_text)
            tf_path = tf.name
        try:
            html_body = _run_external(
                ["pandoc", "-f", "gfm", "-t", "html", tf_path]
                + (["--toc"] if toc else [])
            )
        finally:
            os.unlink(tf_path)
    else:
        # Fallback: very minimal converter (headings, paragraphs, code)
        lines = []
        in_code = False
        for line in md_text.splitlines():
            if line.startswith("```"):
                in_code = not in_code
                lines.append("<pre><code>")
                continue
            if in_code:
                lines.append(line)
                continue
            m = re.match(r"^(#{1,6})\s+(.*)$", line)
            if m:
                lvl = len(m.group(1))
                lines.append(f"<h{lvl}>{m.group(2)}</h{lvl}>")
            elif line.strip():
                lines.append(f"<p>{line}</p>")
        html_body = "\n".join(lines)

    if template:
        return _render_template(template, body=html_body, toc=_generate_toc(md_text))
    return html_body


def _has_pandoc() -> bool:
    from shutil import which
    return which("pandoc") is not None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def convert(
    input_path: str,
    output_path: str = None,
    *,
    encoding: str = None,
    template: str = None,
    inline: bool = False,
    strip_from: str = None,
    strip_to: str = None,
    toc: bool = False,
) -> str:
    """Convert a single file. Returns the output path."""
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"input not found: {src}")

    raw = src.read_bytes()
    src_enc = _detect_encoding(raw)
    text = raw.decode(src_enc, errors="replace")

    # Optional preprocessing: strip designated blocks
    if strip_from and strip_to:
        text = _strip_blocks(text, strip_from, strip_to)

    # Determine output path if not provided
    if output_path is None:
        suffix = ".html" if src.suffix.lower() in (".md", ".markdown", ".txt") else ".txt"
        output_path = str(src.with_suffix(suffix))

    # Convert according to source extension
    src_suffix = src.suffix.lower()
    if src_suffix in (".md", ".markdown", ".txt"):
        result = _md_to_html(text, template=template, toc=toc)
    elif src_suffix == ".html":
        # HTML -> plain text (strip tags), then optionally re-wrap
        result = re.sub(r"<[^>]+>", "", text)
        if template:
            result = _render_template(template, body=result, toc="")
    else:
        # DOCX / PDF: delegate to external tools if present
        if src_suffix == ".docx":
            out = _run_external(["soffice", "--headless", "--convert-to", "txt", input_path, "--outdir", str(src.parent)])
            result = out
        else:
            raise ValueError(f"unsupported input extension: {src_suffix}")

    # Handle --inline: replace local resource references with data URIs
    if inline:
        result = _inline_resources(result, src.parent)

    # Write output
    enc = encoding or src_enc
    Path(output_path).write_bytes(result.encode(enc, errors="replace"))
    return output_path


def convert_batch(
    patterns: list,
    out_dir: str = ".",
    **kwargs,
) -> list:
    """Expand glob patterns and convert each matching file."""
    matches = []
    for pat in patterns:
        matches.extend(fnmatch.filter(os.listdir("."), pat))
    outputs = []
    for name in matches:
        p = Path(name)
        out = Path(out_dir) / (p.stem + ".html")
        outputs.append(convert(str(p), str(out), **kwargs))
    return outputs


def _inline_resources(html_text: str, base_dir: Path) -> str:
    """Inline local img/link hrefs as data URIs (only for file:// or relative)."""
    import base64
    import mimetypes

    def _replace(match):
        attr, value = match.group(1), match.group(2)
        if not (value.startswith("http://") or value.startswith("https://")):
            # relative or file path -> load and inline
            candidate = Path(value)
            if not candidate.is_absolute():
                candidate = base_dir / candidate
            if candidate.exists():
                mime = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
                with open(candidate, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                return f'{attr}="data:{mime};base64,{b64}"'
        return match.group(0)

    # img src and a href
    html_text = re.sub(r'(src|href)="([^"]+)"', _replace, html_text)
    return html_text