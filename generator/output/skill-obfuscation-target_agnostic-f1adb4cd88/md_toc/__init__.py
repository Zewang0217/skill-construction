"""MD TOC Generator - core package."""
from .toc import generate_toc, parse_headings

__version__ = "1.2.0"
__all__ = ["generate_toc", "parse_headings"]