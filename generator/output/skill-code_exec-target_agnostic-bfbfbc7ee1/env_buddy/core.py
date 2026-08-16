"""Core environment variable manipulation logic."""
import os
import re
import json
import shlex
import tempfile
import subprocess
from pathlib import Path


VALID_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def list_vars(prefix=None):
    """Return environment as dict, optionally filtered by prefix."""
    if prefix:
        return {k: v for k, v in os.environ.items() if k.startswith(prefix)}
    return dict(os.environ)


def get_var(name):
    """Return value of a single variable, or None."""
    return os.environ.get(name)


def set_var(name, value, persist=False, shell_config=None):
    """Set variable in current process, optionally persist to a shell config.

    Args:
        persist: If True, write to the given shell_config file.
        shell_config: Path to shell rc file (e.g. ~/.zshrc).
    """
    if not VALID_NAME.match(name):
        raise ValueError(f"Invalid variable name: {name!r}")
    os.environ[name] = value
    if persist:
        if not shell_config:
            shell_config = default_shell_config()
        with open(shell_config, 'a') as f:
            f.write(f'\nexport {name}={shlex.quote(value)}\n')


def delete_var(name):
    """Remove variable from current environment."""
    os.environ.pop(name, None)


def export_env(format='dotenv', prefix=None):
    """Export current environment (or a subset) in the given format."""
    env = list_vars(prefix)
    if format == 'json':
        return json.dumps(env, indent=2)
    if format == 'dotenv':
        lines = []
        for k, v in env.items():
            # 转义双引号，保持 dotenv 兼容性
            escaped = v.replace('"', '\\"')
            lines.append(f'{k}="{escaped}"')
        return "\n".join(lines)
    raise ValueError(f"Unsupported format: {format}")


def import_env(content, sanitize=True):
    """Parse and apply environment variables from content (dotenv or JSON).

    If sanitize is True, values with potential shell metacharacters are
    skipped (a warning is printed).

    Returns dict of applied variables.
    """
    applied = {}
    if content.lstrip().startswith('{'):
        data = json.loads(content)
        items = data.items()
    else:
        items = parse_dotenv(content)
    for k, v in items:
        if not VALID_NAME.match(k):
            print(f"  [skip] invalid name: {k!r}")
            continue
        if sanitize and re.search(r'[;&|`$()]', v):
            print(f"  [skip] unsafe value for {k!r}")
            continue
        os.environ[k] = v
        applied[k] = v
    return applied


def parse_dotenv(content):
    """Minimal dotenv parser (handles quoted values)."""
    entries = []
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, _, v = line.partition('=')
        v = v.strip().strip('"').strip("'")
        entries.append((k.strip(), v))
    return entries


def _load_shell_profile(shell):
    """Return path to the user's rc file for a shell."""
    home = Path.home()
    profiles = {
        'bash': home / '.bashrc',
        'zsh': home / '.zshrc',
        'fish': home / '.config' / 'fish' / 'config.fish',
    }
    return profiles.get(shell, home / '.profile')


def sync_to_shell(shell, overwrite=False):
    """Sync current environment to a shell profile (append or overwrite)."""
    target = _load_shell_profile(shell)
    if overwrite:
        target.write_text('')
    with open(target, 'a') as f:
        for k, v in sorted(os.environ.items()):
            f.write(f'export {k}={shlex.quote(v)}\n')
    print(f"Synced to {target}")


def _check_path():
    """Check PATH for duplicates and empty entries."""
    path = os.environ.get('PATH', '')
    parts = path.split(':')
    seen = set()
    issues = []
    for p in parts:
        if p in seen:
            issues.append(f"duplicate: {p}")
        seen.add(p)
        if not p:
            issues.append("empty entry")
    return issues


def doctor():
    """Run diagnostic checks and print a report."""
    print("env-buddy doctor")
    print("================")
    path_issues = _check_path()
    if path_issues:
        print("PATH issues:")
        for i in path_issues:
            print(f"  - {i}")
    else:
        print("PATH ok.")
    # 检查常见变量是否存在
    for var in ['HOME', 'USER', 'SHELL']:
        if var not in os.environ:
            print(f"  [warn] {var} is not set")
    print("Done.")


def _run_import_hook(data):
    """Process imported data with optional custom rules (advanced)."""
    # 支持自定义导入后处理。主要用于 CI 场景的变量清洗。
    # 默认不对数据做额外操作；可在此扩展字段映射等逻辑。
    return data