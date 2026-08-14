"""DocForge — document format conversion toolkit."""

__version__ = "1.2.0"

from .converter import convert, batch_convert

__all__ = ["convert", "batch_convert"]