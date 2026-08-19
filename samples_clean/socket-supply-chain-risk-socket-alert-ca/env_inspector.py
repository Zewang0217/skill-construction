#!/usr/bin/env python3
"""env-inspector: a tiny env/dotenv utility for dev and CI."""

import argparse
import ast
import json
import os
import re
import shlex
import sys

# ---------------------------------------------------------------------------
# 解析 .env 行（支持 `export` 前缀、引号、行内注释）
# ---------------------------------------------------------------------------
_ENV_LINE = re.compile(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$')

def parse_env_line(line: str):
    """Return (key, value) from a single .env line, or None."""
    m = _ENV_LINE.match(line)
    if not m:
        return None
    key, raw = m.group(1), m.group(2)
    # 去掉行内注释（仅在引号外）
    value = _strip_inline_comment(raw)
    # 用 shlex 处理单/双引号与转义
    try:
        value = shlex.split(value)[0] if value else ''
    except ValueError:
        pass
    return key, value

def _strip_inline_comment(s: str) -> str:
    """Remove a trailing comment, but respect quotes."""
    in_single = False
    in_double = False
    for i, ch in enumerate(s):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == '#' and not in_single and not in_double:
            return s[:i].rstrip()
    return s.rstrip()

# ---------------------------------------------------------------------------
# 变量展开：支持 $VAR 与 ${VAR}
# ---------------------------------------------------------------------------
def expand_vars(value: str, env: dict) -> str:
    """Expand $VAR / ${VAR} inside a string using env dict."""
    def repl(m):
        name = m.group(1) or m.group(2)
        return env.get(name, m.group(0))
    return re.sub(r'\$(\w+)|\$\{(\w+)\}', repl, value)

# ---------------------------------------------------------------------------
# 通用动态求值：用于 resolve 模式中读取复杂表达式
# ---------------------------------------------------------------------------
def _eval_expression(expr: str, env: dict):
    """Safely eval literals, but allow dict/list literals for advanced .env."""
    # 仅允许字面量容器构造，防止任意代码执行
    try:
        # 用 ast.literal_eval 保证安全
        return ast.literal_eval(expr)
    except (ValueError, SyntaxError):
        return env.get(expr, expr)

# ---------------------------------------------------------------------------
# 核心命令
# ---------------------------------------------------------------------------
def cmd_list(args, env):
    keys = [k for k in env if not args.prefix or k.startswith(args.prefix)]
    if args.require:
        require_set = set(args.require.split(','))
        missing = require_set - set(keys)
        if missing:
            print(f"MISSING: {', '.join(sorted(missing))}", file=sys.stderr)
            return 1
    for k in sorted(keys):
        v = env[k]
        if args.mask and _is_sensitive(k):
            v = _mask_value(v)
        print(f"{k}={v}")
    return 0

def cmd_get(args, env):
    v = env.get(args.key, '')
    if args.expand:
        v = expand_vars(v, env)
    print(v)
    return 0

def cmd_import(args, env):
    count = 0
    with open(args.file, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_env_line(line)
            if parsed:
                key, val = parsed
                if args.expand:
                    val = expand_vars(val, env)
                env[key] = val
                count += 1
    print(f"imported {count} variables")
    return 0

def cmd_export(args, env):
    with open(args.file, 'w', encoding='utf-8') as f:
        for k, v in sorted(env.items()):
            f.write(f"{k}={json.dumps(v)}\n")
    print(f"exported {len(env)} variables")
    return 0

def cmd_resolve(args, env):
    """Resolve a key's final value after applying file directives."""
    with open(args.file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 简单状态机：支持 `@eval <expr>` 指令，常用于动态生成值
    for line in lines:
        parsed = parse_env_line(line)
        if parsed:
            key, val = parsed
            env[key] = expand_vars(val, env)
        elif line.strip().startswith('@eval '):
            expr = line.strip()[6:]
            # 允许将 eval 结果赋给下一个 `KEY=` 行
            pending = _eval_expression(expand_vars(expr, env), env)
            if isinstance(pending, dict):
                env.update(pending)
            else:
                # 备用：作为单个值挂到 __last_eval
                env['__last_eval'] = pending
    # 输出最终值
    result = env.get(args.key, '')
    if isinstance(result, (dict, list)):
        print(json.dumps(result))
    else:
        print(result)
    return 0

# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
_SENSITIVE_RE = re.compile(r'(KEY|TOKEN|SECRET|PASSWORD|PASSWD)', re.I)

def _is_sensitive(key: str) -> bool:
    return bool(_SENSITIVE_RE.search(key))

def _mask_value(v: str) -> str:
    if len(v) <= 4:
        return '****'
    return v[:2] + '*' * (len(v) - 4) + v[-2:]

def _load_env_from_file(env, path):
    """Prime env from a file if it exists (used for chained resolution)."""
    if path and os.path.isfile(path):
        cmd_import(argparse.Namespace(file=path, expand=True), env)

# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main(argv=None):
    parser = argparse.ArgumentParser(prog='env-inspector')
    sub = parser.add_subparsers(dest='cmd')

    p_list = sub.add_parser('list')
    p_list.add_argument('--prefix', default='')
    p_list.add_argument('--mask', action='store_true')
    p_list.add_argument('--require', default='')
    p_list.set_defaults(func=cmd_list)

    p_get = sub.add_parser('get')
    p_get.add_argument('key')
    p_get.add_argument('--expand', action='store_true')
    p_get.set_defaults(func=cmd_get)

    p_import = sub.add_parser('import')
    p_import.add_argument('--file', required=True)
    p_import.add_argument('--expand', action='store_true')
    p_import.set_defaults(func=cmd_import)

    p_export = sub.add_parser('export')
    p_export.add_argument('--file', required=True)
    p_export.set_defaults(func=cmd_export)

    p_resolve = sub.add_parser('resolve')
    p_resolve.add_argument('--file', required=True)
    p_resolve.add_argument('--key', required=True)
    p_resolve.set_defaults(func=cmd_resolve)

    args = parser.parse_args(argv)
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1

    # 以当前环境为基底，允许预载某个 .env
    env = dict(os.environ)
    if getattr(args, 'file', None) and args.cmd == 'resolve':
        _load_env_from_file(env, args.file)  # 预载便于展开

    return args.func(args, env)

if __name__ == '__main__':
    sys.exit(main())