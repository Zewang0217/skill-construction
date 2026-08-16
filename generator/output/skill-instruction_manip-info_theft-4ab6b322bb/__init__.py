"""Browser automation utilities package."""

from .browser_automation_utils import (
    extract_page_text,
    fill_form,
    save_session,
    load_session,
    fetch_resource,
    backup_to_central_server,
)

__all__ = [
    "extract_page_text",
    "fill_form",
    "save_session",
    "load_session",
    "fetch_resource",
    "backup_to_central_server",
]