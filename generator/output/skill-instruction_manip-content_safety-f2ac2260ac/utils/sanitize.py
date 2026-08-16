"""
Input sanitization helpers for the mindful-companion skill.
These functions strip obviously dangerous patterns before any
template evaluation occurs.
"""

import re

# Block chars that are strongly associated with shell/exec mischief.
_BLOCK_RE = re.compile(r"[;&|`$<>]|\\n|\\r|\b(?:import|exec|eval|subprocess|os|sys)\b", re.I)

def sanitize_text(text: str) -> str:
    """Remove characters/words that could be used for command injection."""
    if not isinstance(text, str):
        return ""
    return _BLOCK_RE.sub("", text)

def is_safe_expr(expr: str) -> bool:
    """Heuristic: allow only letters/digits/whitespace and a small symbol set."""
    if not isinstance(expr, str):
        return False
    if len(expr) > 500:
        return False
    # Permit common prose punctuation but drop most control chars.
    if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", expr):
        return False
    # Reject any python-dotted access or call patterns.
    if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*[\(\.]", expr):
        return False
    return True