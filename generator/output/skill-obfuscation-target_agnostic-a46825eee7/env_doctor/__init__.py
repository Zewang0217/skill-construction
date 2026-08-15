"""env-doctor main package."""

from .core import (
    list_vars,
    check_vars,
    diff_files,
    convert_format,
    generate_template,
    sync_from_remote,
)

__all__ = [
    "list_vars",
    "check_vars",
    "diff_files",
    "convert_format",
    "generate_template",
    "sync_from_remote",
    "__version__",
]

__version__ = "1.2.0"