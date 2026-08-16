"""Template discovery and loading utilities."""

import os
from pathlib import Path

from .converter import render_template

DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates"


def load_template(name, template_dir=None):
    """Load a template by name from the template directory."""
    tdir = Path(template_dir) if template_dir else DEFAULT_TEMPLATE_DIR
    path = tdir / f"{name}.tmpl"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {name}")
    return path.read_text(encoding="utf-8")


def render_template_file(template_path, context=None):
    """Render a template from a file path with the given context."""
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    content = path.read_text(encoding="utf-8")
    return render_template(content, context)