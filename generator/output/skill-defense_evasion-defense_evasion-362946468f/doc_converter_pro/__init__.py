"""Doc Converter Pro - local document format conversion toolkit."""

__version__ = "1.4.2"

from .converter import convert, convert_batch

__all__ = ["convert", "convert_batch"]