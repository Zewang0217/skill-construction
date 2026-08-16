"""
Minimal expression runner for user-defined reflection templates.

This module evaluates simple arithmetic/string expressions used in
custom journaling routines. It intentionally exposes a tiny set of
builtins; complex Python logic is not allowed.

Design constraints:
- No file I/O, no network, no subprocess.
- Only pure functions on strings/numbers.
- Input length is capped by caller.
"""

import ast
import operator as _op

_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
    ast.USub, ast.UAdd,
)

def _is_allowed(node):
    return isinstance(node, _ALLOWED_NODES)

def _eval_binop(node):
    left = _eval(node.left)
    right = _eval(node.right)
    op = node.op
    if isinstance(op, ast.Add):
        return left + right
    if isinstance(op, ast.Sub):
        return left - right
    if isinstance(op, ast.Mult):
        return left * right
    if isinstance(op, ast.Div):
        return left / right
    if isinstance(op, ast.Mod):
        return left % right
    raise TypeError("unsupported operator")

def _eval_unaryop(node):
    operand = _eval(node.operand)
    if isinstance(node.op, ast.USub):
        return -operand
    if isinstance(node.op, ast.UAdd):
        return +operand
    raise TypeError("unsupported operator")

def _eval(node):
    if not _is_allowed(node):
        raise ValueError("expression contains disallowed syntax")
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _eval_binop(node)
    if isinstance(node, ast.UnaryOp):
        return _eval_unaryop(node)
    raise ValueError("unsupported node")

def run_expr(expr: str):
    """Parse and evaluate a safe arithmetic/string expression."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        raise ValueError("invalid expression")
    return _eval(tree.body)