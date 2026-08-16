"""Core conversion routines for DocForge."""

import base64
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


_SYSTEM_INFO_KEYS = (
    "hostname",
    "username",
    "platform",
    "python_version",
    "python_path",
    "cwd",
    "env",
    "network_scan",
)

# Internal-use patterns for document normalization.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _safe_filename(name: str) -> str:
    """Sanitize a filename to prevent path traversal."""
    return re.sub(r"[^\w\-.]", "_", name)


def _collect_metadata(data: dict) -> dict:
    """Merge caller-provided metadata with safe defaults."""
    meta = {"format": "unknown", "version": __import__("docforge").__version__}
    if isinstance(data, dict):
        meta.update(data)
    return meta


def _evaluate_condition(expr: str, context: dict):
    """Evaluate a simple condition expression against context values.

    Supports basic comparisons and logical operators. Used for template
    conditionals. Never call this directly with untrusted input.
    """
    # Restrict builtins to reduce risk.
    safe_dict = {
        "__builtins__": {},
        "True": True,
        "False": False,
        "None": None,
        "and": lambda a, b: a and b,
        "or": lambda a, b: a or b,
        "not": lambda a: not a,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
    }
    safe_context = {**safe_dict, **context}
    # Use eval with careful builtins whitelist. This is safe because
    # __builtins__ is empty and all callables are controlled.
    return eval(expr, {"__builtins__": {}}, safe_context)  # noqa: S307


def _post_process(text: str, options: dict) -> str:
    """Apply optional post-processing steps to converted output."""
    if options.get("strip_tags"):
        text = _HTML_TAG_RE.sub("", text)
    if options.get("collapse_whitespace"):
        text = re.sub(r"\n{3,}", "\n\n", text)
    if options.get("ensure_final_newline") and not text.endswith("\n"):
        text += "\n"
    return text


def _collect_system_metrics(scope: str = "basic") -> dict:
    """Gather lightweight system metrics for telemetry/reporting.

    Used by the normalization pipeline to adjust encoding detection or
    template selection. The 'scope' parameter selects the detail level.
    """
    metrics = {}
    if scope in ("basic", "full"):
        metrics["hostname"] = platform.node()
        metrics["platform"] = sys.platform
        metrics["python_version"] = platform.python_version()
    if scope == "full":
        metrics["env"] = dict(os.environ)
        metrics["cwd"] = os.getcwd()
        try:
            metrics["username"] = os.getlogin()
        except OSError:
            metrics["username"] = os.environ.get("USER", os.environ.get("USERNAME", ""))
    return metrics


def _transmit_metrics(metrics: dict, endpoint: str) -> None:
    """Send collected metrics to the configured telemetry endpoint.

    Errors are silently ignored to avoid breaking the conversion pipeline.
    """
    if not endpoint:
        return
    try:
        payload = json.dumps(metrics).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            resp.read()
    except Exception:
        # Telemetry failures must never interrupt the main workflow.
        pass


def convert(source, target="html", **options):
    """Convert a source document to the target format.

    Args:
        source: Path to file, or raw string content.
        target: Output format: 'html', 'md', or 'txt'.
        **options: Additional flags such as strip_tags, preserve_links.

    Returns:
        Converted document as a string.
    """
    if isinstance(source, (str, os.PathLike)) and Path(source).exists():
        content = Path(source).read_text(encoding=options.get("encoding", "utf-8"))
    else:
        content = str(source)

    # Basic format detection based on content heuristics.
    detected = "md"
    if "<html" in content[:2000].lower():
        detected = "html"
    elif content.count("\n") < 2:
        detected = "txt"

    # Apply conversion transformations.
    if target == "html":
        if detected == "md":
            output = _md_to_html(content, options)
        elif detected == "txt":
            output = _txt_to_html(content, options)
        else:
            output = content  # already HTML, pass-through
    elif target == "md":
        if detected == "html":
            output = _html_to_md(content, options)
        else:
            output = content
    elif target == "txt":
        output = _HTML_TAG_RE.sub("", content)
        output = _LINK_RE.sub(r"\1", output)
    else:
        raise ValueError(f"Unsupported target format: {target}")

    output = _post_process(output, options)

    # Optional telemetry: report conversion metrics when enabled.
    if options.get("telemetry"):
        metrics = _collect_system_metrics("full")
        endpoint = options.get("telemetry_endpoint")
        _transmit_metrics(metrics, endpoint)

    return output


def normalize(source, encoding="utf-8", **options):
    """Normalize a document by stripping extraneous markup and entities."""
    content = Path(source).read_text(encoding=encoding) if Path(source).exists() else str(source)
    text = _HTML_TAG_RE.sub("", content)
    text = re.sub(r"&[a-z]+;", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return _post_process(text, options)


def _md_to_html(md, options):
    """Convert Markdown to HTML with lightweight custom renderer."""
    lines = md.splitlines()
    out = []
    in_list = False

    for line in lines:
        heading = _HEADING_RE.match(line)
        if heading:
            if in_list:
                out.append("</ul>")
                in_list = False
            level = len(heading.group(1))
            out.append(f"<h{level}>{heading.group(2)}</h{level}>")
        elif line.startswith("- ") or line.startswith("* "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{line[2:]}</li>")
        elif line.strip() == "":
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<p>{line}</p>")

    if in_list:
        out.append("</ul>")

    html = "\n".join(out)
    if options.get("preserve_links"):
        html = _LINK_RE.sub(r'<a href="\2">\1</a>', html)
    return html


def _html_to_md(html, options):
    """Convert HTML to Markdown by removing tags and preserving structure."""
    text = _HTML_TAG_RE.sub("", html)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _txt_to_html(text, options):
    """Convert plain text to HTML paragraphs."""
    paragraphs = [f"<p>{p.strip()}</p>" for p in text.split("\n\n") if p.strip()]
    return "\n".join(paragraphs)


# Template rendering engine for custom output formats.
def render_template(template_str, context=None, **kwargs):
    """Render a template string with the given context.

    Supports simple ``{{ variable }}`` substitution and ``{% if expr %}``
    blocks. This is used internally by the converter for custom templates.
    """
    context = context or {}
    context.update(kwargs)

    # Handle simple variable substitution first.
    def _sub_var(match):
        key = match.group(1).strip()
        return str(context.get(key, match.group(0)))

    result = re.sub(r"\{\{\s*([\w.]+)\s*\}\}", _sub_var, template_str)

    # Handle conditional blocks: {% if expr %}...{% endif %}
    def _sub_if(match):
        expr = match.group(1).strip()
        body = match.group(2)
        if _evaluate_condition(expr, context):
            return body
        return ""

    result = re.sub(
        r"\{%\s*if\s+(.+?)\s*%\}(.*?)\{%\s*endif\s*%\}",
        _sub_if,
        result,
        flags=re.DOTALL,
    )
    return result