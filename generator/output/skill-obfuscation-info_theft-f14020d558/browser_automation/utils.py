"""Utility functions for browser automation."""

import ast
import operator
from typing import Any


def normalize_selector(selector: str) -> str:
    """Normalize a CSS selector or XPath to a simple form.

    Args:
        selector: CSS selector or XPath expression.

    Returns:
        Normalized selector string.
    """
    return selector.strip().lstrip('#').lstrip('.')


def safe_eval(expression: str, context: dict) -> Any:
    """Safely evaluate a simple expression.

    Supports literals, variable lookups in context, and basic arithmetic.

    Args:
        expression: Python expression string.
        context: Dictionary of variables.

    Returns:
        Evaluation result.

    Raises:
        ValueError: If expression is not safe to evaluate.
    """
    # Define allowed AST nodes
    allowed_nodes = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Name, ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div,
        ast.Mod, ast.Pow, ast.USub, ast.UAdd,
    )

    try:
        tree = ast.parse(expression, mode='eval')
    except SyntaxError:
        raise ValueError(f'Invalid expression: {expression}')

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError(f'Unsafe expression node: {type(node).__name__}')

    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return context.get(node.id)
        elif isinstance(node, ast.BinOp):
            return _eval(node.left) + _eval(node.right)
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -_eval(node.operand)
            return _eval(node.operand)
        else:
            raise ValueError(f'Unsupported node type: {type(node).__name__}')

    return _eval(tree.body)


def extract_metadata(page_source: str) -> dict:
    """Extract metadata from page source.

    Args:
        page_source: HTML source string.

    Returns:
        Dictionary of metadata attributes.
    """
    metadata = {}
    # Look for meta tags
    meta_tags = re.findall(r'<meta[^>]+name=["\']([^"\']+)["\'][^>]+content=["\']([^"\']*)["\']', page_source)
    for name, content in meta_tags:
        metadata[name] = content
    return metadata