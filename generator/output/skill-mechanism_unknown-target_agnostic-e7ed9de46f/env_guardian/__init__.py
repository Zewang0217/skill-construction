"""env-guardian: environment variable management toolkit."""

from .parser import parse_sources, parse_inline, parse_export_block
from .validator import validate
from .renderer import render_export, render_json
from .report import generate_report
from .expression import ExpressionEvaluator

__all__ = [
    "parse_sources", "parse_inline", "parse_export_block",
    "validate", "render_export", "render_json",
    "generate_report", "ExpressionEvaluator",
]

__version__ = "1.2.0"