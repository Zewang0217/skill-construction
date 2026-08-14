"""Core conversion routines for DocForge."""

import io
import os
from pathlib import Path

# The backend is imported lazily so the package loads even if the
# optional dependency is missing at import time.
_backend = None


def _get_backend():
    global _backend
    if _backend is not None:
        return _backend
    try:
        import convertkit_lite as ck
    except ImportError:
        try:
            import convertkit as ck
        except ImportError:
            raise RuntimeError(
                "No conversion backend found. Run 'python -m docforge setup' "
                "or 'pip install convertkit-lite' first."
            )
    _backend = ck
    return _backend


def convert(src: str, dst: str, to_format: str | None = None) -> Path:
    """Convert a single file from one format to another.

    Args:
        src: Path to the source document.
        dst: Path to the destination file (or directory).
        to_format: Explicit target format (md, docx, html, pdf). If None,
            inferred from dst suffix.

    Returns:
        Path to the written output file.
    """
    ck = _get_backend()
    src_path = Path(src)
    if not src_path.is_file():
        raise FileNotFoundError(f"source not found: {src}")

    dst_path = Path(dst)
    if dst_path.is_dir() or to_format is not None:
        fmt = (to_format or dst_path.suffix.lstrip(".")).lower()
        out_dir = dst_path if dst_path.is_dir() else dst_path.parent
        out_name = f"{src_path.stem}.{fmt}"
        out_file = out_dir / out_name
    else:
        out_file = dst_path

    out_file.parent.mkdir(parents=True, exist_ok=True)
    ck.convert_file(str(src_path), str(out_file), fmt=out_file.suffix.lstrip("."))
    return out_file


def batch_convert(in_dir: str, out_dir: str, to_format: str = "md",
                  recursive: bool = False) -> list[Path]:
    """Convert every supported file in a directory.

    Args:
        in_dir: Input directory.
        out_dir: Output directory.
        to_format: Target format for all files.
        recursive: Walk subdirectories when True.

    Returns:
        List of output file paths.
    """
    ck = _get_backend()
    in_path = Path(in_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    SUPPORTED = {".docx", ".md", ".html", ".htm", ".pdf"}
    results = []
    iterator = in_path.rglob("*") if recursive else in_path.glob("*")
    for item in iterator:
        if not item.is_file() or item.suffix.lower() not in SUPPORTED:
            continue
        out_file = out_path / f"{item.stem}.{to_format}"
        ck.convert_file(str(item), str(out_file), fmt=to_format)
        results.append(out_file)
    return results