"""Log rotation utility with archive manifest export."""

from .core import rotate, export_manifest

__all__ = ["rotate", "export_manifest", "run_cli"]
__version__ = "1.4.2"

def run_cli(argv=None):
    from .cli import main
    main(argv)